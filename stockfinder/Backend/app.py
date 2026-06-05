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




from datetime import datetime

@app.get("/scan")
def scan_market():

    scan_status["running"] = True
    scan_status["message"] = "Scanning..."

    try:
        result = subprocess.run(
            ["python", "stock.py"],
            capture_output=True,
            text=True
        )

        scan_status["running"] = False
        scan_status["last_scan"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if result.returncode == 0:
            scan_status["message"] = "Completed"
        else:
            scan_status["message"] = result.stderr

        return {
            "returncode": result.returncode
        }

    except Exception as e:

        scan_status["running"] = False
        scan_status["message"] = str(e)

        return {"error": str(e)}
           
scan_status = {
    "running": False,
    "last_scan": None,
    "message": ""
}

@app.get("/scan-status")
def get_scan_status():
    return scan_status
@app.get("/env")


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