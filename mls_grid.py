import os
import requests

MLS_GRID_BASE_URL = "https://api.mlsgrid.com/v2/Property"

def fetch_mls_listings(limit=100):
    token = os.environ.get("MLS_GRID_TOKEN")
    originating_system_name = os.environ.get("MLS_ORIGINATING_SYSTEM_NAME")

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }

    params = {
        "$select": "ListingKey,ListingId",
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

    if not response.ok:
        print("MLS Grid error status:", response.status_code)
        print("MLS Grid error response:", response.text)
        print("MLS Grid request URL:", response.url)
        response.raise_for_status()

    data = response.json()

    return data.get("value", [])