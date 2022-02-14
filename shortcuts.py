import modalListener as mL
import modalReturner as mR
from flask import Response


def sortShortcut(client, data):
    trigger_id = data.get('trigger_id')
    shortcut = data.get("callback_id")
    type = data.get('type')
    #print (data)

    if type == "view_submission":
        #print (data['view'].keys())
        mL.listenModal(data)
    
    elif type == "block_actions":
        print ("Block actions is happening")
        pass

    elif shortcut == 'shortcutNewRotation':
        mR.NewRotation(client, trigger_id)

    else:
        print ("shortcut not yet implemented")
        print (data)

    return Response(), 200