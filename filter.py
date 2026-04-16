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


def qualifies(listing, criteria):
    if listing.get("MlsStatus") != criteria["required_status"]:
        return False

    if float(listing.get("ListPrice", 0)) > criteria["max_price"]:
        return False

    road_surface = str(listing.get("RoadSurfaceType", "")).lower()
    if criteria["excluded_road_surface"].lower() in road_surface:
        return False

    miles = distance_miles(
        listing.get("Latitude"),
        listing.get("Longitude"),
        criteria["center_latitude"],
        criteria["center_longitude"]
    )

    if miles > criteria["radius_miles"]:
        return False

    sewer = str(listing.get("Sewer", "")).lower()
    acres = float(listing.get("LotSizeAcres", 0))

    if "sewer" in sewer:
        if acres < criteria["minimum_acres_with_sewer"]:
            return False
    else:
        if acres < criteria["minimum_acres_without_sewer"]:
            return False

    return True