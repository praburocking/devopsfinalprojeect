from typing import Union

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
import uvicorn

app = FastAPI()
FILE_PATH="/usr/data/temp_file.txt"

@app.get("/", response_class=PlainTextResponse)
def read_root():
	f = open(FILE_PATH, "r")
	return str(f.read())
    
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
    
