import json
import requests
import os
from datetime import datetime
from filter import qualifies
from mls_grid import fetch_mls_listings

SHEET_WEBHOOK_URL = os.environ["SHEET_WEBHOOK_URL"]

with open("criteria.json", "r") as f:
    criteria = json.load(f)

# Fetch real MLS data
listings = fetch_mls_listings(limit=50)

results = []

for listing in listings:
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

print(results)