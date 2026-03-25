import re
import sys
from pathlib import Path

def clean_text(text):
    # Table de remplacement des accents
    accents = {
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'à': 'a', 'â': 'a', 'ä': 'a',
        'ù': 'u', 'û': 'u', 'ü': 'u',
        'ô': 'o', 'ö': 'o',
        'î': 'i', 'ï': 'i',
        'ç': 'c',
        'œ': 'oe', 'æ': 'ae',
        'É': 'E', 'È': 'E', 'Ê': 'E', 'Ë': 'E',
        'À': 'A', 'Â': 'A', 'Ä': 'A',
        'Ù': 'U', 'Û': 'U', 'Ü': 'U',
        'Ô': 'O', 'Ö': 'O',
        'Î': 'I', 'Ï': 'I',
        'Ç': 'C',
    }
    for acc, ascii_ in accents.items():
        text = text.replace(acc, ascii_)
    
    # Remplacer les emojis
    emojis = {
        '🚀': '(fusee)',
        '🗺️': '(carte)',
        '📂': '(dossier)',
        '💾': '(disquette)',
        '🔍': '(loupe)',
        '📏': '(regle)',
        '📋': '(presse-papiers)',
        '🛰️': '(satellite)',
        '🌍': '(terre)',
        '✅': '(OK)',
        '❌': '(erreur)',
        '🪐': '(planete)',
        '🔲': '(carre)',
        '📊': '(graphique)',
        '📈': '(stats)',
        '📉': '(courbe)',
        '📍': '(pointeur)',
        '🕐': '(heure)',
    }
    for emoji, rep in emojis.items():
        text = text.replace(emoji, rep)
    
    return text

input_file = Path("spatial_gis_ultimate.py")
output_file = Path("spatial_gis_ultimate_ascii.py")

if not input_file.exists():
    print(f"Fichier {input_file} introuvable.")
    sys.exit(1)

# Lire le fichier source avec l'encodage UTF-8
with open(input_file, 'r', encoding='utf-8') as f:
    content = f.read()

cleaned = clean_text(content)

# Écrire le fichier de sortie en ASCII strict (les caractères non ASCII seront transformés)
with open(output_file, 'w', encoding='ascii') as f:
    f.write(cleaned)

print(f"Fichier ASCII généré : {output_file}")
