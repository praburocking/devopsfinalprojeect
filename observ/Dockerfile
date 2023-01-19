FROM python:3.9
WORKDIR /usr/src/observ
RUN mkdir /usr/data
RUN mkdir /usr/logs
COPY . .
RUN pip install pika
RUN pip install PyLog2html
CMD ["python3", "observ.py"]
