import pika, sys, os
import time
from HTMLLogger import HTMLLogger
from datetime import datetime
now = datetime.now()
LOG_DIR="/usr/logs"
LOG_PREFIX=now.strftime("%d_%m_%Y_%H_%M_%S")
log_file=LOG_DIR+"/"+LOG_PREFIX+"_imed_logs.html"
logger=HTMLLogger(name="IMED", html_filename=log_file, console_log=True)


HOST="rabitmq"
#HOST="localhost"
ROUTING_KEY1="compse140.o"
ROUTING_KEY2="compse140.i"
EXCHANGE='topic_msg'

logger.info("imed pre check ........")
print("imed pre check")
def is_port_in_use(port: int) -> bool:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print('socket host address <h1>'+HOST+' </hl> :: port address <h1>'+str(port)+'</hl>')
        logger.info('socket host address <hl>'+HOST+' </hl> :: port address <hl>'+str(port)+'</hl>')
        return s.connect_ex((HOST, port)) == 0

# sleep util the rabit mq is active to accept the client.
while True:
	if not is_port_in_use(5672):
		time.sleep(2)
	else:
		print("imed started ........")
		break

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=HOST))
    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE, exchange_type='topic')
    channel.queue_declare(queue=ROUTING_KEY1)
    channel.queue_declare(queue=ROUTING_KEY2)
    channel.queue_bind(exchange=EXCHANGE, queue=ROUTING_KEY2, routing_key=ROUTING_KEY2)

    def callback(ch, method, properties, body):
        channel.basic_publish(exchange=EXCHANGE,
                        routing_key=ROUTING_KEY2,
                        body=body)
        time.sleep(1)
        logger.info("******** [x] Received %r" % body)

    channel.basic_consume(queue=ROUTING_KEY1, on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)




