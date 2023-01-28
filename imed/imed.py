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

#control queue variables
CONTROL_SIGNAL_EXCHANGE='control_msg'
CONTROL__SIGNAL_ROUTING_KEY="state_control.key"
CONTROL__SIGNAL_ORIG_QUEUE="state_control.orig"
CONTROL__SIGNAL_IMED_QUEUE="state_control.imed"
CONTROL__SIGNAL_OBSERV_QUEUE="state_control.observ"

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


    channel.exchange_declare(exchange=CONTROL_SIGNAL_EXCHANGE, exchange_type='topic')
    channel.queue_declare(queue=CONTROL__SIGNAL_OBSERV_QUEUE)
    channel.queue_declare(queue=CONTROL__SIGNAL_ORIG_QUEUE)
    channel.queue_declare(queue=CONTROL__SIGNAL_IMED_QUEUE)
    channel.queue_bind(exchange=EXCHANGE, queue=CONTROL__SIGNAL_OBSERV_QUEUE, routing_key=CONTROL__SIGNAL_ROUTING_KEY)
    channel.queue_bind(exchange=EXCHANGE, queue=CONTROL__SIGNAL_ORIG_QUEUE, routing_key=CONTROL__SIGNAL_ROUTING_KEY)
    channel.queue_bind(exchange=EXCHANGE, queue=CONTROL__SIGNAL_IMED_QUEUE, routing_key=CONTROL__SIGNAL_ROUTING_KEY)

    def callback(ch, method, properties, body):
        channel.basic_publish(exchange=EXCHANGE,
                        routing_key=ROUTING_KEY2,
                        body=body)
        time.sleep(1)
        logger.info("******** [x] Received %r" % body)

    channel.basic_consume(queue=ROUTING_KEY1, on_message_callback=callback, auto_ack=True)


    def control_callback(ch, method, properties, body):
        logger.info("control signal received "+body.decode('utf-8'))
        if body.decode('utf-8')=="SHUTDOWN":
            logger.info("message published %r" % body)
            channel.close()
            sys.exit()

    channel.basic_consume(queue=CONTROL__SIGNAL_IMED_QUEUE, on_message_callback=control_callback, auto_ack=True)

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




