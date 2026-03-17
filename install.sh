#!/bin/bash
# Script d'installation pour Open Insect Identifier

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCÈS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[ATTENTION]${NC} $1"; }
print_error() { echo -e "${RED}[ERREUR]${NC} $1"; }

# 1. VÉRIFICATION DES PRÉREQUIS
print_info "Vérification des prérequis..."

if ! command -v python3 &> /dev/null; then
    print_error "Python3 n'est pas installé."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_success "Python $PYTHON_VERSION détecté"

if ! command -v pip3 &> /dev/null; then
    print_error "pip3 n'est pas installé."
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt introuvable !"
    exit 1
fi

# 2. ENVIRONNEMENT VIRTUEL (RECOMMANDÉ)
print_info "Configuration de l'environnement Python..."
VENV_DIR="venv"

read -p "Utiliser un environnement virtuel ? (recommandé) [O/n] " -n 1 -r
echo
if [[ $REPLY =~ ^[Oo]$ ]] || [[ -z $REPLY ]]; then
    if [ -d "$VENV_DIR" ]; then
        print_warning "Environnement virtuel existant."
    else
        python3 -m venv "$VENV_DIR"
        print_success "Environnement virtuel créé."
    fi
    source "$VENV_DIR/bin/activate"
    print_success "Environnement virtuel activé."
fi

# 3. INSTALLATION DES DÉPENDANCES
print_info "Installation des dépendances..."
pip3 install --upgrade pip
pip3 install -r requirements.txt
print_success "Dépendances installées."

# 4. INSTRUCTIONS DE LANCEMENT
echo
print_success "Installation terminée !"
echo
print_info "Pour lancer l'application :"
echo "  $ ./run.sh"
echo
print_info "Ou avec l'environnement virtuel :"
echo "  $ source venv/bin/activate"
echo "  $ python3 main.py"
echo

exit 0