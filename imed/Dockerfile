FROM python:3.9
WORKDIR /usr/src/imed
COPY . .
RUN pip install pika
RUN echo "starting imed.py"
CMD ["python3", "imed.py"]
