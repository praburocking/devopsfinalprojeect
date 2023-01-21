from typing import Union
import pika
from fastapi import FastAPI
import time
from fastapi.responses import PlainTextResponse
import uvicorn
from HTMLLogger import HTMLLogger
from datetime import datetime
from dotenv import load_dotenv
import os

now = datetime.now()
load_dotenv()
APP_ENV=os.getenv("ENV")

LOG_DIR=os.getenv("PROD_LOG_DIR") if APP_ENV=="PROD" else os.getenv("TEST_LOG_DIR") 
LOG_PREFIX=now.strftime("%d_%m_%Y_%H_%M_%S")
PORT=8083

log_file=LOG_DIR+"/"+LOG_PREFIX+"_httpserver_logs.html"
logger=HTMLLogger(name="HTTP SERVER", html_filename=log_file, console_log=True)


HOST="rabitmq"
EXCHANGE='topic_msg'
CONTROL__SIGNAL_ROUTING_KEY="state_control.i"


def is_port_in_use(port: int) -> bool:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print('socket host address <h1>'+HOST+'</h1> :: port address <h1>'+str(port)+'</h1>')
        logger.info('socket host address <hl>'+HOST+' </hl> :: port address <hl>'+str(port)+'</hl>')
        return s.connect_ex((HOST, port)) == 0

# sleep util the rabit mq is active to accept the client.
while True and APP_ENV=="PROD":
	if not is_port_in_use(5672):
		time.sleep(2)
	else:
		print("orig started ........")
		break

if APP_ENV=="PROD":
	connection = pika.BlockingConnection(pika.ConnectionParameters(HOST))
	channel = connection.channel()

	#create the quque and bind it with exchanges
	channel.exchange_declare(exchange=EXCHANGE, exchange_type='topic')
	channel.queue_declare(queue=CONTROL__SIGNAL_ROUTING_KEY)
	channel.queue_bind(exchange=EXCHANGE, queue=CONTROL__SIGNAL_ROUTING_KEY, routing_key=CONTROL__SIGNAL_ROUTING_KEY)



app = FastAPI()
FILE_PATH="/usr/data/temp_file.txt"

@app.get("/message", response_class=PlainTextResponse)
def read_root():
	f = open(FILE_PATH, "r")
	return str(f.read())

@app.put("/state", response_class=PlainTextResponse)
def update_state():
	return None

@app.get("/state", response_class=PlainTextResponse)
def get_state():
	return None

@app.get("/run-log", response_class=PlainTextResponse)
def get_run_log():
	return None



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
    
