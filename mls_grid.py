import os
import time
import requests

MLS_GRID_BASE_URL = "https://api.mlsgrid.com/v2/Property"

SELECT_FIELDS = ",".join([
    "ListingId",
    "ParcelNumber",
    "StreetNumber",
    "StreetName",
    "StreetSuffix",
    "City",
    "CountyOrParish",
    "StateOrProvince",
    "PostalCode",
    "LotSizeAcres",
    "LotSizeArea",
    "LotSizeUnits",
    "LotSizeSquareFeet",
    "ListPrice",
    "StandardStatus",
    "PropertyType",
    "Latitude",
    "Longitude",
    "WaterSource",
    "Sewer",
    "RoadSurfaceType",
    "PossibleUse",
    "CAR_CCRSubjectTo",
    "CAR_CityTaxesPaidTo",
    "AssociationFee",
    "ListAgentFullName",
    "ListAgentEmail",
    "ListingContractDate",
    "ModificationTimestamp"
])


def get_headers():
    token = os.environ.get("MLS_GRID_TOKEN")

    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }


def make_mls_request(params, headers, label):
    max_attempts = 3

    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.get(
                MLS_GRID_BASE_URL,
                headers=headers,
                params=params,
                timeout=60,
            )

            if not response.ok:
                print("MLS Grid error status:", response.status_code, flush=True)
                print("MLS Grid error response:", response.text, flush=True)
                print("MLS Grid request URL:", response.url, flush=True)
                response.raise_for_status()

            return response

        except requests.exceptions.Timeout:
            print(
                f"{label}: MLS Grid timeout. Attempt {attempt}/{max_attempts}",
                flush=True
            )

            if attempt == max_attempts:
                raise

            time.sleep(3)

        except requests.exceptions.RequestException as e:
            print(
                f"{label}: MLS Grid request failed. Attempt {attempt}/{max_attempts}: {e}",
                flush=True
            )

            if attempt == max_attempts:
                raise

            time.sleep(3)


def fetch_paginated_listings(filter_text, label="MLS"):
    headers = get_headers()

    all_listings = []
    seen_listing_ids = set()
    skip = 0
    batch_size = 100

    while True:
        print(f"{label}: requesting skip={skip}", flush=True)

        params = {
            "$select": SELECT_FIELDS,
            "$filter": filter_text,
            "$orderby": "ModificationTimestamp desc",
            "$top": str(batch_size),
            "$skip": str(skip),
        }

        response = make_mls_request(params, headers, label)
        data = response.json()
        batch = data.get("value", [])
        
        print(f"{label}: MLS Grid returned {len(batch)} listings", flush=True)

        if not batch:
            break

        new_batch = []

        for listing in batch:
            listing_id = listing.get("ListingId")

            if listing_id and listing_id not in seen_listing_ids:
                seen_listing_ids.add(listing_id)
                new_batch.append(listing)

        if not new_batch:
            print(f"{label}: no new unique listings in this batch. Stopping.", flush=True)
            break

        all_listings.extend(new_batch)

        print(
            f"{label}: fetched {len(new_batch)} new listings "
            f"(total: {len(all_listings)})",
            flush=True
        )

        if len(batch) < batch_size:
            break

        skip += batch_size

    return all_listings


def fetch_all_active_land_listings():
    originating_system_name = os.environ.get("MLS_ORIGINATING_SYSTEM_NAME", "carolina")

    filter_text = (
        f"OriginatingSystemName eq '{originating_system_name}' "
        f"and StandardStatus eq 'Active' "
        f"and PropertyType eq 'Land'"
    )

    return fetch_paginated_listings(filter_text, label="Full active scan")


def fetch_modified_land_listings_since(last_run):
    originating_system_name = os.environ.get("MLS_ORIGINATING_SYSTEM_NAME", "carolina")

    filter_text = (
        f"OriginatingSystemName eq '{originating_system_name}' "
        f"and PropertyType eq 'Land' "
        f"and ModificationTimestamp gt '{last_run}'"
    )

    return fetch_paginated_listings(filter_text, label="Incremental scan")