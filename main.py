from flask import Flask
import requests
import os
from datetime import datetime

app = Flask(__name__)

SHEET_WEBHOOK_URL = os.environ["SHEET_WEBHOOK_URL"]

@app.route("/")
def home():
    return "MLS Land Bot is running"

@app.route("/test-lead")
def test_lead():
    payload = {
        "status": "New",
        "dateFound": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "mlsId": "TEST123",
        "parcelId": "PARCEL123",
        "county": "Cabarrus",
        "address": "123 Test Road",
        "acres": 5,
        "price": 100000,
        "agentName": "Test Agent",
        "agentEmail": "evan@prespro.com",
        "mlsLink": "https://example.com/mls",
        "gisLink": "https://example.com/gis"
    }

    response = requests.post(SHEET_WEBHOOK_URL, json=payload)
    return f"Sheet response: {response.text}"