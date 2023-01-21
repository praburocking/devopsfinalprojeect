
FROM python:3.9
WORKDIR /usr/src/orig
COPY . .
RUN pip install pika
RUN pip install PyLog2html
RUN pip install python-dotenv
RUN mkdir /usr/logs
CMD ["python3", "orig.py"]
