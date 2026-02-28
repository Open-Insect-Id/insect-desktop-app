# 🐞 Open Insect ID - Application Desktop

Une application desktop intelligente pour l'identification d'insectes utilisant l'intelligence artificielle, développée en Python avec Tkinter et CustomTkinter.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge)
![Tkinter](https://img.shields.io/badge/Tkinter-Included-orange?style=for-the-badge)
![License](https://img.shields.io/badge/License-GPLv3-green?style=for-the-badge)

## 📋 Description

Open Insect ID est une application desktop qui permet d'identifier les insectes à partir de photos en utilisant un modèle d'IA entraîné. L'application interroge l'API GBIF pour obtenir des informations détaillées sur les espèces identifiées, incluant leur classification taxonomique, des images et des données de distribution géographique.

## ✨ Fonctionnalités

- 🔍 **Identification automatique** : Upload d'images pour identification d'insectes
- 🌐 **Données GBIF** : Récupération d'informations scientifiques précises
- 🖼️ **Galerie d'images** : Affichage d'images de l'espèce depuis GBIF
- 📍 **Carte de distribution** : Visualisation des occurrences géographiques
- 📖 **Informations détaillées** : Nom scientifique, famille, genre, liens externes
- 🎨 **Interface moderne** : UI élégante avec CustomTkinter

## 🚀 Installation

### Prérequis

- Python 3.8 ou supérieur
- Tkinter (inclus dans la plupart des installations Python)

### Étapes d'installation

1. **Clonez le repository :**
   ```bash
   git clone https://github.com/Open-Insect-Id/insect-desktop-app.git
   cd insect-desktop-app
   ```

2. **Créez un environnement virtuel :**
   ```bash
   python -m venv .venv
   ```

3. **Activez l'environnement virtuel :**

      - Windows :
         ```bash
         .venv\Scripts\activate
         ```

      - Linux / MacOS :
         ```bash
         source .venv/bin/activate
         ```

4. **Installez les dépendances :**
   ```bash
   pip install -r requirements.txt
   ```

5. **Lancez l'application :**
   ```bash
   python main.py
   ```

## 📖 Utilisation

1. Ouvrez l'application
2. Cliquez sur "Charger une image" pour sélectionner une photo d'insecte
3. L'IA analyse l'image et propose une identification
4. Consultez les informations détaillées depuis GBIF :
   - Nom scientifique et classification
   - Images de référence
   - Carte de distribution mondiale
   - Liens vers des ressources externes

## 🛠️ Architecture

```
insect-desktop-app/
├── main.py              # Point d'entrée de l'application
├── gui.py               # Interface utilisateur principale
├── model.py             # Intégration du modèle IA
├── gbif_api.py          # API client pour GBIF
├── wikipedia_search.py  # Recherche d'informations Wikipedia
├── map_viewer.py        # Visualisation des cartes
├── config.py            # Configuration de l'application
├── logger.py            # Système de logging
├── preprocess.py        # Prétraitement des images
├── test_installation.py # Tests d'installation
├── model/               # Modèle IA entraîné
│   ├── hierarchy_labels.json
│   ├── hierarchy_map.json
│   └── insect_model.onnx
├── images/              # Ressources graphiques
├── logs/                # Fichiers de logs
└── requirements.txt     # Dépendances Python
```


## 🔧 Dépannage

### `ModuleNotFoundError: No module named 'tkinter'`

<details>

Si vous rencontrez cette erreur, tkinter n'est pas installé ou disponible dans votre environnement Python.

Tkinter fait partie de la bibliothèque standard Python, mais sur certains systèmes (surtout Linux), il peut ne pas être inclus par défaut.

#### Solutions :

1. **Installer tkinter au niveau système (Linux) :**
   - Ubuntu/Debian : `sudo apt-get install python3-tk`
   - Fedora : `sudo dnf install python3-tkinter`
   - Arch : `sudo pacman -S tk`

2. **Exécuter en dehors de VS Code Flatpak :**
   Si vous utilisez VS Code installé via Flatpak, tkinter peut ne pas être disponible à cause du sandboxing. La version Flatpak de VS Code utilise un environnement Python sandboxé qui n'inclut pas tkinter.
   - Installez VS Code nativement (pas via Flatpak) pour accéder au Python système avec tkinter.
   - Lancez l'app directement depuis un terminal hôte en dehors de VS Code (voir tutoriel détaillé ci-dessous).

3. **Utiliser le Python système :**
   Assurez-vous d'utiliser le Python système qui a tkinter. Vérifiez avec `python3 -c "import tkinter"`.

Après installation, recréez l'environnement virtuel si nécessaire.

#### Tutoriel détaillé : Exécution depuis un terminal externe sur Linux

Puisque le terminal dans VS Code Flatpak est sandboxé et n'a pas accès à tkinter, vous devez lancer l'app depuis votre terminal système natif. Suivez ces étapes :

1. **Ouvrez un terminal système :**
   - Appuyez sur `Ctrl + Alt + T` (fonctionne sur la plupart des distributions Linux comme Ubuntu, Fedora, etc.).
   - Ou cherchez "Terminal" ou "Console" dans le menu des applications.

2. **Naviguez vers le répertoire du projet :**
   - Utilisez `cd` pour aller dans le répertoire. Remplacez par votre chemin réel :
     ```
     cd /home/yoann/Documents/GitHub/insect-desktop-app
     ```
   - Confirmez avec `ls` que vous voyez `main.py` et `requirements.txt`.

3. **Activez l'environnement virtuel (si créé) :**
   - S'il y a un dossier `.venv`, activez-le :
     ```
     source .venv/bin/activate
     ```
   - Votre prompt devrait afficher `(.venv)` au début.

4. **Installez les dépendances (si pas fait) :**
   ```bash
   pip install -r requirements.txt
   ```

5. **Lancez l'application :**
   ```bash
   python main.py
   ```
   - La fenêtre GUI devrait s'ouvrir. Si l'erreur tkinter persiste, passez à l'étape suivante.

6. **Si tkinter manque toujours :**
   - Quittez l'environnement virtuel : `deactivate`
   - Installez tkinter sur le système (voir Solution 1).
   - Recréez l'environnement virtuel :
     ```
     rm -rf .venv
     python -m venv .venv
     source .venv/bin/activate
     pip install -r requirements.txt
     ```
   - Relancez `python main.py`.

Cette méthode exécute l'app dans l'environnement hôte, où tkinter et les bibliothèques GUI sont accessibles.
</details>

## 📄 Licence

Ce projet est sous licence GPLv3 — voir le fichier [LICENSE](LICENSE) pour plus de détails.
