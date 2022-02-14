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
import pyodbc
import psycopg2

import externalDataSource as eDS 
import modalReturner as mR
import shortcuts as sT

app = Flask(__name__)
#creating flask's 'Application Object' 
#print ("Debug msg: App object created")

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET'],'/slack/events', app)
client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
BOT_ID = client.api_call("auth.test")['user_id']
#loading environment files
#print ("Debug msg: .env loading done")


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


@app.route('/external', methods=['POST'])
def external():
    data = json.loads(request.form.get('payload'))
    return eDS.userGroupList(client, data)
    # When a modal needs to serve data that is not easily available through the .json blocks, it sends a request to this endpoint, expecting said data. 
    # In this case, we are providing the user with a (shortened) list of the worspace's user groups. 
    # If more external data sources are needed in the future, the eDS module can easily fit new funcions.

@app.route('/shortcuts', methods=['POST'])
def shortcuts ():
    data = json.loads(request.form.get('payload'))
    return sT.sortShortcut (client, data)



    

 

if __name__ == "__main__":
    app.run(debug=True)
#automaticaly reruns webserver




