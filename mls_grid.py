import os
import requests

MLS_GRID_BASE_URL = "https://api.mlsgrid.com/v2/Property"

def fetch_mls_listings(limit=50):
    token = os.environ.get("MLS_GRID_TOKEN")
    originating_system_name = os.environ.get("MLS_ORIGINATING_SYSTEM_NAME", "carolina")

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }

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
            "OriginatingSystemName",
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
            "ModificationTimestamp"
        ]),
        "$filter": (
            f"OriginatingSystemName eq '{originating_system_name}' "
            f"and StandardStatus eq 'Active' "
            f"and PropertyType eq 'Land'"
        ),
        "$orderby": "ModificationTimestamp desc",
        "$top": str(limit),
    }

    response = requests.get(
        MLS_GRID_BASE_URL,
        headers=headers,
        params=params,
        timeout=30,
    )

    if not response.ok:
        print("MLS Grid error status:", response.status_code)
        print("MLS Grid error response:", response.text)
        print("MLS Grid request URL:", response.url)
        response.raise_for_status()

    data = response.json()
    return data.get("value", [])