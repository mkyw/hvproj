#
#  app.py
#  hvProj
#
#  Created by Michael Wong on 3/3/25.
#


from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Address API!"}

class Address(BaseModel):
    address: str

@app.post("/address")
async def receive_address(address: Address):
    # API calls and mortgage calculation
    return {"message": "Address received successfully", "address": address.address}



# Handling the favicon.ico request
@app.get("/favicon.ico")
async def favicon():
    return {}
