import slack
import os
from pathlib import Path
from flask import Flask, request, Response, make_response
from slackeventsapi import SlackEventAdapter
from dotenv import load_dotenv
import schedule
import time
import json
import datetime
from views import views


env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
app.register_blueprint(views, url_prefix="/")


slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET'],'/slack/events', app)

client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
#loading environment files

BOT_ID = client.api_call("auth.test")['user_id']



@app.route('/external', methods=['POST'])
def external():
    usrGroups = client.usergroups_list(token=os.environ['SLACK_TOKEN']).data['usergroups']
    data = request.form['payload']
    jsonV = json.loads(data)
    substring = jsonV['value']
    #print (usrGroups)
    normList = []
    for ug in usrGroups:
        if substring in ug['handle']:
            normList.append(dict(text=dict(type="plain_text",text=ug['handle']),value=ug['id']))
    
    response = make_response(json.dumps(dict(options = normList)), 200)
    response.headers['Content-Type']="application/json"

    return response
#Eu não sei como essa desgraça está funcionando. Mas está.



def rotate():
    print ("Iniciando rotate()")

    listDict=[]
    doc = open("currentRotations.txt", "r")
    for line in doc:
        listDict.append(json.loads(line))
    #carrega as linhas em formato dicionário json do .txt numa lista de dicionários python
    doc.close()


    for rotation in listDict:
        if int(rotation['weekDay']) == int(datetime.datetime.today().weekday()): 
        #se hoje bate com a data, execute a rotação

            print ("executando rotação HOJE")

            currentUsers = client.usergroups_users_list(token=os.environ['SLACK_TOKEN'], usergroup=rotation['groupID'])["users"]
            print (f"Usuários atuais são {currentUsers}")
            newUsers = rotation["listPerm"]
            print (f"LIsta de perm é {newUsers}")
        #confere os atuais membros

            rotList = rotation["listRot"]
            print (f"Usuários em rotação são {rotList}")

            rotList.append(rotList[0])
            rotList.pop(0)
            rotation["listRot"] = rotList
        #joga o primeiro nome da lista para o final
            print (f"A nova ordem será {rotList}")

            newUsers.append(rotList[0])
        #inclui o membro fresco na rotação

            tNewUsers = tuple(newUsers)
            strNewUsers = ",".join(tNewUsers)
            for user in newUsers:
                strNewUsers+user
        #transforma a lista em string para passar como parâmetro

            print(client.usergroups_users_update(token=os.environ['SLACK_TOKEN'], usergroup=rotation['groupID'], users=strNewUsers))
        #atualiza os usuários do grupo


    doc = open ("currentRotations.txt", "w")
    for rotation in listDict:
        doc.write(str(json.dumps(rotation)))
    doc.close()
        #updates .txt

    print("Sucesso")
    return Response(), 200

def returningNewRotationModel(tg_id):
    print('\n' + "Beginning stNewRot()")
    doc = open('stNewRot.json', 'r')
    modal = json.loads(doc.read())
    doc.close()
    client.views_open(token=os.environ['SLACK_TOKEN'], trigger_id=tg_id, view=modal)
    return Response(), 200


def modalListener(data):
    #print('\n' + "Beginning modalListener()")
    #print (data)
    #print ("Data printed^\n")
    if data['view']['title']['text'] == 'Criar rotação de oncall':
    
        state = data['view']['state']['values']
        #print (state)
        #print ("state printed^\n")

        stValues=[]
        for value in state.values():
            stValues.append(value)
        #stValues = state.values()
        #print (stValues)
        #print ("stValues printes^\n")
        #for value in stValues:
        #    print (value)


        dictForm = dict(
        usergroup = stValues[0]['text1234']['selected_option']['value'],
        messageChannelID = stValues[1]['channel_select-action']['selected_channel'],
        periodicy = stValues[2]['static_select-action']['selected_option']['value'],
        weekDay = stValues[3]['static_select-action']['selected_option']['value'],        
        messageTime = stValues[4]['timepicker-action']['selected_time'],
        listPerm_ID = stValues[5]['multi_users_select-action']['selected_users'],
        listRot_ID = stValues[6]['multi_users_select-action']['selected_users']
        )

        #print ('\n' + dictForm)

        doc = open("currentRotations.txt", "a")
        doc.write(str(dictForm))
        doc.close()



    else:
        return Response(), 400   

    

