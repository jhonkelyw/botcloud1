from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from pydantic import BaseModel
import uuid
import requests

API_KEY = "API_BOTCLOUD_123456"
MONGO_URI = "mongodb+srv://botcloud_user:I2562Ojhonkely@botclouddb.abcde.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(MONGO_URI)
db = client.botcloud
files = db.files

app = FastAPI()

class UploadRequest(BaseModel):
    api_key: str
    file_name: str
    size_mb: int

@app.post("/upload")
def upload_file(request: UploadRequest):
    user = files.find_one({"api_key": API_KEY})
    if user is None:
        files.insert_one({"api_key": API_KEY, "used": 0, "limit": 50})
        user = files.find_one({"api_key": API_KEY})

    if request.api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    if user["used"] + request.size_mb > user["limit"]:
        raise HTTPException(status_code=402, detail="Storage Limit Reached")

    files.update_one({"api_key": API_KEY}, {"$inc": {"used": request.size_mb}})
    return {"message": "File uploaded successfully", "remaining_space": user["limit"] - user["used"]}

@app.post("/payment")
def create_payment():
    payment_id = str(uuid.uuid4())
    files.insert_one({"payment_id": payment_id, "status": "paid"})
    return {"payment_id": payment_id, "message": "Payment registered successfully"}

@app.get("/simulate_bot")
def simulate_bot():
    headers = {"Content-Type": "application/json"}
    upload_payload = {"api_key": API_KEY, "file_name": "bot_file.txt", "size_mb": 10}
    requests.post("http://localhost:10000/upload", json=upload_payload, headers=headers)
    return {"message": "Bot Simulated Successfully"}

@app.get("/")
def root():
    return {"message": "Welcome to BotCloud API"}