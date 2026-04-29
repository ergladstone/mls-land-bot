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

    acres = listing.get("LotSizeAcres")

    if acres in [None, ""]:
        lot_size_area = listing.get("LotSizeArea")
        lot_size_units = str(listing.get("LotSizeUnits", "")).lower()

        if lot_size_area not in [None, ""] and "acre" in lot_size_units:
            acres = lot_size_area

    if acres in [None, ""]:
        lot_size_sqft = listing.get("LotSizeSquareFeet")

        if lot_size_sqft not in [None, ""]:
            acres = round(float(lot_size_sqft) / 43560, 2)

    payload = {
        "status": "Qualified",
        "dateFound": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "mlsId": listing.get("ListingId", ""),
        "parcelId": listing.get("ParcelNumber", ""),
        "address": full_address,
        "county": listing.get("CountyOrParish", ""),
        "municipality": city,
        "acres": acres if acres not in [None, ""] else "",
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