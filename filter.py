import math


def distance_miles(lat1, lon1, lat2, lon2):
    radius = 3958.8

    lat1 = math.radians(float(lat1))
    lon1 = math.radians(float(lon1))
    lat2 = math.radians(float(lat2))
    lon2 = math.radians(float(lon2))

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius * c


def value_contains(value, search_text):
    if value is None:
        return False

    if isinstance(value, list):
        return any(search_text in str(item).lower() for item in value)

    return search_text in str(value).lower()


def value_is_blank(value):
    return value is None or value == "" or value == []


def get_acres(listing):
    acres = listing.get("LotSizeAcres")

    if acres not in [None, ""]:
        return float(acres)

    lot_size_area = listing.get("LotSizeArea")
    lot_size_units = str(listing.get("LotSizeUnits", "")).lower()

    if lot_size_area not in [None, ""] and "acre" in lot_size_units:
        return float(lot_size_area)

    lot_size_sqft = listing.get("LotSizeSquareFeet")

    if lot_size_sqft not in [None, ""]:
        return float(lot_size_sqft) / 43560

    return 0


def qualification_result(listing, criteria=None):
    if listing.get("StandardStatus") != "Active":
        return False, "Status is not Active"

    if listing.get("PropertyType") != "Land":
        return False, "PropertyType is not Land"

    price = listing.get("ListPrice")
    if price in [None, ""]:
        return False, "Missing ListPrice"

    if float(price) > 120000:
        return False, "ListPrice over 120000"

    if listing.get("Latitude") in [None, ""] or listing.get("Longitude") in [None, ""]:
        return False, "Missing Latitude or Longitude"

    concord_lat = 35.4088
    concord_lng = -80.5795

    miles = distance_miles(
        listing.get("Latitude"),
        listing.get("Longitude"),
        concord_lat,
        concord_lng
    )

    if miles > 40:
        return False, f"Outside 40 miles from Concord ({round(miles, 1)} miles)"

    road_surface = listing.get("RoadSurfaceType")

    if value_contains(road_surface, "dirt"):
        return False, "RoadSurfaceType contains dirt"

    possible_use = listing.get("PossibleUse")

    if not value_is_blank(possible_use):
        if not value_contains(possible_use, "residential"):
            return False, "PossibleUse is not blank or residential"

    sewer = listing.get("Sewer")
    acres = get_acres(listing)

    if value_contains(sewer, "sewer"):
        if acres < 0.1:
            return False, f"Acres below 0.1 for sewer ({round(acres, 2)})"
    else:
        if acres < 0.7:
            return False, f"Acres below 0.7 for septic/unknown sewer ({round(acres, 2)})"

    return True, "Qualified"


def qualifies(listing, criteria=None):
    passed, reason = qualification_result(listing, criteria)
    return passed