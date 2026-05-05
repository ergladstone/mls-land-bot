import os
import requests

MLS_GRID_BASE_URL = "https://api.mlsgrid.com/v2/Property"


def fetch_all_active_land_listings():
    token = os.environ.get("MLS_GRID_TOKEN")
    originating_system_name = os.environ.get("MLS_ORIGINATING_SYSTEM_NAME", "carolina")

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }

    all_listings = []
    skip = 0
    batch_size = 200  # max safe size

    while True:
        params = {
            "$select": ",".join([
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
            ]),
            "$filter": (
                f"OriginatingSystemName eq '{originating_system_name}' "
                f"and StandardStatus eq 'Active' "
                f"and PropertyType eq 'Land'"
            ),
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
            print("MLS Grid error:", response.text)
            break

        data = response.json()
        batch = data.get("value", [])

        if not batch:
            break

        all_listings.extend(batch)

        print(f"Fetched {len(batch)} listings (total: {len(all_listings)})")

        if len(batch) < batch_size:
            break

        skip += batch_size

    return all_listings