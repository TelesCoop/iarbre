import logging
from collections import Counter

import requests

logger = logging.getLogger(__name__)

GBIF_API_URL = "https://api.gbif.org/v1/occurrence/search"
GBIF_TIMEOUT_SECONDS = 5
PLANTAE_KINGDOM_KEY = 6


def fetch_local_flora(lat: float, lng: float, radius_m: int = 1000) -> list[dict]:
    """Fetch plant species occurrences near coordinates from GBIF API.

    Returns a deduplicated list of species sorted by occurrence count.
    """
    params = {
        "decimalLatitude": lat,
        "decimalLongitude": lng,
        "radius": radius_m,
        "kingdomKey": PLANTAE_KINGDOM_KEY,
        "limit": 300,
        "hasCoordinate": "true",
        "hasGeospatialIssue": "false",
    }

    try:
        response = requests.get(
            GBIF_API_URL, params=params, timeout=GBIF_TIMEOUT_SECONDS
        )
        response.raise_for_status()
    except (requests.RequestException, requests.Timeout):
        logger.warning("GBIF API unavailable for coordinates (%s, %s)", lat, lng)
        return []

    results = response.json().get("results", [])
    species_counter: Counter[str] = Counter()
    species_info: dict[str, dict] = {}

    for record in results:
        species_name = record.get("species")
        if not species_name:
            continue

        species_counter[species_name] += 1
        if species_name not in species_info:
            species_info[species_name] = {
                "species": species_name,
                "genus": record.get("genus", ""),
                "family": record.get("family", ""),
            }

    flora = []
    for species_name, count in species_counter.most_common():
        entry = species_info[species_name].copy()
        entry["occurrence_count"] = count
        flora.append(entry)

    return flora
