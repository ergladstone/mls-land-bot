from flask import Flask, request, jsonify
import requests
import os
import json
from datetime import datetime
from filter import qualifies
from process_mls import process_sample_mls

app = Flask(__name__)

SHEET_WEBHOOK_URL = os.environ["SHEET_WEBHOOK_URL"]

with open("criteria.json", "r") as f:
    criteria = json.load(f)


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


@app.route("/test-filter")
def test_filter():
    listing = {
        "CountyOrParish": "Cabarrus",
        "Latitude": 35.4100,
        "Longitude": -80.6000,
        "MlsStatus": "Active",
        "ListPrice": 100000,
        "LotSizeAcres": 1.2,
        "Sewer": "Septic Needed",
        "RoadSurfaceType": "Paved",
        "ListingId": "FILTER001",
        "ListAgentFullName": "Test Agent",
        "ListAgentEmail": "evan@prespro.com",
        "UnparsedAddress": "456 Example Lane"
    }

    return jsonify({
        "qualifies": qualifies(listing, criteria),
        "listing": listing,
        "criteria": criteria
    })

@app.route("/process-sample")
def process_sample():
    result = process_sample_mls()
    return jsonify(result)

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