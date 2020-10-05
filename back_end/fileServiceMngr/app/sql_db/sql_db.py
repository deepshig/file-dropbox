from typing import List, Dict
from sql_dbconf import dbCon


def clients_history(clientId)-> List[Dict]:
    connection = dbCon()
    cursor = connection.cursor()
    #cursor.execute("SELECT uid, fileId FROM clients_history")
    query = "SELECT uid, fileId FROM clients_history WHERE uid="+str(clientId)
    cursor.execute(query)
    results = [{"uid":uid,"fileId":fileId} for (uid, fileId) in cursor]
    cursor.close()
    connection.close()
    return results


def update_client_history(clientId,req_data):
    connection = dbCon()
    cursor = connection.cursor()
    query = ("INSERT INTO clients_history (uid,userName,fileId,fileName,activity) VALUES (%s,%s,%s,%s,%s)")
    val   =  (req_data['uid'], req_data['userName'],req_data['fileId'],req_data['fileName'],req_data['activity'])
    cursor.execute(query,val)
    connection.commit()
    if (cursor.rowcount == 1):
       cursor.close()
       return True
    else:
       cursor.close()
       return False



