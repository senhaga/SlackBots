from flask import Response
import createRotation as cR

def listenModal(data):
    #print('\n' + "Beginning modalListener()")
    #print (data)
    #print ("Data printed^\n")
    
    if data['view']['title']['text'] == 'Criar rotação de oncall':
        return cR.createRotation(data) 
    else:
        return Response(), 400