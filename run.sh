#!/bin/bash
# Script de lancement pour Open Insect Identifier (Linux/Mac)
set -e

# Vérifier Python
if ! command -v python3 &> /dev/null; then
  echo "Python3 n'est pas installé. Veuillez l'installer."
  exit 1
fi

# Vérifier pip
if ! command -v pip3 &> /dev/null; then
  echo "pip3 n'est pas installé. Veuillez l'installer."
  exit 1
fi

# Vérifier les dépendances Python
if [ ! -f requirements.txt ]; then
  echo "requirements.txt introuvable !"
  exit 1
fi

pip3 install --user -r requirements.txt

# Lancer l'application
python3 main.py
