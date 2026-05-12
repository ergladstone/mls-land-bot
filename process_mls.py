print("PROCESS_MLS SCRIPT STARTED", flush=True)

import json
import os
import requests
from datetime import datetime, timezone

from filter import qualification_result, get_acres
from mls_grid import fetch_modified_land_listings_since

SHEET_WEBHOOK_URL = os.environ["SHEET_WEBHOOK_URL"]

with open("criteria.json", "r") as f:
    criteria = json.load(f)


def post_to_sheet(payload, timeout=60):
    try:
        response = requests.post(SHEET_WEBHOOK_URL, json=payload, timeout=timeout)
        response.raise_for_status()
        return response.text

    except requests.exceptions.Timeout:
        print(f"WARNING: Sheet webhook timed out for action: {payload.get('action')}", flush=True)
        return "TIMEOUT"

    except requests.exceptions.RequestException as e:
        print(f"WARNING: Sheet webhook failed for action {payload.get('action')}: {e}", flush=True)
        return f"ERROR: {e}"


def format_list(value):
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    return value or ""


def get_last_run():
    response_text = post_to_sheet({
        "action": "get_last_run"
    }, timeout=60)

    value = response_text.strip()

    if value and not value.startswith("ERROR") and value != "TIMEOUT":
        return value

    return "1970-01-01T00:00:00Z"


def set_last_run(timestamp):
    return post_to_sheet({
        "action": "set_last_run",
        "lastRun": timestamp
    }, timeout=60)


def build_payload(listing, action):
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

    return {
        "action": action,
        "dateFound": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "mlsId": listing.get("ListingId", ""),
        "parcelId": listing.get("ParcelNumber", ""),
        "address": full_address,
        "county": listing.get("CountyOrParish", ""),
        "acres": acres if acres else "",
        "price": listing.get("ListPrice", ""),
        "mlsLink": "",
        "gisLink": "",
        "waterType": format_list(listing.get("WaterSource")),
        "sewerType": format_list(listing.get("Sewer")),
        "subjectToHoa": "Yes" if float(listing.get("AssociationFee") or 0) > 0 else "No",
        "subjectToCcrs": listing.get("CAR_CCRSubjectTo", ""),
        "cityTaxPaidTo": listing.get("CAR_CityTaxesPaidTo", ""),
        "agentName": listing.get("ListAgentFullName", ""),
        "agentEmail": listing.get("ListAgentEmail", ""),
        "dateListed": listing.get("ListingContractDate", "").split("T")[0] if listing.get("ListingContractDate") else ""
    }


last_run = get_last_run()
new_last_run = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

print(f"Last MLS Run: {last_run}", flush=True)
print(f"New Last MLS Run will be: {new_last_run}", flush=True)

listings = fetch_modified_land_listings_since(last_run)

results = []
processed_count = 0

for listing in listings:
    listing_id = listing.get("ListingId", "")
    status = listing.get("StandardStatus", "")

    if status != "Active":
        payload = {
            "action": "delete",
            "mlsId": listing_id
        }

        sheet_response = post_to_sheet(payload, timeout=60)

        results.append({
            "listingId": listing_id,
            "action": "delete",
            "reason": f"Status is {status}",
            "sheetResponse": sheet_response
        })

    else:
        passed, reason = qualification_result(listing, criteria)

        if passed:
            payload = build_payload(listing, "upsert")
        else:
            payload = build_payload(listing, "update_if_exists")

        sheet_response = post_to_sheet(payload, timeout=60)

        results.append({
            "listingId": listing_id,
            "action": payload["action"],
            "reason": reason,
            "sheetResponse": sheet_response
        })

    processed_count += 1

    if processed_count % 25 == 0:
        print(f"Processed {processed_count} / {len(listings)}", flush=True)

set_response = set_last_run(new_last_run)

print(f"Processed total: {processed_count}", flush=True)
print(f"Last run update response: {set_response}", flush=True)
print("PROCESS COMPLETE", flush=True)