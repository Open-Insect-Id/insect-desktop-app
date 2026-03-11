import requests
import json
from random import sample

from utils.logger import setup_logger
logger = setup_logger(__name__)

def get_species_id(species_name: str) -> tuple[str, str]:
    """GBIF search for species ID. Returns (usageKey, nubKey)."""
    try:
        search_url = f"https://api.gbif.org/v1/species/match?name={species_name.replace(' ', '+')}"
        resp = requests.get(search_url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            usage_key = str(data.get('usageKey', ''))
            nub_key = str(data.get('nubKey', usage_key))
            logger.debug(f"GBIF search for '{species_name}': usageKey={usage_key}, nubKey={nub_key}")
            return usage_key, nub_key
        return "", ""
    except Exception as e:
        logger.error(f"Erreur lors de la recherche de l'espèce: {e}")
        return "", ""
    
def get_species_info(species_id: str) -> dict:
    """GBIF lookup."""
    try:
        detail_url = f"https://api.gbif.org/v1/species/{species_id}"
        detail_resp = requests.get(detail_url, timeout=10)
        data = detail_resp.json()

        logger.debug(f"GBIF detail response for '{species_id}': {data}")
        
        return {
            "nom": data.get("scientificName", ""),
            "famille": data.get("family", ""),
            "genre": data.get("genus", ""),
            "url": f"https://www.gbif.org/species/{species_id}"
        }
    except Exception as e:
        logger.error(f"API erreur: {e}")
        return {"error": f"API erreur: {e}"}

def get_species_image(species_id: str, limit: int = 10) -> list:
    """GBIF media lookup from iNaturalist observations for better relevance."""
    images = []
    try:
        media_url = f"https://api.gbif.org/v1/occurrence/search?taxonKey={species_id}&mediaType=StillImage&limit={limit}"
        media_resp = requests.get(media_url, timeout=10)
        media_data = media_resp.json()

        logger.info(f"Media response status: {media_resp.status_code}")
        logger.debug(f"Media response data: {media_data}")
        for item in media_data.get("results", []):
            if "media" in item:
                for med in item["media"]:
                    if med.get("identifier"):
                        images.append(
                            med.get("identifier")
                        )
        logger.debug(f"Extracted image URLs: {sample(images, min(len(images), 10))}")
        return images
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'image: {e}")
        return []
    
def get_species_locations(species_id: str, count: int = 300) -> list:
    """GBIF occurrence lookup with parallel requests."""
    try:
        locations = []
        limit_per_page = 300
        num_pages = (count + limit_per_page - 1) // limit_per_page
        
        def fetch_page(offset):
            occ_url = f"https://api.gbif.org/v1/occurrence/search?taxonKey={species_id}&hasCoordinate=true&limit={limit_per_page}&offset={offset}"
            try:
                occ_resp = requests.get(occ_url, timeout=15)
                if occ_resp.status_code == 200:
                    data = occ_resp.json()
                    page_locations = []
                    for item in data.get("results", []):
                        if "decimalLatitude" in item and "decimalLongitude" in item:
                            page_locations.append((item["decimalLatitude"], item["decimalLongitude"]))
                    return page_locations
            except Exception as e:
                logger.error(f"Error fetching page at offset {offset}: {e}")
            return []

        offsets = [i * limit_per_page for i in range(num_pages)]
        for offset in offsets:
            page_locs = fetch_page(offset)
            locations.extend(page_locs)
            if len(locations) >= count:
                break
            
        return locations
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des occurrences: {e}")
        return []