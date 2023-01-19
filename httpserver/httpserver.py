from typing import Union

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
import uvicorn
from HTMLLogger import HTMLLogger
from datetime import datetime
now = datetime.now()
LOG_DIR="/usr/logs"
LOG_PREFIX=now.strftime("%d_%m_%Y_%H_%M_%S")
log_file=LOG_DIR+"/"+LOG_PREFIX+"_httpserver_logs.html"
logger=HTMLLogger(name="HTTP SERVER", html_filename=log_file, console_log=True)

app = FastAPI()
FILE_PATH="/usr/data/temp_file.txt"

@app.get("/", response_class=PlainTextResponse)
def read_root():
	f = open(FILE_PATH, "r")
	return str(f.read())
    
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
    
