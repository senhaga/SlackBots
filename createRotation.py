from datetime import datetime
import pyodbc
from dotenv import load_dotenv
import os
import psycopg2



def createRotation(data):
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

    creator_id = str(data['user']['id']),
    creation_time = str(datetime.now()),
    group_id_to_rotate = str(stValues[0]['text1234']['selected_option']['value']),
    channel_id_to_message = str(stValues[1]['channel_select-action']['selected_channel']),
    periodicy = str(stValues[2]['static_select-action']['selected_option']['value']),
    weekday = str(stValues[3]['static_select-action']['selected_option']['value']),        
    rotation_time = str(stValues[4]['timepicker-action']['selected_time']),
    permanent_users_ID = str(stValues[5]['multi_users_select-action']['selected_users']),
    rotating_users_ID = str(stValues[6]['multi_users_select-action']['selected_users'])
    )

    DATABASE_URL = os.environ['DB_URL']
    connectionDB = psycopg2.connect(DATABASE_URL, sslmode='require', user=os.environ['DB_USER'], password=os.environ['DB_PASSWORD'])
    #print ("DB Connection succeded.")

    cursor = connectionDB.cursor()

    #print (tuple(dictForm.values()))

    creator_id = str(data['user']['id']),
    cursor.execute("INSERT INTO active_rotations (creator_id, creation_time, group_id_to_rotate, channel_id_to_message, periodicy, weekday, rotation_time, permanent_users_ID, rotating_users_ID) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)", tuple(dictForm.values()))
    
    #cursor.execute("SELECT creator_id, creation_time, group_id_to_rotate, channel_id_to_message, periodicy, weekday, rotation_time, permanent_users_ID, rotating_users_ID from active_rotations")
    #rows = cursor.fetchall()
    #print ("trying to fetch")
    #for r in rows:
    #    print (f"creator_id={r[0]}, creation_time={r[1]}, group_id_to_rotate={r[2]}, channel_id_to_message={r[3]}], periodicy={r[4]}, weekday={r[5]} rotation_time={r[6]}, permanent_users_ID={r[7]}, rotating_users_ID={r[8]}")

    connectionDB.commit()


    cursor.close()
    connectionDB.close()
    print ("End of test")


    #doc = open("currentRotations.txt", "a")
    #doc.write(str(dictForm))
    #doc.close()    
