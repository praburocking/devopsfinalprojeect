import pika
import time


HOST="exe3-rabitmq-1"
#HOST="localhost"
ROUTING_KEY1="compse140.o"
EXCHANGE='topic_msg'
ROUTING_KEY2="compse140.i"


def is_port_in_use(port: int) -> bool:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
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
N=3
for i in range(N):
    channel.basic_publish(exchange=EXCHANGE,
                        routing_key=ROUTING_KEY1,
                        body='MSG_'+str(i+1))
    print(" [x] Sent 'Hello World!---'")
    time.sleep(3)

connection.close()