@app.route('/shortcuts', methods=['POST'])
def shortcuts ():
    data = json.loads(request.form.get('payload'))
    #print (data)

    trigger_id = data.get('trigger_id')
    shortcut = data.get("callback_id")
    type = data.get('type')
    #print (data)





    if type == "view_submission":
        #print (data['view'].keys())
        modalListener(data)
    
    elif type == "block_actions":
        print ("Block actions is happening")
        pass

    elif shortcut == 'shortcutNewRotation':
        returningNewRotationModel(trigger_id)

    else:
        print ("shortcut not yet implemented")
        print (data)

    return Response(), 200


@app.route('/new-rotation', methods=['POST'])
def new_rotation ():
    print ("Iniciando new_rotation")
    data = request.form
    channel_id = data.get('channel_id')
    channel_name = data.get('channel_name')

    rawInput = data.get('text')
    listInput = rawInput.lower().split()

    toUpdate = listInput[0].strip('*')
    toUpdateID = ''
    usrGroups = client.usergroups_list(token=os.environ['SLACK_TOKEN']).data['usergroups']
    for group in usrGroups:
        if toUpdate==group['handle']:
            toUpdateID = group['id']
    #getting the group's ID 



    if toUpdateID!='':
        rotDict={}
        rotDict["groupID"] = toUpdateID
        rotDict["groupHandle"] = listInput[0]
        rotDict["weekDay"]=listInput[1] #monday=0, sunday=6   
        rotDict["cicleDuration"] = listInput[2]

        #print(client.users_list(token=os.environ['SLACK_TOKEN']))

        listPermName = listInput[4:4+int(listInput [3])]
        listPermID = []
        for name in listPermName: #para cada nome na lista de membros permanentes,
            for member in client.users_list()['members']: #compare com os nomes de todos os membros do workspace
                #print(member["profile"]["display_name"])
                if name == member["profile"]["display_name"] and member["deleted"]==False: #se o nome bater com a handle de usuário não deletado, pegue o ID
                    #print (member["profile"]["display_name"])
                    listPermID.append(member["id"])
        rotDict["listPerm"] = listPermID

        listRotName = listInput[4+int(listInput [3]):]
        listRotID =[]
        for name in listRotName: #para cada nome na lista de membros rotativos,
            for member in client.users_list()['members']: #compare com os nomes de todos os membros do workspace
                if name == member["profile"]["display_name"] and member["deleted"]==False: #se o nome bater com a handle de usuário não deletado, pegue o ID
                    #print(member["profile"]["display_name"])
                    listRotID.append(member["id"])
        rotDict["listRot"] = listRotID
   

    jsonDict = json.dumps(rotDict) 

    doc = open("currentRotations.txt", "a")
    doc.write(str(jsonDict))
    doc.close()

    rotate()
  
    #/new-rotation legal-eng_lawsuits-oncall
    return Response(), 200

@app.route('/new-oncall', methods=['POST'])
def new_oncall ():
    data = request.form
    channel_id = data.get('channel_id')
    channel_name = data.get('channel_name')

    rawInput = data.get('text')
    listInput = rawInput.split()
    newOncallName = listInput[0]
    listInput.pop(0)

    print (data)

    client.usergroups_create(name=newOncallName, token=os.environ['SLACK_TOKEN'])

    return Response(), 200
  



if __name__ == "__main__":
    app.run(debug=True)
#automaticaly reruns webserver





#schedule.every().day.at("01:00").do(job,'It is 01:00')
