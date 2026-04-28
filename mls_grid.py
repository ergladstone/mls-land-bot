import os
import requests

MLS_GRID_BASE_URL = "https://api.mlsgrid.com/v2/Property"

def fetch_mls_listings(limit=100):
    token = os.environ.get("MLS_GRID_TOKEN")
    originating_system_name = os.environ.get("MLS_ORIGINATING_SYSTEM_NAME")
    property_type = os.environ.get("MLS_LIST_PROPERTY_TYPE", "Land")

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }

    params = {
        "$select": ",".join([
            "ListingKey",
            "ListingId",
            "MlsStatus",
            "StandardStatus",
            "ListPrice",
            "PropertyType",
            "LotSizeAcres",
            "RoadSurfaceType",
            "Sewer",
            "Latitude",
            "Longitude",
            "UnparsedAddress",
            "City",
            "CountyOrParish",
            "StateOrProvince",
            "PostalCode",
            "ModificationTimestamp",
            "ListAgentFullName",
            "ListAgentEmail",
        ]),
        "$filter": (
            f"OriginatingSystemName eq '{originating_system_name}' "
            f"and MlsStatus eq 'Active'"
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

    response.raise_for_status()
    data = response.json()

    return data.get("value", [])