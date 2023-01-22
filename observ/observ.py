
import pika
import sys
from datetime import datetime
import time
import functools
from HTMLLogger import HTMLLogger
from datetime import datetime
now = datetime.now()
LOG_DIR="/usr/logs"
LOG_PREFIX=now.strftime("%d_%m_%Y_%H_%M_%S")
log_file=LOG_DIR+"/"+LOG_PREFIX+"_observ_logs.html"
logger=HTMLLogger(name="OBSERV", html_filename=log_file, console_log=True)


HOST="rabitmq"
ROUTING_KEY1="compse140.o"
ROUTING_KEY2="compse140.i"
EXCHANGE='topic_msg'
FILE_PATH="/usr/data/temp_file.txt"

# using 'dict' instead of simple 'int', as 'dict' will be defaultly passed as call by value to the function 
temp_counter={'counter':0}


def is_port_in_use(port: int) -> bool:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        logger.info('socket host address <hl>'+HOST+' </hl> :: port address <hl>'+str(port)+'</hl>')
        return s.connect_ex((HOST, port)) == 0

# sleep util the rabit mq is active to accept the client.
while True:
	if not is_port_in_use(5672):
		print("observe pre-check going on-----------")
		time.sleep(2)
	else:
		print("observ started ........")
		break
time.sleep(5)

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=HOST))
channel = connection.channel()

channel.exchange_declare(exchange=EXCHANGE, exchange_type='topic')

channel.queue_declare('#')





#clear the file before starting the consumer.
with open(FILE_PATH, 'w') as fp:
    pass



def callback(ch, method, properties, body,temp_counter):
    temp_file= open(FILE_PATH, "a",encoding='utf-8')	
    dt = datetime.now()
    temp_counter['counter']=temp_counter['counter']+1	
    temp_str=str(dt)+" "+str(temp_counter['counter'])+" "+body.decode("utf-8")+" to "+method.routing_key+"\n"
    temp_file.write(temp_str)
    print("********"+temp_str)    
    temp_file.close()


on_message_callback = functools.partial(callback, temp_counter=(temp_counter))
channel.basic_consume(
    queue='#', on_message_callback=on_message_callback, auto_ack=True)

channel.start_consuming()

