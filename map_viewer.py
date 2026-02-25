"""
Module pour afficher les cartes géographiques des observations d'insectes.
"""
import folium
import webbrowser
from pathlib import Path
import tempfile


def create_insect_map(species_name: str, coordinates: list, output_path: str = None):
    """
    Crée une carte interactive avec les observations d'une espèce d'insecte.
    
    Args:
        species_name: Nom de l'espèce (ex: "Andrena virginalis")
        coordinates: Liste de coordonnées [[lat, lon], [lat, lon], ...]
        output_path: Chemin pour sauvegarder la carte HTML (optionnel)
    
    Returns:
        str: Chemin du fichier HTML créé
    """
    if not coordinates or len(coordinates) == 0:
        return None
    
    # Calculer le centre de la carte (moyenne des coordonnées)
    avg_lat = sum(coord[0] for coord in coordinates) / len(coordinates)
    avg_lon = sum(coord[1] for coord in coordinates) / len(coordinates)
    
    # Créer la carte centrée sur la moyenne
    m = folium.Map(
        location=[avg_lat, avg_lon],
        zoom_start=6,
        tiles='OpenStreetMap'
    )
    
    # Ajouter un marqueur pour chaque observation
    for lat, lon in coordinates:
        folium.CircleMarker(
            location=[lat, lon],
            radius=5,
            popup=f"{species_name}<br>Lat: {lat:.5f}<br>Lon: {lon:.5f}",
            color='#3388ff',
            fill=True,
            fillColor='#3388ff',
            fillOpacity=0.6
        ).add_to(m)
    
    # Ajouter un truc style map chaleur si beaucoup de points
    if len(coordinates) > 50:
        from folium.plugins import HeatMap
        HeatMap(coordinates, radius=15, blur=25, max_zoom=13).add_to(m)
    
    # Sauvegarder la carte
    if output_path is None:
        # Créer un fichier temporaire
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8')
        output_path = temp_file.name
        temp_file.close()
    
    m.save(output_path)
    return output_path


def open_map_in_browser(species_name: str, coordinates: list):
    """
    Crée et ouvre une carte dans le navigateur web.
    
    Args:
        species_name: Nom de l'espèce
        coordinates: Liste de coordonnées [[lat, lon], [lat, lon], ...]
    """
    if not coordinates or len(coordinates) == 0:
        print(f"Aucune donnée géographique disponible pour {species_name}")
        return
    
    try:
        map_path = create_insect_map(species_name, coordinates)
        if map_path:
            webbrowser.open('file://' + map_path)
            print(f"Carte ouverte pour {species_name} ({len(coordinates)} observations)")
    except Exception as e:
        print(f"Erreur lors de l'ouverture de la carte: {e}")
