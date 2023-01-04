FROM python:3.9
WORKDIR /usr/src/httpserver
RUN mkdir /usr/data
COPY . .
RUN pip install fastapi
RUN pip install "uvicorn[standard]"
EXPOSE 8080
CMD ["python3" ,"httpserver.py"]

#CMD ["uvicorn" "httpserver:app" "--reload"]
