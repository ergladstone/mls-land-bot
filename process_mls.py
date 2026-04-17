import json
import requests
import os
from datetime import datetime
from filter import qualifies

SHEET_WEBHOOK_URL = os.environ["SHEET_WEBHOOK_URL"]

with open("criteria.json", "r") as f:
    criteria = json.load(f)


def process_sample_mls():
    with open("mls_sample.json", "r") as f:
        mls_data = json.load(f)

    results = []

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
                "mlsLink": f"https://matrix.canopymls.com/matrix/shared/{listing.get('ListingId', '')}",
                "gisLink": ""
            }

            response = requests.post(SHEET_WEBHOOK_URL, json=payload)

            results.append({
                "listingId": listing.get("ListingId"),
                "qualified": True,
                "sheetResponse": response.text
            })
        else:
            results.append({
                "listingId": listing.get("ListingId"),
                "qualified": False
            })

    return results