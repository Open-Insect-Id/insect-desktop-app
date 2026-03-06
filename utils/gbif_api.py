from math import lgamma

import requests

from utils.logger import setup_logger
logger = setup_logger(__name__)


def get_species_id(species_name: str) -> str:
    """GBIF search for species ID."""
    try:
        search_url = "https://api.gbif.org/v1/species/search?q=" + species_name.replace(" ", "+")
        resp = requests.get(search_url, timeout=5)
        if resp.status_code == 200 and resp.json()['results']:
            return str(resp.json()['results'][0]['key']),str(resp.json()['results'][0]['nubKey'])
        else:
            return ""
    except Exception as e:
        logger.error(f"Erreur lors de la recherche de l'espèce: {e}")
        return ""
    
def get_species_info(species_id: str) -> dict:
    """GBIF lookup."""
    try:
        detail_url = f"https://api.gbif.org/v1/species/{species_id}"
        detail_resp = requests.get(detail_url, timeout=10)
        data = detail_resp.json()
        
        return {
            "nom": data.get("scientificName", ""),
            "famille": data.get("family", ""),
            "genre": data.get("genus", ""),
            "url": f"https://www.gbif.org/species/{species_id}"
        }
    except Exception as e:
        return {"error": f"API erreur: {e}"}

def get_species_image(species_id: str, limit: int = 10) -> list:
    """GBIF media lookup."""
    images = []
    try:
        media_url = f"https://api.gbif.org/v1/occurrence/search?taxonKey={species_id}&mediaType=StillImage&limit={limit}"
        media_resp = requests.get(media_url, timeout=10)
        media_data = media_resp.json()
        
        logger.info(f"Media response status: {media_resp.status_code}")
        logger.debug(f"Media data count: {media_data.get('count', 0)}")
        
        for item in media_data.get("results", []):
            if "media" in item:
                for med in item["media"]:
                    if med.get("type") == "StillImage" and med.get("identifier"):
                        images.append({
                            'url': med["identifier"],
                            'license': med.get('license', ''),
                            'source': med.get('publisher', ''),
                            'description': med.get('description', ''),
                            'rightsHolder': med.get('rightsHolder', '')
                        })
        
        # Fallback to Wikipedia
        # TODO pour Nathanaël : intégrer une recherche d'image Wikipedia via l'API pour éviter de devoir faire du web scraping
        
        return images
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'image: {e}")
        return []
    
def get_species_locations(species_id: str, limit: int = 500) -> list:
    """GBIF occurrence lookup."""
    try:
        occ_url = f"https://api.gbif.org/v1/occurrence/search?taxonKey={species_id}&hasCoordinate=true&limit={limit}"
        occ_resp = requests.get(occ_url, timeout=15)
        occ_data = occ_resp.json()

        logger.debug(f"Occurrence URL: {occ_url}")
        
        logger.debug(f"Occ response status: {occ_resp.status_code}")
        logger.debug(f"Occ data count: {occ_data.get('count', 0)}")
        
        locations = []
        for item in occ_data.get("results", []):
            if "decimalLatitude" in item and "decimalLongitude" in item:
                locations.append((item["decimalLatitude"], item["decimalLongitude"]))
        
        return locations
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des occurrences: {e}")
        return []
    

if __name__ == "__main__":
    species_name = "Coccinella septempunctata"
    species_id = get_species_id(species_name)
    if species_id:
        species_info = get_species_info(species_id[0])
        logger.info(species_info)
        image_url = ""
        if "error" not in species_info:
            image_url = get_species_image(species_id[1], species_name)
        locations = get_species_locations(species_id[1])
        logger.debug(f"Locations found: {len(locations)}")
        from map_viewer import create_insect_map, open_map_in_browser
        map_path = create_insect_map(species_name, locations, "test_map.html")
        logger.debug(f"Map saved to: {map_path}")
        open_map_in_browser(species_name, locations)