from fastapi import FastAPI
import json
import os
from fastapi.middleware.cors import CORSMiddleware
import subprocess

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
API_KEY = os.getenv("API_KEY")
CLIENT_ID = os.getenv("CLIENT_ID")
MPIN = os.getenv("MPIN")
TOTP_SECRET = os.getenv("TOTP_SECRET")

@app.get("/")
def home():
    return {
        "status": "Scanner API Running"
    }

@app.get("/scan")
def scan_market():

    try:
        subprocess.run(
            ["python", "stock.py"],
            check=True
        )

        return {
            "status": "success",
            "message": "Scan completed"
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }
           
@app.get("/env")
def env():
    return {
        "api": API_KEY is not None,
        "client": CLIENT_ID is not None
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