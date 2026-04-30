import json
import os
import requests
from datetime import datetime
from filter import qualification_result, get_acres
from mls_grid import fetch_mls_listings

SHEET_WEBHOOK_URL = os.environ["SHEET_WEBHOOK_URL"]

with open("criteria.json", "r") as f:
    criteria = json.load(f)

# Fetch ONLY 5 active MLS land listings for now
listings = fetch_mls_listings(limit=50)

results = []

for listing in listings:
    passed, reason = qualification_result(listing, criteria)

    if not passed:
        results.append({
            "listingId": listing.get("ListingId"),
            "sentToSheet": False,
            "reason": reason
        })
        continue

    street_number = listing.get("StreetNumber", "")
    street_name = listing.get("StreetName", "")
    street_suffix = listing.get("StreetSuffix", "")
    city = listing.get("City", "")
    state = listing.get("StateOrProvince", "")
    zip_code = listing.get("PostalCode", "")

    street_address = " ".join(
        part for part in [street_number, street_name, street_suffix] if part
    ).strip()

    city_state_zip = " ".join(
        part for part in [city, state, zip_code] if part
    ).strip()

    full_address = ", ".join(
        part for part in [street_address, city_state_zip] if part
    )

    acres = get_acres(listing)

    payload = {
        "status": "New",
        "dateFound": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "mlsId": listing.get("ListingId", ""),
        "parcelId": listing.get("ParcelNumber", ""),
        "address": full_address,
        "county": listing.get("CountyOrParish", ""),
        "municipality": city,
        "acres": acres if acres else "",
        "price": listing.get("ListPrice", ""),
        "mlsLink": "",
        "gisLink": ""
    }

    response = requests.post(SHEET_WEBHOOK_URL, json=payload)

    results.append({
        "listingId": listing.get("ListingId"),
        "sentToSheet": True,
        "reason": reason,
        "sheetResponse": response.text
    })

print(results)