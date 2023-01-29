from typing import Union
import pika
from fastapi import FastAPI,HTTPException
from starlette.requests import Request
from starlette.responses import Response
import time
from fastapi.responses import PlainTextResponse
import uvicorn
from HTMLLogger import HTMLLogger
from datetime import datetime
from dotenv import load_dotenv
import os
import sys

#loading environment
load_dotenv()
APP_ENV=os.getenv("ENV")

#logging variables
now = datetime.now()
LOG_DIR=os.getenv("PROD_LOG_DIR") if APP_ENV=="PROD" else os.getenv("TEST_LOG_DIR") 
LOG_PREFIX=now.strftime("%d_%m_%Y_%H_%M_%S")
log_file=LOG_DIR+"/"+LOG_PREFIX+"_httpserver_logs.html"
logger=HTMLLogger(name="HTTP SERVER", html_filename=log_file, console_log=True)

#other variables
HOST="rabitmq"
#HOST="localhost"
EXCHANGE='control_msg'
CONTROL__SIGNAL_ROUTING_KEY="state_control.key"
CONTROL__SIGNAL_ORIG_QUEUE="state_control.orig"
CONTROL__SIGNAL_IMED_QUEUE="state_control.imed"
CONTROL__SIGNAL_OBSERV_QUEUE="state_control.observ"
RUN_LOG_FILE_PATH="/usr/data/run_log_file.txt" if APP_ENV=='PROD' else os.getenv('TEST_RUN_LOG_FILE_PATH')
FILE_PATH="/usr/data/temp_file.txt" if APP_ENV=='PROD' else os.getenv('TEST_FILE_PATH')
ALLOWED_STATES=["INIT", "PAUSED", "RUNNING", "SHUTDOWN"]
PORT=8083

logger.info("app environment type "+APP_ENV+" running on port number "+str(PORT))

#check if the rabbitmq started
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
		print("httpserver started ........")
		break

connection = pika.BlockingConnection(pika.ConnectionParameters(HOST))
channel = connection.channel()

#create the quque and bind it with exchanges for sending the control signals to other containers
channel.exchange_declare(exchange=EXCHANGE, exchange_type='topic')
channel.queue_declare(queue=CONTROL__SIGNAL_OBSERV_QUEUE)
channel.queue_declare(queue=CONTROL__SIGNAL_ORIG_QUEUE)
channel.queue_declare(queue=CONTROL__SIGNAL_IMED_QUEUE)

#create quques for sending control signals.
channel.queue_bind(exchange=EXCHANGE, queue=CONTROL__SIGNAL_OBSERV_QUEUE, routing_key=CONTROL__SIGNAL_ROUTING_KEY)
channel.queue_bind(exchange=EXCHANGE, queue=CONTROL__SIGNAL_ORIG_QUEUE, routing_key=CONTROL__SIGNAL_ROUTING_KEY)
channel.queue_bind(exchange=EXCHANGE, queue=CONTROL__SIGNAL_IMED_QUEUE, routing_key=CONTROL__SIGNAL_ROUTING_KEY)
logger.info("creating cotrol queue and topic with name "+CONTROL__SIGNAL_ROUTING_KEY)

#state is updated to INIT
def init_service():
	logger.info("INIT service is triggered ")
	with open(RUN_LOG_FILE_PATH, 'w') as fp:
		pass
	with open(FILE_PATH, 'w') as fp:
		pass
	persist_service_change("INIT")
	channel.basic_publish(exchange=EXCHANGE,
                        routing_key=CONTROL__SIGNAL_ROUTING_KEY,
                        body="INIT")
	
#state is updated to PAUSED
def pause_service():
	logger.info("PAUSE service is triggered ")
	persist_service_change("PAUSED")
	channel.basic_publish(exchange=EXCHANGE,
                        routing_key=CONTROL__SIGNAL_ROUTING_KEY,
                        body="PAUSED")
 
#state is updated to RUNNING
def run_service():
	logger.info("RUN service is triggered ")
	persist_service_change("RUNNING")
	channel.basic_publish(exchange=EXCHANGE,
                        routing_key=CONTROL__SIGNAL_ROUTING_KEY,
                        body="RUNNING")
	
#state is updated to SHUTDOWN
async def shutdown_service():
	logger.info("SHUTDOWN service is triggered ")
	persist_service_change("SHUTDOWN")
	channel.basic_publish(exchange=EXCHANGE,
                        routing_key=CONTROL__SIGNAL_ROUTING_KEY,
                        body="SHUTDOWN")
	#shutdown the server
	global server
	server.should_exit = True
	server.force_exit = True
	await server.shutdown()
 
 
#persist the state changes. the file will be reset when INIT state is called 
def persist_service_change(state):
	#update the changes in the run_log_file.txt before 
	temp_file= open(RUN_LOG_FILE_PATH, "a", encoding='utf-8')
	dt = datetime.now()
	temp_str=str(dt)+": "+state+"\n"
	temp_file.write(temp_str)
	logger.info("writing to the "+RUN_LOG_FILE_PATH+":: the data is "+temp_str)
	temp_file.close()


#fast api handles request and responses
app = FastAPI()

#init and run the services
init_service()
run_service()

# GET /message endpoint
@app.get("/message", response_class=PlainTextResponse)
def read_message():
	logger.info("expected file path "+FILE_PATH)
	logger.info("GET request received for <hl>/message</hl>")
	f = open(FILE_PATH, "r")
	return str(f.read())

# PUT /state endpoint
@app.put("/state", response_class=PlainTextResponse)
async def update_state(request: Request):
	state=await request.body()
	state=state.decode("utf-8")
	logger.info("PUT request received for <hl>/state</hl> and the input state :"+str(state))
	if not state in ALLOWED_STATES:
		return PlainTextResponse(content="Invalid state. Allowed state "+str(ALLOWED_STATES), status_code=400)

	#check the last status and if it is same as current one don't do anything	
	f= open(RUN_LOG_FILE_PATH, 'r')
	last_line = f.readlines()[-1]
	last_state=str(last_line.split(":")[-1]).strip()

	if state==last_state:
		return "state not updated"
	if state=="INIT":
		init_service()
	elif state=="PAUSED":
		pause_service()
	elif state == "RUNNING":
		run_service()
	elif state == "SHUTDOWN":
		await shutdown_service()
	return "state updated"

#GET /state endpoint
@app.get("/state", response_class=PlainTextResponse)
def get_state():
	logger.info("GET request received for <hl>/state</hl>")
	f= open(RUN_LOG_FILE_PATH, 'r')
	last_line = f.readlines()[-1]
	return str(last_line.split(":")[-1]).strip()

#GET /run-log endpoint
@app.get("/run-log", response_class=PlainTextResponse)
def get_run_log():
	logger.info("GET request received for <hl>/run-log</hl>")
	f = open(RUN_LOG_FILE_PATH, "r")
	return str(f.read())


server=None
if __name__ == "__main__":
    config = uvicorn.Config(app, host="0.0.0.0", port=PORT, log_level="info", loop="asyncio")
    server = uvicorn.Server(config=config)
    server.run()
	
    
