from flask import Flask, request
import threading
import requests
import pika
import sqlite3
import json
from datetime import datetime

app = Flask(__name__)

apartments = []
bookings = []

RABBITMQ_HOST = 'rabbitmq'
RABBITMQ_PORT = 5672
RABBITMQ_QUEUE = 'search'
DATE_FORMAT = "%Y%m%d"

##CHECK IF APARTMENT IS AVAILABLE (duhet me marr krejt booking nga databaza)
# def getAvailableAps(fromDate, toDate):
#     aps = []
#     global bookings
#     for x in bookings:
#         if fromDate>datetime.strptime(x["to"],DATE_FORMAT): aps.append(x["apartment_id"])
#         elif toDate<datetime.strptime(x["from"],DATE_FORMAT): aps.append(x["apartment_id"])

#     return aps

def initDb():
    conn = sqlite3.connect('./search.db')
    c = conn.cursor()
    #What should be stored in the search DB??? maybe just book id, apartment id, and dates???
    c.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id TEXT PRIMARY KEY,
                apartment_id TEXT NOT NULL,
                fromDate TEXT NOT NULL,
                toDate TEXT NOT NULL
            )
        """) 
    conn.commit()
    conn.close()

def listenAps():
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()

    channel.queue_declare(queue=RABBITMQ_QUEUE)

    def callback(ch, method, properties, body):

        lista = body.decode().split(";")
        if lista[0]=="Added":
            apartments.append(lista[1])
        elif lista[0]=="Removed":
            apartments.remove(lista[1])

        # print(f" [x] Received \"{body.decode()}\"")
        ch.basic_ack(delivery_tag = method.delivery_tag)

    channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=callback)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

# def listenBooks():
#     print("CALLED");
#     connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
#     channel = connection.channel()

#     channel.queue_declare(queue="books_events")

#     def callback(ch, method, properties, body):

#         lista = body.decode().split(";")
#         if lista[0]=="Added":
#             ap = lista[1].replace("\'","\"") #some dumb fkin thing which caused me 2 days problem
#             bookings.append(json.loads(ap))#json.loads(lista[1]))
#         elif lista[0]=="Removed":
#             bookings.append("LALE")
#             # target = "raku"
#             # for i in range(len(bookings)):
#             #     if bookings[i]["id"]==lista[2]:
#             #         target = i
#             # # bookings.pop(target)
#             # bookings.append(lista[1])

#         # print(f" [x] Received \"{body.decode()}\"")
#         ch.basic_ack(delivery_tag = method.delivery_tag)

#     channel.basic_consume(queue="books_events", on_message_callback=callback)

#     print(' [*] Waiting for messages. To exit press CTRL+C')
#     channel.start_consuming()

#     # def listen():
#     # connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
#     # channel = connection.channel()

#     # channel.exchange_declare(exchange='logs', exchange_type='fanout')
#     # channel.queue_declare(queue=RABBITMQ_QUEUE)
#     # channel.queue_bind(exchange='logs', queue=RABBITMQ_QUEUE)

#     # def callback(ch, method, properties, body):

#     #     lista = body.decode().split(";")
#     #     if lista[0]=="Added":
#     #         apartments.append(lista[1])
#     #     elif lista[0]=="Removed":
#     #         apartments.remove(lista[1])

#     #     # print(f" [x] Received \"{body.decode()}\"")
#     #     ch.basic_ack(delivery_tag = method.delivery_tag)

#     # channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=callback)

#     # print(' [*] Waiting for messages. To exit press CTRL+C')
#     # channel.start_consuming()

@app.route('/init')
def inittializeEverything():
    try:
        initializeExistingApartments()
        # initializeExistingBookings()
        return "Successfully initialized everything"
    except Exception as e:
        return str(e)

def initializeExistingApartments():
    global apartments
    # try:
    response = requests.get("http://apartments:5001/list")

    if response.status_code == 200:
            apartments = response.json()

    return apartments
    # except Exception as e:
    #     return str(e)
    
# def initializeExistingBookings():
#     global bookings
#     # try:
#     response = requests.get("http://bookings-service:5001/listDetail")

#     if response.status_code == 200:
#             bookings = response.json()

#         # return bookings
#     # except Exception as e:
#     #     return str(e)


@app.route('/')
def hello():
    try:
        print(type(apartments))
        return "SEARCH!!!"
    except Exception as e:
         return str(e)
    
@app.route('/existingAps')
def viewExistinApartments():
    try:
        return apartments
    except Exception as e:
        return str(e)
    
# @app.route('/existingBooks')
# def viewExistinBooks():
#     try:
#         print("EXISTING BOOKS EXECUTED")
#         return bookings
#     except Exception as e:
#         return str(e)

# @app.route('/list')
# def list_apartments():
#     try:
#         conn = sqlite3.connect('search.db')
#         c = conn.cursor()
#         c.execute('SELECT * FROM bookings')
#         bookings = c.fetchall()
#         conn.close()

#         # Convert the result to a list of dictionaries for better JSON serialization
#         result = [row[0] for row in bookings]

#         return result
#     except Exception as e:
#         return str(e)

# @app.route('/listDetail')
# def list_apartmentsDetail():
#     try:
#         conn = sqlite3.connect('bookings.db')
#         c = conn.cursor()
#         c.execute('SELECT * FROM bookings')
#         bookings = c.fetchall()
#         conn.close()

#         # Convert the result to a list of dictionaries for better JSON serialization
#         result = [{"id":row[0], "apartment_id":row[1], "from":row[2], "to":row[3], "who":row[4]} for row in bookings]

#         return result
#     except Exception as e:
#         return str(e)
    
# @app.route('/search')
# def searchAps():
#     try:
#         fromDate = datetime.strptime(request.args.get("from"),DATE_FORMAT)
#         toDate = datetime.strptime(request.args.get("to"),DATE_FORMAT)
#         return getAvailableAps(fromDate , toDate)
#     except Exception as e:
#         return str(e)

# threading.Thread(target=listenBooks, daemon=True).start()
threading.Thread(target=listenAps, daemon=True).start()


initDb()
inittializeEverything()
app.run(host='0.0.0.0', port=5003)


# localhost:5001/add?apartment_id=d31c8d5a-251d-4a88-bd08-789bf862fe74&from=20201212&to=20211212&who=someone
# localhost:5001/add?apartment_id=&from=20201212&to=20211212&who=someone