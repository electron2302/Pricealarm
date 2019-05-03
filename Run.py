from lxml import html
import requests
import mysql.connector
import time
import json
from Mail import sendMail

with open('config.json', 'r') as f:
    config = json.load(f)

debug = config['debug']

def main():

    mydb = dbConect()

    cursor = mydb.cursor()

    cursor.execute("SELECT ID,Name,URl,XPath,LastPrice,LowestPrice FROM watcher")

    result = cursor.fetchall()

    mydb.commit()

    for entry in result:
        wID,Name,URL,XPath,LastPrice,LowestPrice = entry[0:5+1]# the +1 is because of the way python handels slice (they are like the walls between the array objects)
          
        strValue = request(URL=URL,XPath=XPath)
        if debug: print("strValue is: ", strValue)
        
        strValue = Formating(value=strValue)
        if debug: print("strValue is: ", strValue)
          
        CurrentPrice = toInt(strValue)
        if debug: print("CurrentPrice is: ", CurrentPrice)

        if(CurrentPrice < LowestPrice):
              print("wooohoo new Low point")
              updateDbPrices(db=mydb,ID=wID,LastPrice=CurrentPrice,LowestPrice=CurrentPrice)
              subject=config['content']['NewLowPonit']['Title'].format(name=Name,last_price=LastPrice,lowest_price=LowestPrice,current_price=CurrentPrice)
              msg=config['content']['NewLowPonit']['msg'].format(name=Name,last_price=LastPrice,lowest_price=LowestPrice,current_price=CurrentPrice)
              sendMail(subject=subject,msg=msg)
        elif(CurrentPrice < LastPrice):
              print("not that exiting but stil Cool")# at least in my opinion maybe only sen msg with an option for that case in future
              updateDbPrices(db=mydb,ID=wID,LastPrice=CurrentPrice,LowestPrice=LowestPrice)
              subject=config['content']['ItGotCheaper']['Title'].format(name=Name,last_price=LastPrice,lowest_price=LowestPrice,current_price=CurrentPrice)
              msg=config['content']['ItGotCheaper']['msg'].format(name=Name,last_price=LastPrice,lowest_price=LowestPrice,current_price=CurrentPrice)
              sendMail(subject=subject,msg=msg)
        elif(CurrentPrice > LastPrice):
              print("the price even rows :( ")
              updateDbPrices(db=mydb,ID=wID,LastPrice=CurrentPrice,LowestPrice=LowestPrice)
        else:
              print("no change in the price")
              if debug:
                    print("CurrentPrice:",CurrentPrice)
                    print("LastPrice:",LastPrice)
                    print("LowestPrice:",LowestPrice)

        time.sleep(config['sleeptime'])#it also sleeps after the last item ! 

    mydb.disconnect()

def dbConect():
      dbconfig=config['db']
      return mysql.connector.connect(
      host=dbconfig['host'],
      user=dbconfig['user'],
      passwd=dbconfig['passwd'],
      port=dbconfig['port'],
      db=dbconfig['db']
      )

def request(URL,XPath):
    print("Requesting :",URL)
    page = requests.get(URL)
      
    if debug: print("prasing it")
    page = html.fromstring(page.content)

    if debug: print("extracting")
    values = page.xpath(XPath+'/text()')

    if debug: print("picking first item")
    value = values[0]
      
    return value

#TODO: That needs work, maybe regex, it is way to statik like this
def Formating(value):
    if debug: print("Formating")
    replacers = [[u'\xa0\u20ac',''],[',','.']]
    for replacer in replacers:
        value = value.replace(replacer[0],replacer[1])
    return value

def toInt(value):# in this funktion are maybe checks or some setings not a bad Idea :) !!!!! 
    if debug: print("converting to flot and then to int (in cents)")
    number = int(float(value)*100)
    if debug: print("value was ", value, "and number is ", number)
    return number

def updateDbPrices(db,ID,LastPrice,LowestPrice):
    if debug: print("updating prices in row ", ID)
    cursor = db.cursor()
    sql = "UPDATE watcher SET LastPrice = %s, LowestPrice = %s WHERE watcher.ID = %s"
    val = (LastPrice, LowestPrice,ID)
    cursor.execute(sql, val)
    db.commit()