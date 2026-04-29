import os
import requests
from datetime import datetime
from mls_grid import fetch_mls_listings

SHEET_WEBHOOK_URL = os.environ["SHEET_WEBHOOK_URL"]

# Fetch ONLY 5 active MLS listings for now
listings = fetch_mls_listings(limit=5)

results = []

for listing in listings:
    street_number = listing.get("StreetNumber", "")
    street_name = listing.get("StreetName", "")
    address = f"{street_number} {street_name}".strip()

    payload = {
        "status": "Qualified",
        "dateFound": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "mlsId": listing.get("ListingId", ""),
        "parcelId": listing.get("ParcelNumber", ""),
        "address": address,
        "county": listing.get("CountyOrParish", ""),
        "municipality": listing.get("City", ""),
        "acres": listing.get("LotSizeAcres", ""),
        "price": listing.get("ListPrice", ""),
        "mlsLink": f"https://matrix.canopymls.com/matrix/shared/{listing.get('ListingId', '')}",
        "gisLink": ""
    }

    response = requests.post(SHEET_WEBHOOK_URL, json=payload)

    results.append({
        "listingId": listing.get("ListingId"),
        "sentToSheet": True,
        "sheetResponse": response.text
    })

print(results)