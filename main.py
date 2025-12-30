
from fastapi import FastAPI

app=fastAPI()

@app.get("/")
def read_root():
    return{"message": "Hello world"}
