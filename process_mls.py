import json
import os
import requests
from datetime import datetime
from filter import qualification_result, get_acres
from mls_grid import fetch_mls_listings

SHEET_WEBHOOK_URL = os.environ["SHEET_WEBHOOK_URL"]

with open("criteria.json", "r") as f:
    criteria = json.load(f)

# Fetch MLS listings
listings = fetch_mls_listings(limit=50)

results = []

for listing in listings:
    passed, reason = qualification_result(listing, criteria)

    if not passed:
    	delete_payload = {
        	"action": "delete",
        	"mlsId": listing.get("ListingId", "")
    	}

    	response = requests.post(SHEET_WEBHOOK_URL, json=delete_payload)

    	results.append({
        	"listingId": listing.get("ListingId"),
        	"sentToSheet": False,
        	"deletedFromSheet": True,
        	"reason": reason,
        	"sheetResponse": response.text
    	})
    	continue

    # DEBUG: check city tax field
    print("CITY TAX FIELD:", listing.get("CAR_CityTaxesPaidTo"))

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
        "dateFound": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "mlsId": listing.get("ListingId", ""),
        "parcelId": listing.get("ParcelNumber", ""),
        "address": full_address,
        "county": listing.get("CountyOrParish", ""),
        "municipality": city,
        "acres": acres if acres else "",
        "price": listing.get("ListPrice", ""),
        "mlsLink": "",
        "gisLink": "",
        "waterType": ", ".join(listing.get("WaterSource", [])) if isinstance(listing.get("WaterSource"), list) else listing.get("WaterSource", ""),
        "sewerType": ", ".join(listing.get("Sewer", [])) if isinstance(listing.get("Sewer"), list) else listing.get("Sewer", ""),
        "subjectToHoa": "Yes" if float(listing.get("AssociationFee") or 0) > 0 else "No",
        "subjectToCcrs": listing.get("CAR_CCRSubjectTo", ""),
        "cityTaxPaidTo": listing.get("CAR_CityTaxesPaidTo", ""),
        "agentName": listing.get("ListAgentFullName", ""),
        "agentEmail": listing.get("ListAgentEmail", "")
    }

    response = requests.post(SHEET_WEBHOOK_URL, json=payload)

    results.append({
        "listingId": listing.get("ListingId"),
        "sentToSheet": True,
        "reason": reason,
        "sheetResponse": response.text
    })

print(results)