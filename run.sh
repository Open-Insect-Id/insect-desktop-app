#!/bin/bash
# Script de lancement pour Open Insect Identifier (Linux/Mac)
set -e

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCÈS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[ATTENTION]${NC} $1"; }
print_error() { echo -e "${RED}[ERREUR]${NC} $1"; }

# Vérifier Python
if ! command -v python3 &> /dev/null; then
  print_error "Python3 n'est pas installé. Veuillez l'installer."
  exit 1
fi

# Vérifier requirements.txt
if [ ! -f requirements.txt ]; then
  print_error "requirements.txt introuvable !"
  exit 1
fi

# Installer les dépendances
print_info "Installation des dépendances..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
print_success "Dépendances installées."

# Lancer l'application
print_info "Lancement de l'application..."
python3 main.py
