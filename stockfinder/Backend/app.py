from fastapi import FastAPI
import json
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "status": "Scanner API Running"
    }

@app.get("/candidates")
def get_candidates():

    if not os.path.exists("candidates.json"):
        return {
            "status": "error",
            "message": "candidates.json not found"
        }

    try:
        with open("candidates.json", "r") as f:
            data = json.load(f)

        return {
            "count": len(data),
            "stocks": data
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }