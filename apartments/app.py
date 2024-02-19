from flask import Flask, request
import sqlite3
import uuid
import pika

app = Flask(__name__)

RABBITMQ_HOST = 'rabbitmq'
RABBITMQ_PORT = 5672
RABBITMQ_EXCHANGE = "apartment_events"
RABBITMQ_QUEUE2 = 'search'
RABBITMQ_QUEUE1 = 'books'

def notify_rabbitmq(message):
    connection_params = pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT)
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()

    #fanout -> 1 to Many relation
    channel.exchange_declare(exchange=RABBITMQ_EXCHANGE, exchange_type='fanout')
    channel.queue_declare(queue=RABBITMQ_QUEUE1)
    channel.queue_bind(exchange=RABBITMQ_EXCHANGE, queue=RABBITMQ_QUEUE1)
    channel.queue_declare(queue=RABBITMQ_QUEUE2)
    channel.queue_bind(exchange=RABBITMQ_EXCHANGE, queue=RABBITMQ_QUEUE2)

    channel.basic_publish(exchange=RABBITMQ_EXCHANGE, routing_key="", body=message)
    connection.close()

# SQLite database initialization
def initDb():
    conn = sqlite3.connect('./apartments.db')
    c = conn.cursor()
    c.execute("""
            CREATE TABLE IF NOT EXISTS apartments (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                address TEXT NOT NULL,
                noiselevel REAL NOT NULL,
                floor INTEGER NOT NULL
            )
        """) 
    conn.commit()
    conn.close()

@app.route('/')
def hello():
    return "This is the apartment microservice!"


# add?name=name1&address=address1&noiselevel=1&floor=1
# add?name=name2&address=address2&noiselevel=2&floor=2
@app.route('/add')
def add_apartment():
    try:
        appId = str(uuid.uuid4())
        data = request.args
        name = data.get('name')
        address = data.get('address')
        noise_level = float(data.get('noiselevel'))
        floor = int(data.get('floor'))

        conn = sqlite3.connect('apartments.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO apartments (id, name, address, noiselevel, floor)
            VALUES (?, ?, ?, ?, ?)
        ''', (appId, name, address, noise_level, floor))
        conn.commit()
        conn.close()

        notify_rabbitmq(f"Added;{appId}")

        return f"Apartment {appId} added successfully"
    except Exception as e:
        return str(e)
    
@app.route('/remove')
def remove_apartment():
    try:
        apartment_id = request.args.get('id')

        conn = sqlite3.connect('apartments.db')
        c = conn.cursor()
        c.execute('DELETE FROM apartments WHERE id = ?', (apartment_id,))
        conn.commit()
        conn.close()

        notify_rabbitmq(f"Removed;{apartment_id}")

        return f"Apartment {apartment_id} removed successfully"
    except Exception as e:
        return str(e)
    
@app.route('/list')
def list_apartments():
    try:
        conn = sqlite3.connect('apartments.db')
        c = conn.cursor()
        c.execute('SELECT * FROM apartments')
        apartments = c.fetchall()
        conn.close()

        # Convert the result to a list of dictionaries for better JSON serialization
        result = [row[0] for row in apartments]
        # How it was before
        # result = [{'id': row[0], 'name': row[1], 'address': row[2], 'noiselevel': row[3], 'floor': row[4]} for row in apartments]

        return result
    except Exception as e:
        return str(e)

# http://localhost:5001/

initDb()
app.run(host='0.0.0.0',port=5001)