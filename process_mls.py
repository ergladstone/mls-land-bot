import json
import requests
import os
from datetime import datetime
from filter import qualifies

SHEET_WEBHOOK_URL = os.environ["SHEET_WEBHOOK_URL"]

with open("criteria.json", "r") as f:
    criteria = json.load(f)

with open("mls_sample.json", "r") as f:
    mls_data = json.load(f)

for listing in mls_data["value"]:
    if qualifies(listing, criteria):
        payload = {
            "status": "Qualified",
            "dateFound": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "mlsId": listing.get("ListingId", ""),
            "parcelId": "",
            "county": listing.get("CountyOrParish", ""),
            "address": listing.get("UnparsedAddress", ""),
            "acres": listing.get("LotSizeAcres", ""),
            "price": listing.get("ListPrice", ""),
            "agentName": listing.get("ListAgentFullName", ""),
            "agentEmail": listing.get("ListAgentEmail", ""),
            "mlsLink": "",
            "gisLink": ""
        }

        response = requests.post(SHEET_WEBHOOK_URL, json=payload)
        print(f'Sent {listing.get("ListingId")} -> {response.text}')
    else:
        print(f'Skipped {listing.get("ListingId")}')