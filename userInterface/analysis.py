import dataCollection
import sendemail
import threading
from threading import Timer
import time
import datetime
import sqlite3
import stateDataStorage

ENABLE_EMAIL = 0 #1 to enable email sending
USER_EMAIL = ['jyl49@cam.ac.uk'] # ['abc@xyz.com','efg@xyz.com']
TRIG1=7
ECHO1=11
TRIG2=15
ECHO2=16
TRIG3=23
ECHO3=24
TRIG4=35
ECHO4=36
DAYSTOEXPIRE = 7
    
def time_in_range(current):
    """Returns whether current is in the range [start, end]"""
    start = datetime.time(8, 0, 0)
    end = datetime.time(17, 0, 0)
    if start <= end:
        return start <= current <= end
    else:
        return start <= current or current <= end
    
def schedule_db_timing():
    x = datetime.datetime.today()
    y = x.replace(day=x.day, hour=9, minute=00, second=0, microsecond=0) + datetime.timedelta(days=1)#daily
    delta_t = y - x
    secs = delta_t.total_seconds()
    return secs

def analyseMeasureAverage(TRIG,ECHO):
    read = 0
    read = dataCollection.measureAverage(TRIG,ECHO)
    if read > 900:
        avg_dist = 'Check connection'
    elif read > 80:
        avg_dist = 0
    elif read > 60:
        avg_dist = 0.25
    elif read > 40:
        avg_dist = 0.5
    else:
        avg_dist = 1
    return avg_dist
 
def analyseMeasure(TRIG,ECHO):
    read = 0
    read = dataCollection.measure(TRIG,ECHO)
    if read > 900:
        distance = 'Check connection'
    elif read > 80:
        distance = 0
    elif read > 60:
        distance = 0.25
    elif read > 40:
        distance = 0.5
    else:
        distance = 1
    return distance

def dataStorage():
    # Create a SQL connection to our SQLite database
    con = sqlite3.connect("stock_db.db")

    cur = con.cursor()

    # Return all results of query
    cur.execute('SELECT itemCode,remainStock,remainStockTrigger,dateExpiry FROM barrels')
    result = cur.fetchall()

    # Be sure to close the connection
    con.close()
    return result

def schedule_db():
#     print('schedule')
    x = datetime.datetime.today()
    time_in = time_in_range (datetime.datetime.now().time())
    read1 = analyseMeasureAverage(TRIG1,ECHO1)
    read2 = analyseMeasureAverage(TRIG2,ECHO2)
    read3 = analyseMeasureAverage(TRIG3,ECHO3)
    read4 = analyseMeasureAverage(TRIG4,ECHO4)
    readings = [read1,read2,read3,read4]
    stateDataStorage.Temp21.set_value(read1)
    stateDataStorage.Temp22.set_value(read2)
    stateDataStorage.Temp23.set_value(read3)
    stateDataStorage.Temp24.set_value(read4)
    sensorlist = []
    triggerlist = []
    expirelist = []
#     print(readings)
    if time_in == True and x.isoweekday() < 6 and ENABLE_EMAIL == 1: 
        for i in range(len(readings)):
            if str(readings[i]) == '0.25' or str(readings[i]) == '0':
                sensorlist.append('Sensor ' + str(i+1))
        result = dataStorage()
#         print(result)
        for i in range(len(result)):
            if result[i][1] == result[i][2]:
                triggerlist.append(result[i][0])
            if (x + datetime.timedelta(days=DAYSTOEXPIRE)).strftime("%Y-%m-%d") == result[i][3]:
#                 print((x + datetime.timedelta(days=DAYSTOEXPIRE)).strftime("%Y-%m-%d"),result[i][3])
                expirelist.append(result[i][0])
        if sensorlist or triggerlist or expirelist:
            sender = sendemail.Emailer()
            sendTo = USER_EMAIL
            emailSubject = "Stock level monitoring status"
            emailContent = "Please ignore if not relevant to you. <br><br> Liquid level is running low: " + str(sensorlist) + "<br> Remaining stock trigger: "+ str(triggerlist) + "<br> Expiring stock: "+ str(expirelist) + "<br><br> To accesss web page: http://(raspberrypi_ip_adress):5000"
            sender.sendmail(sendTo, emailSubject, emailContent)
    secs2 = schedule_db_timing()
#     print('secs2',secs2)
    Timer(secs2,schedule_db).start()#86400seconds=24hours
    
secs1 = schedule_db_timing()
# print('secs1',secs1)
t=Timer(secs1, schedule_db)
t.start()
time.sleep(0.1)

if __name__ == '__main__':
    g=dataCollection.measureAverage(7,11)
    print(g)
    h= analyseMeasureAverage(7,11)
    print(type(h))
