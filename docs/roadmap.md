# Roadmap

---

## Légende

| Symbole | État |
| :--- | :--- |
| ✅ | Complété |
| ☑️ | En cours |
| ⏳ | En attente |
| 🆘 | Besoin d'aide |
| ❌ | Abandon |

---

## Modèle : Yoann

- [x] Téléchargement depuis le repo iNaturalist 2021
- [x] Préparation (gestion des performances avec `ijson`)
- [x] Filtrage pour ne conserver que les insectes
- [x] Upload sur Kaggle, solution gratuite similaire à Google Colab
- [x] Vérification des données sur Kaggle
- [x] Suppression des quelques fichiers corrompus par les interruptions pendant le transfert
- [x] Préparation des datasets (train/train-mini/val/public-test)
- [x] Extraction de la hiérarchie par ordre > famille > genre > espèce depuis les noms de dossiers
- [x] Application de transformation pour augmenter artificiellement la taille du dataset train
- [x] Construction d'un dictionnaire représentant la hiérarchie
- [x] Apprentissage de la théorie sur le finetune du modèle MobileNet v3
- [x] Entrainement sur le dataset train-mini
- [x] Entrainement sur le dataset train complet

---

## Application Android : Lucas / Clovis

### ❌ Tentative Application Python
Python n'est pas un langage pratique à utiliser pour réaliser des applications Android. Nous avons exploré plusieurs pistes :

- **Flet** : un module Python pour convertir du Python en Dart avec Flutter. Ne supporte pas l'accès caméra.
- **Kivy** : un module Python qui semble compliqué à prendre en main. Problèmes de compatibilité avec les versions récentes d'Android.
- **PWA (Progressive Web App)** : Approche alternative avec accès à la caméra via le navigateur web du téléphone.

### État d'avancement
- [x] **Solution de secours** : Création d'une appli de test en Kotlin par Clovis.
- [x] Gestion de la caméra
- [x] Gestion de la galerie
- [ ] Export vers un ordinateur
- [ ] Transfert

---

## Application Desktop : Lucas / Clovis / Yoann

- [x] Création d'une appli avec **CustomTkinter**
- [x] Création d'une **API** pour permettre la communication entre l'ordinateur et le téléphone
- [x] Gérer le modèle (utilisation avec `onnx-runtime`)
- [x] Interface permettant une interaction avec le modèle de reconnaissance d'insectes
- [x] Carte du monde permettant la visualisation graphique du dataset, avec un marqueur par image
- [x] Biographie Wikipédia de l'espèce/famille
- [x] Informations détaillées fournies par **GBIF API**
- [x] Galerie pour comparaison visuelle avec l'espèce prédite par le modèle
