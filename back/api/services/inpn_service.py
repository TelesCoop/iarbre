import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from django.core.cache import cache

logger = logging.getLogger(__name__)

TAXREF_API_URL = "https://taxref.mnhn.fr/api/taxa/search"
TAXREF_TIMEOUT = 5
MAX_WORKERS = 5


def _check_species(scientific_name: str) -> tuple[str, bool]:
    cache_key = f"taxref_{scientific_name.replace(' ', '_').lower()}"
    cached = cache.get(cache_key)
    if cached is not None:
        return scientific_name, cached

    try:
        response = requests.get(
            TAXREF_API_URL,
            params={"scientificNames": scientific_name, "territories": "fr"},
            timeout=TAXREF_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        found = data.get("page", {}).get("totalElements", 0) > 0
    except Exception:
        logger.warning(f"TaxRef API unavailable for {scientific_name}")
        found = False

    cache.set(cache_key, found, timeout=None)
    return scientific_name, found


def validate_species_in_france(scientific_names: list[str]) -> dict[str, bool]:
    """Validate a list of species names against the INPN TaxRef API (parallel)."""
    results: dict[str, bool] = {}

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(_check_species, name): name for name in scientific_names
        }
        for future in as_completed(futures):
            try:
                name, found = future.result()
                results[name] = found
            except Exception:
                results[futures[future]] = False

    return results
