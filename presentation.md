# Dossier Technique : Open Insect ID

## 1. Présentation Globale
**Open Insect ID** est une application desktop intelligente développée en Python dédiée à l'identification automatisée d'insectes. 

### Points clés
- Faciliter la reconnaissance des insectes pour les amateurs de nature.
- Utilisation d'un modèle d'apprentissage automatique (Deep Learning).
- Intégration de données scientifiques via l'API GBIF (*Global Biodiversity Information Facility*).

---

## 2. Architecture Technique

### Cœur du Système
- **Modèle IA Classifier** : Architecture **MobileNetV3** exportée au format **ONNX**.
- **Classification** : Approche taxonomique hiérarchique (Ordre > Famille > Genre > Espèce).
- **Interface Graphique** : Développée avec **CustomTkinter** pour une expérience utilisateur moderne et intuitive.

### Connectivité Mobile (Mobile Connect)
Pour pallier les limitations des frameworks Python sur mobile (Kivy, Flet), nous avons implémenté une solution hybride :
- **Serveur Backend** : API légère via **Flask** intégrée à l'application Desktop.
- **Interface Mobile** : PWA ou interface web accessible via **QR Code**, permettant l'envoi direct de photos depuis la caméra du smartphone vers l'ordinateur via le réseau local.

---

## 3. Organisation de l'Équipe

- **Yoann** : 
    - Préparation du dataset (nettoyage, filtrage iNaturalist 2021).
    - Entraînement et optimisation du modèle sur Kaggle (Data Augmentation).
    - Exportation et intégration du modèle ONNX.
- **Clovis & Lucas** : 
    - Conception de l'architecture logicielle Python.
    - Développement de l'interface graphique (GUI).
    - Intégration des APIs externes (GBIF, Wikipedia).
    - Implémentation du système de communication Flask/Mobile.

---

## 4. Étapes de Développement

1.  **Phase IA** : Filtrage du dataset iNaturalist (extraction des insectes uniquement) et itérations d'entraînement pour atteindre une précision de **77%**.
2.  **Prototypage** : Validation du moteur d'inférence ONNX via des scripts simplifiés.
3.  **Core Logic** : Développement des modules de preprocessing d'images et de configuration globale.
4.  **Enrichissement de Données** :
    - Abandon de la géolocalisation interne (trop lourde/imprécise).
    - Migration vers l'**API GBIF** pour des cartes de distribution dynamiques et précises.
    - Intégration de galeries visuelles et fiches Wikipedia.
5.  **Optimisation** : Correction de bugs, amélioration du temps de prédiction et polissage de l'interface (icônes, ergonomie).

---

En marge du programme NSI, une application native **Kotlin** a été développée par Clovis à des fins de tests comparatifs. Elle permet une exécution 100% locale du modèle sur Android, bien que les fonctionnalités d'enrichissement (cartes, biographie) restent pour l'instant l'exclusivité de la version Desktop.
