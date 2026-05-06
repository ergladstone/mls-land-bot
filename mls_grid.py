import os
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


def fetch_paginated_listings(filter_text, label="MLS"):
    headers = get_headers()

    all_listings = []
    skip = 0
    batch_size = 200

    while True:
        params = {
            "$select": SELECT_FIELDS,
            "$filter": filter_text,
            "$orderby": "ModificationTimestamp desc",
            "$top": str(batch_size),
            "$skip": str(skip),
        }

        response = requests.get(
            MLS_GRID_BASE_URL,
            headers=headers,
            params=params,
            timeout=60,
        )

        if not response.ok:
            print("MLS Grid error status:", response.status_code)
            print("MLS Grid error response:", response.text)
            print("MLS Grid request URL:", response.url)
            response.raise_for_status()

        data = response.json()
        batch = data.get("value", [])

        if not batch:
            break

        all_listings.extend(batch)
        print(f"{label}: fetched {len(batch)} listings (total: {len(all_listings)})")

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
        f"and ModificationTimestamp gt {last_run}"
    )

    return fetch_paginated_listings(filter_text, label="Incremental scan")