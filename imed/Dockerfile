FROM python:3.9
WORKDIR /usr/src/imed
COPY . .
RUN pip install pika
RUN pip install PyLog2html
RUN pip install python-dotenv
RUN mkdir /usr/logs
RUN echo "starting imed.py"
CMD ["python3", "imed.py"]
