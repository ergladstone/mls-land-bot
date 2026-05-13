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
            print(f"{label}: MLS Grid timeout. Attempt {attempt}/{max_attempts}", flush=True)

            if attempt == max_attempts:
                raise

            time.sleep(3)

        except requests.exceptions.RequestException as e:
            print(f"{label}: MLS Grid request failed. Attempt {attempt}/{max_attempts}: {e}", flush=True)

            if attempt == max_attempts:
                raise

            time.sleep(3)


def fetch_paginated_listings(filter_text, label="MLS", max_records=None):
    headers = get_headers()

    all_listings = []
    skip = 0
    batch_size = 200

    while True:
        current_top = batch_size

        if max_records is not None:
            remaining = max_records - len(all_listings)

            if remaining <= 0:
                break

            current_top = min(batch_size, remaining)

        print(f"{label}: requesting skip={skip}", flush=True)
        print(f"{label}: filter={filter_text}", flush=True)

        params = {
            "$select": SELECT_FIELDS,
            "$filter": filter_text,
            "$orderby": "ModificationTimestamp asc",
            "$top": str(current_top),
            "$skip": str(skip),
        }

        response = make_mls_request(params, headers, label)

        data = response.json()
        batch = data.get("value", [])

        print(f"{label}: MLS Grid returned {len(batch)} listings", flush=True)

        if not batch:
            break

        all_listings.extend(batch)

        print(
            f"{label}: fetched {len(batch)} listings "
            f"(total: {len(all_listings)})",
            flush=True
        )

        if len(batch) < current_top:
            break

        if max_records is not None and len(all_listings) >= max_records:
            break

        skip += current_top

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
        f"and ModificationTimestamp gt {last_run}"
    )

    return fetch_paginated_listings(
        filter_text,
        label="Incremental scan",
        max_records=100
    )