import pika
import time
from HTMLLogger import HTMLLogger
from datetime import datetime
import sys
now = datetime.now()
LOG_DIR="/usr/logs"
LOG_PREFIX=now.strftime("%d_%m_%Y_%H_%M_%S")
log_file=LOG_DIR+"/"+LOG_PREFIX+"_orig_logs.html"
logger=HTMLLogger(name="ORIG", html_filename=log_file, console_log=True)

HOST="rabitmq"
ROUTING_KEY1="compse140.o"
EXCHANGE='topic_msg'
ROUTING_KEY2="compse140.i"

#control queue variables
CONTROL_SIGNAL_EXCHANGE='control_msg'
CONTROL__SIGNAL_ROUTING_KEY="state_control.key"
CONTROL__SIGNAL_ORIG_QUEUE="state_control.orig"
CONTROL__SIGNAL_IMED_QUEUE="state_control.imed"
CONTROL__SIGNAL_OBSERV_QUEUE="state_control.observ"
RUN_LOG_FILE_PATH="/usr/data/run_log_file.txt"

def is_port_in_use(port: int) -> bool:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print('socket host address <h1>'+HOST+'</h1> :: port address <h1>'+str(port)+'</h1>')
        logger.info('socket host address <hl>'+HOST+' </hl> :: port address <hl>'+str(port)+'</hl>')
        return s.connect_ex((HOST, port)) == 0

# sleep util the rabit mq is active to accept the client.
while True:
	if not is_port_in_use(5672):
		time.sleep(2)
	else:
		print("orig started ........")
		break

connection = pika.BlockingConnection(pika.ConnectionParameters(HOST))
channel = connection.channel()

#create the quque and bind it with exchanges
channel.exchange_declare(exchange=EXCHANGE, exchange_type='topic')
channel.queue_declare(queue=ROUTING_KEY1)
channel.queue_bind(exchange=EXCHANGE, queue=ROUTING_KEY1, routing_key=ROUTING_KEY1)
channel.queue_declare(queue='#')
channel.queue_bind(exchange=EXCHANGE, queue='#', routing_key='#')

channel.exchange_declare(exchange=CONTROL_SIGNAL_EXCHANGE, exchange_type='topic')
channel.queue_declare(queue=CONTROL__SIGNAL_OBSERV_QUEUE)
channel.queue_declare(queue=CONTROL__SIGNAL_ORIG_QUEUE)
channel.queue_declare(queue=CONTROL__SIGNAL_IMED_QUEUE)
channel.queue_bind(exchange=EXCHANGE, queue=CONTROL__SIGNAL_OBSERV_QUEUE, routing_key=CONTROL__SIGNAL_ROUTING_KEY)
channel.queue_bind(exchange=EXCHANGE, queue=CONTROL__SIGNAL_ORIG_QUEUE, routing_key=CONTROL__SIGNAL_ROUTING_KEY)
channel.queue_bind(exchange=EXCHANGE, queue=CONTROL__SIGNAL_IMED_QUEUE, routing_key=CONTROL__SIGNAL_ROUTING_KEY)

N=3

def read_control_file():
    f= open(RUN_LOG_FILE_PATH, 'r')
    last_line = f.readlines()[-1]
    return str(last_line.split(":")[-1]).strip()

# Callback function for receving the control signals. i.e State changes.
def control_callback(ch, method, properties, body):
    logger.info("control signal received "+body.decode('utf-8'))
    
    #if control signal is received as RUNNING then start  publishing the message.
    if body.decode('utf-8')=="RUNNING":
        for i in range(N):
            #reading the last updated states from RUN_LOG_FILE and if it is PAUESED then the publishing loop will be breaked.
            last_updated_state=read_control_file()
            #last_updated_state="RUNNING"
            if last_updated_state=="PAUSED":
                logger.warning("control signal 'PAUSED' read from the  "+RUN_LOG_FILE_PATH+" file so breaking publishing loop")
                break
            channel.basic_publish(exchange=EXCHANGE,
                            routing_key=ROUTING_KEY1,
                            body='MSG_'+str(i+1))
            print(" [x] Sent 'Hello World!---'")
            time.sleep(3)
        logger.info("message published %r" % body)
    
    #if control signal receives SHUTDOWN state, it will close the connection and exit the python, thereby closing the docker container    
    elif body.decode('utf-8')=="SHUTDOWN":
         channel.close()
         sys.exit()

#consuming the control signal sent from httpserver
channel.basic_consume(queue=CONTROL__SIGNAL_ORIG_QUEUE, on_message_callback=control_callback, auto_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()

