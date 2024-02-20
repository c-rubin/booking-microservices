from flask import Flask, request
import requests
from urllib.parse import urlencode
import json
# import pika

app = Flask(__name__)

LINKS = "<br>http://localhost:5000/apartments<br>http://localhost:5000/bookings<br>http://localhost:5000/search<br>"

# RABBITMQ_HOST = 'rabbitmq'
# RABBITMQ_PORT = 5672
# RABBITMQ_QUEUE = 'gateway_events'

# def notify_rabbitmq(message):
#     connection_params = pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT)
#     connection = pika.BlockingConnection(connection_params)
#     channel = connection.channel()
#     channel.queue_declare(queue=RABBITMQ_QUEUE)
#     channel.basic_publish(exchange='', routing_key=RABBITMQ_QUEUE, body=message)
#     connection.close()

@app.route("/<service_name>")
def gateway0(service_name):
    if service_name == "apartments": service_url = "http://apartments:5001/"
    elif service_name == "bookings": service_url = "http://bookings:5002/"
    elif service_name == "search": service_url = "http://search:5003/"
    else: return service_name+" service doesn't exist!<br>"+LINKS

    response = requests.get(service_url)
    return response.text

@app.route('/<service_name>/<command>')
def gateway(service_name, command):
    # print("Command is: "+command+"\nType: "+str(type(command)), flush=True)
    if service_name == "apartments":
        # print("Command is: "+command+"\nType: "+str(type(command)), flush=True)
        service_url = "http://apartments:5001/"
        if not (command==None or command ==""):
            service_url=service_url+command+"?"+urlencode(request.args)
        
    elif service_name == "bookings":
        service_url = "http://bookings:5002/"
        if not (command==None or command ==""):
            service_url=service_url+command+"?"+urlencode(request.args)
        
        # print("Command is: "+command+"\nType: "+type(command))

    elif service_name == "search":
        service_url = "http://search:5003/"
        if not (command==None or command ==""):
            service_url=service_url+command+"?"+urlencode(request.args)
        
        # print("Command is: "+command+"\nType: "+type(command))

    else: return service_name+" service doesn't exist!<br>"+LINKS

    response = requests.get(service_url)
    # if command=="list" or command == "listDetail" or command == "existing" or command == "existingAps" or command == "existingBooks": return response.text
    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        return response.text

@app.route('/')
def hi():
    return "WELCOME!!!!! THIS IS THE GATEWAY!!!<br><br><br>Try the following links:<br>"+LINKS


app.run(host='0.0.0.0', port=5000)
