import requests

def get_species_info(species_name: str) -> dict:
    """GBIF lookup."""
    try:
        search_url = "https://api.gbif.org/v1/species/search?q=" + species_name.replace(" ", "+")
        resp = requests.get(search_url, headers={'User-Agent': 'Insect-ID/1.0'}, timeout=5)
        if resp.status_code != 200 or not resp.json()['results']:
            return {"error": "Aucune espèce trouvée"}
        
        species_id = resp.json()['results'][0]['key']
        detail_url = f"https://api.gbif.org/v1/species/{species_id}"
        detail_resp = requests.get(detail_url, headers={'User-Agent': 'Insect-ID/1.0'}, timeout=5)
        data = detail_resp.json()
        
        return {
            "nom": data.get("scientificName", species_name),
            "famille": data.get("family", ""),
            "genre": data.get("genus", ""),
            "url": f"https://www.gbif.org/species/{species_id}"
        }
    except Exception as e:
        return {"error": f"API erreur: {e}"}
    


def get_species_image(species_id: str) -> str:
    """GBIF media lookup."""
    try:
        media_url = f"https://api.gbif.org/v1/species/{species_id}/media"
        media_resp = requests.get(media_url, headers={'User-Agent': 'Insect-ID/1.0'}, timeout=5)
        media_data = media_resp.json()
        
        for item in media_data.get("results", []):
            if item.get("type") == "StillImage" and item.get("identifier"):
                return item["identifier"]
        
        return ""
    except Exception as e:
        return ""