# Problèmes courants

## ModuleNotFoundError: No module named 'tkinter'

Il est impossible de lancer correctement l'application depuis un IDE installé via Flatpak (comme VSCode Flatpak sous Linux). En effet, ces versions sandboxées n'ont pas accès à certains modules système comme `tkinter` ou à l'environnement graphique complet, ce qui empêche l'exécution des applications graphiques Python. Pour utiliser ce projet, il est recommandé d'utiliser VSCode installé via un paquet natif (deb, rpm, etc.) ou d'exécuter les scripts directement depuis un terminal hors sandbox.

## ModuleNotFoundError: No module named 'PIL'

Cette erreur indique que la bibliothèque Pillow (PIL) n'est pas installée. Installez-la avec :

    pip install pillow

## ModuleNotFoundError: No module named 'customtkinter'

L'interface utilise la bibliothèque customtkinter. Installez-la avec :

    pip install customtkinter

## ModuleNotFoundError: No module named 'onnxruntime'

Le modèle d'insectes nécessite onnxruntime. Installez-le avec :

    pip install onnxruntime

## ImportError: libGL.so.1: cannot open shared object file

Il manque une bibliothèque système pour l'affichage d'images. Sous Ubuntu/Debian, installez-la avec :

    sudo apt install libgl1

## UnicodeDecodeError lors de l'ouverture d'une image

Cela peut arriver si le chemin du fichier contient des caractères spéciaux non supportés. Essayez de déplacer l'image dans un dossier avec un nom simple (sans accents ni caractères spéciaux).

## PermissionError lors de l'accès à un fichier

Vérifiez que vous avez les droits de lecture/écriture sur le fichier ou le dossier concerné.