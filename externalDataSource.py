import os
import dotenv
import json
from flask import Flask, request, Response, make_response

def userGroupList(client, data):
    print ('Debug msg: external() has begun')
    usrGroups = client.usergroups_list(token=os.environ['SLACK_TOKEN']).data['usergroups']
    substring = data['value']
    normList = []
    for ug in usrGroups:
        if substring in ug['handle']:
            normList.append(dict(text=dict(type="plain_text",text=ug['handle']),value=ug['id']))
    response = make_response(json.dumps(dict(options = normList)), 200)
    response.headers['Content-Type']="application/json"
    return response