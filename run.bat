@echo off
REM Script de lancement pour Open Insect Identifier (Windows)

where python >nul 2>nul
if errorlevel 1 (
    echo Python n'est pas installe. Veuillez l'installer.
    exit /b 1
)

where pip >nul 2>nul
if errorlevel 1 (
    echo pip n'est pas installe. Veuillez l'installer.
    exit /b 1
)

if not exist requirements.txt (
    echo requirements.txt introuvable !
    exit /b 1
)

pip install --user -r requirements.txt

python sources/main.py
