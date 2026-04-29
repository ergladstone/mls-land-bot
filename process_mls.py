import json
import requests
import os
from datetime import datetime
from mls_grid import fetch_mls_listings

SHEET_WEBHOOK_URL = os.environ["SHEET_WEBHOOK_URL"]

# Fetch ONLY 5 listings
listings = fetch_mls_listings(limit=5)

results = []

for listing in listings:
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

print(results)