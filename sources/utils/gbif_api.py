import requests
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from random import sample

from utils.logger import setup_logger

logger = setup_logger(__name__)


def get_species_id(species_name: str) -> tuple[str, str]:
    """GBIF search for species ID. Returns (usageKey, nubKey)."""
    logger.info(f"Recherche GBIF pour l'espèce: {species_name}")
    try:
        search_url = f"https://api.gbif.org/v1/species/match?name={species_name.replace(' ', '+')}"
        resp = requests.get(search_url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            # Ensure data is a dict before accessing keys
            if not isinstance(data, dict):
                logger.warning(f"Réponse GBIF inattendue (non-dict): {type(data)}")
                return "", ""
            usage_key = data.get("usageKey", "")
            nub_key = data.get("nubKey", usage_key)
            # Convert to string, handling None and numeric types
            usage_key = str(usage_key) if usage_key is not None else ""
            nub_key = str(nub_key) if nub_key is not None else ""
            logger.info(f"GBIF IDs trouvés: usageKey={usage_key}, nubKey={nub_key}")
            return usage_key, nub_key
        logger.warning(f"GBIF a retourné status {resp.status_code}")
        return "", ""
    except Exception as e:
        logger.error(f"Erreur lors de la recherche de l'espèce: {e}")
        return "", ""


def get_species_info(species_id: str) -> dict:
    """GBIF lookup."""
    logger.info(f"Récupération des informations GBIF pour species_id: {species_id}")
    try:
        detail_url = f"https://api.gbif.org/v1/species/{species_id}"
        detail_resp = requests.get(detail_url, timeout=10)
        data = detail_resp.json()

        # Ensure data is a dict before accessing keys
        if not isinstance(data, dict):
            logger.warning(f"Réponse GBIF info inattendue (non-dict): {type(data)}")
            return {"error": "Invalid response format from GBIF API"}

        result = {
            "nom": data.get("scientificName", ""),
            "famille": data.get("family", ""),
            "genre": data.get("genus", ""),
            "url": f"https://www.gbif.org/species/{species_id}",
        }
        logger.info(f"Informations GBIF: {result}")
        return result
    except Exception as e:
        logger.error(f"API erreur: {e}")
        return {"error": f"API erreur: {e}"}


def get_species_image(species_id: str, limit: int = 10) -> list:
    """GBIF media lookup from iNaturalist observations for better relevance."""
    logger.info(
        f"Récupération des images pour species_id: {species_id} (limit={limit})"
    )
    images = []
    try:
        media_url = f"https://api.gbif.org/v1/occurrence/search?taxonKey={species_id}&mediaType=StillImage&limit={limit}"
        media_resp = requests.get(media_url, timeout=10)
        media_data = media_resp.json()

        # Ensure media_data is a dict with 'results' key
        if isinstance(media_data, dict):
            results = media_data.get("results", [])
        else:
            # If response is not a dict, treat as empty results
            results = []

        for item in results:
            if isinstance(item, dict) and "media" in item:
                for med in item["media"]:
                    if isinstance(med, dict) and med.get("identifier"):
                        images.append(med.get("identifier"))
        logger.info(f"{len(images)} images trouvées")
        return images
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'image: {e}")
        return []


def get_species_locations(species_id: str, count: int = 300) -> list:
    """GBIF occurrence lookup with parallel requests for faster loading."""
    try:
        logger.info(
            f"Chargement des localisations pour species_id={species_id}, count={count}"
        )
        locations = []
        limit_per_page = 300
        num_pages = (count + limit_per_page - 1) // limit_per_page
        logger.info(f"Nombre de pages à charger: {num_pages}")

        def fetch_page(offset):
            occ_url = f"https://api.gbif.org/v1/occurrence/search?taxonKey={species_id}&hasCoordinate=true&limit={limit_per_page}&offset={offset}"
            try:
                logger.debug(f"Chargement page offset={offset}")
                occ_resp = requests.get(occ_url, timeout=15)
                if occ_resp.status_code == 200:
                    data = occ_resp.json()
                    page_locations = []
                    # Ensure data is a dict before accessing 'results'
                    if isinstance(data, dict):
                        results = data.get("results", [])
                    else:
                        results = []
                    for item in results:
                        if (
                            isinstance(item, dict)
                            and "decimalLatitude" in item
                            and "decimalLongitude" in item
                        ):
                            page_locations.append(
                                (item["decimalLatitude"], item["decimalLongitude"])
                            )
                    logger.debug(
                        f"Page offset={offset}: {len(page_locations)} localisations"
                    )
                    return page_locations
                else:
                    logger.warning(
                        f"Page offset={offset}: status {occ_resp.status_code}"
                    )
            except Exception as e:
                logger.error(f"Error fetching page at offset {offset}: {e}")
            return []

        # Générer tous les offsets
        offsets = [i * limit_per_page for i in range(num_pages)]

        # Utiliser ThreadPoolExecutor pour les requêtes parallèles
        max_workers = min(5, num_pages)  # Limiter à 5 workers max
        logger.info(f"Utilisation de {max_workers} workers parallèles")
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Soumettre toutes les tâches
            future_to_offset = {
                executor.submit(fetch_page, offset): offset for offset in offsets
            }

            # Récupérer les résultats au fur et à mesure
            completed = 0
            for future in as_completed(future_to_offset):
                page_locs = future.result()
                locations.extend(page_locs)
                completed += 1
                logger.debug(
                    f"Tâches complétées: {completed}/{num_pages}, total localisations: {len(locations)}"
                )
                if len(locations) >= count:
                    # Annuler les tâches restantes si on a atteint le count
                    cancelled = 0
                    for f in future_to_offset:
                        if not f.done():
                            f.cancel()
                            cancelled += 1
                    logger.info(f"Objectif atteint, {cancelled} tâches annulées")
                    break

        final_count = len(locations)
        logger.info(f"Chargement terminé: {final_count} localisations récupérées")
        return locations[:count]  # Limiter exactement au count demandé
    except Exception as e:
        logger.error(
            f"Erreur lors de la récupération des occurrences: {e}", exc_info=True
        )
        return []
