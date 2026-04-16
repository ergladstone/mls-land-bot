from flask import Flask, request, jsonify
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
        "status": "Qualified",
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


@app.route("/add-lead", methods=["POST"])
def add_lead():
    data = request.get_json()

    payload = {
        "status": data.get("status", "Qualified"),
        "dateFound": data.get("dateFound", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        "mlsId": data.get("mlsId", ""),
        "parcelId": data.get("parcelId", ""),
        "county": data.get("county", ""),
        "address": data.get("address", ""),
        "acres": data.get("acres", ""),
        "price": data.get("price", ""),
        "agentName": data.get("agentName", ""),
        "agentEmail": data.get("agentEmail", ""),
        "mlsLink": data.get("mlsLink", ""),
        "gisLink": data.get("gisLink", "")
    }

    response = requests.post(SHEET_WEBHOOK_URL, json=payload)

    return jsonify({
        "status": "ok",
        "sheet_response": response.text
    })