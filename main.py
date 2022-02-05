import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter
import schedule
import time
import json
import datetime


env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET'],'/slack/events', app)

client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
#loading environment file

BOT_ID = client.api_call("auth.test")['user_id']


def rotate():
    listDict=[]
    doc = open("currentRotations.txt", "r")
    for line in doc:
        listDict.append(json.loads(line))
    #carrega as linhas em formato dicionário json do .txt numa lista de dicionários python
    for rotation in listDict:
        if int(rotation['weekDay']) == int(datetime.datetime.today().weekday()): #se hoje bate com a data, execute a rotação
            print (client.usergroups_users_list(token=os.environ['SLACK_TOKEN'], usergroup=rotation['groupID']))




@app.route('/new-rotation', methods=['POST'])
def new_rotation ():
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
        rotDict["listPerm"] = listInput[4:4+int(listInput [3])]
        rotDict["listRot"] = listInput[4+int(listInput [3]):]
   

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
