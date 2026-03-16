# 🐞 Open Insect ID - Application Desktop

Une application desktop intelligente pour l'identification d'insectes utilisant l'intelligence artificielle, développée en Python avec Tkinter et CustomTkinter.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge)
![License](https://img.shields.io/badge/License-GPLv3-green?style=for-the-badge)

## 📋 Description

Open Insect ID est une application desktop qui permet d'identifier les insectes à partir de photos en utilisant un modèle d'IA entraîné par nos soins. L'application interroge l'API GBIF pour obtenir des informations détaillées sur les espèces identifiées, incluant leur classification taxonomique, des images et des données de distribution géographique.

## ✨ Fonctionnalités

- 🔍 **Identification automatique** : Upload d'images pour identification d'insectes
- 🎯 **Centrage automatique** : Détecte l'objet principal de l'image pour se focus dessus
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

## 📄 Licence

Ce projet est sous licence GPLv3 — voir le fichier [LICENSE](LICENSE) pour plus de détails.
