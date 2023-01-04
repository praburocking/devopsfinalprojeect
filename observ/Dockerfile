FROM python:3.9
WORKDIR /usr/src/observ
RUN mkdir /usr/data
COPY . .
RUN pip install pika
CMD ["python3", "observ.py"]
