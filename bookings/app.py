from flask import Flask, request
import threading
import requests
import pika
import sqlite3
import uuid

app = Flask(__name__)

apartments = []

RABBITMQ_HOST = 'rabbitmq'
RABBITMQ_PORT = 5672
BOOKINGS_EXCHANGE = "booking_events"
# APARTMENTS_EXCHANGE = "apartment_events"
APARTMENTS_QUEUE = 'books'
SEARCH_QUEUE = 'bookings_search'

def notAvailable(apartment):
    if apartment not in apartments:
        return True
    return False

def initDb():
    conn = sqlite3.connect('./bookings.db')
    c = conn.cursor()
    c.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id TEXT PRIMARY KEY,
                apartment_id TEXT NOT NULL,
                fromDate TEXT NOT NULL,
                toDate TEXT NOT NULL,
                who TEXT NOT NULL
            )
        """) 
    conn.commit()
    conn.close()

def notify_rabbitmq(message):
    connection_params = pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT)
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()

    #fanout -> 1 to Many relation
    channel.exchange_declare(exchange=BOOKINGS_EXCHANGE, exchange_type='fanout')
    channel.queue_declare(queue=SEARCH_QUEUE)
    channel.queue_bind(exchange="booking_events", queue=SEARCH_QUEUE)

    channel.basic_publish(exchange='booking_events', routing_key="", body=message)
    # channel.basic_publish(exchange='', routing_key=RABBITMQ_QUEUE2, body=message)
    connection.close()

def listen():
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()

    channel.queue_declare(queue=APARTMENTS_QUEUE)

    def callback(ch, method, properties, body):

        lista = body.decode().split(";")
        if lista[0]=="Added":
            apartments.append(lista[1])
        elif lista[0]=="Removed":
            if lista[1] in apartments: apartments.remove(lista[1])

        # print(f" [x] Received \"{body.decode()}\"")
        ch.basic_ack(delivery_tag = method.delivery_tag)

    channel.basic_consume(queue=APARTMENTS_QUEUE, on_message_callback=callback)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

@app.route('/init')
def initializeExistingApartments():
    global apartments
    try:
        response = requests.get("http://apartments:5001/list")

        if response.status_code == 200:
                apartments = response.json()

        return apartments
    except Exception as e:
        return str(e)


@app.route('/')
def hello():
    try:
        print(type(apartments))
        return "This is bookings microservice!"
    except Exception as e:
         return str(e)
    
@app.route('/existing')
def viewExistinApartments():
    try:
        return apartments
    except Exception as e:
        return str(e)

@app.route('/add')
def addBook():
    try:
        bookId = str(uuid.uuid4())
        data = request.args
        apId = data.get('apartment_id')

        if notAvailable(apId): return "Apartment not available"

        fromDate = data.get('from')
        toDate = data.get('to')
        who = data.get('who')

        conn = sqlite3.connect('bookings.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO bookings (id, apartment_id, fromDate, toDate, who)
            VALUES (?, ?, ?, ?, ?)
        ''', (bookId, apId, fromDate, toDate, who))
        conn.commit()
        conn.close()

        #what we need for the search DB
        booking = {"id":bookId, "apartment_id":apId, "from":fromDate, "to":toDate}
        notify_rabbitmq(f"Added;{booking}")

        return f"Booking {bookId} added successfully"
    except Exception as e:
        return str(e)

# @app.route('/change')
# def changeBook():
#     try:
#         data = request.args
#         bookId = data.get('id')
#         fromDate = data.get('from')
#         toDate = data.get('to')
#         # who = data.get('who')

#         conn = sqlite3.connect('bookings.db')
#         c = conn.cursor()
#         c.execute('''
#             UPDATE bookings
#             SET fromDate=?, toDate=?
#             WHERE id=?
#         ''', (fromDate, toDate, bookId))
#         conn.commit()
#         conn.close()

#         notify_rabbitmq(f"Added;{bookId}")

#         return f"Booking {bookId} changed successfully"
#     except Exception as e:
#         return str(e)


@app.route("/cancel")
def remove_apartment():
    try:
        bookId= request.args.get('id')

        conn = sqlite3.connect('bookings.db')
        c = conn.cursor()
        c.execute('DELETE FROM bookings WHERE id = ?', (bookId,))
        conn.commit()
        conn.close()

        notify_rabbitmq(f"Removed;{bookId}")

        return f"Booking {bookId} removed successfully"
    except Exception as e:
        return str(e)

@app.route('/list')
def list_apartments():
    try:
        conn = sqlite3.connect('bookings.db')
        c = conn.cursor()
        c.execute('SELECT * FROM bookings')
        bookings = c.fetchall()
        conn.close()

        # Convert the result to a list of dictionaries for better JSON serialization
        result = [row[0] for row in bookings]

        return result
    except Exception as e:
        return str(e)

@app.route('/listDetail')
def list_apartmentsDetail():
    try:
        conn = sqlite3.connect('bookings.db')
        c = conn.cursor()
        c.execute('SELECT * FROM bookings')
        bookings = c.fetchall()
        conn.close()

        # Convert the result to a list of dictionaries for better JSON serialization
        result = [{"id":row[0], "apartment_id":row[1], "from":row[2], "to":row[3], "who":row[4]} for row in bookings]

        return result
    except Exception as e:
        return str(e)

threading.Thread(target=listen, daemon=True).start()

initDb()
initializeExistingApartments()
app.run(host='0.0.0.0', port=5002)


# localhost:5001/add?apartment_id=d31c8d5a-251d-4a88-bd08-789bf862fe74&from=20201212&to=20211212&who=someone
# localhost:5001/add?apartment_id=&from=20201212&to=20211212&who=someone