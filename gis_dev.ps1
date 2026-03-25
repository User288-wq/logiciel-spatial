# ============================================================================
# SPATIAL GIS - ENVIRONNEMENT DE DÉVELOPPEMENT INTERACTIF
# ============================================================================

Write-Host @"
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    🌍 SPATIAL GIS - DEV INTERACTIF                            ║
║                         Mode Développement                                    ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

Write-Host @"
Commandes disponibles:
  py          - Lancer Python interactif avec les libs GIS chargées
  run         - Lancer le logiciel spatial complet
  test        - Tester une fonction spécifique
  edit        - Ouvrir le code pour édition
  log         - Voir les logs
  clear       - Nettoyer l'écran
  help        - Cette aide
  exit        - Quitter

"@ -ForegroundColor Yellow

function Start-PythonInteractive {
    Write-Host "`n🐍 Lancement de Python avec les librairies GIS..." -ForegroundColor Green
    Write-Host "Tapez votre code Python. Les librairies sont déjà importées." -ForegroundColor DarkGray
    Write-Host "Pour quitter Python, tapez: exit() ou Ctrl+D`n" -ForegroundColor DarkGray
    
    python -c @"
import sys
import os
import warnings
warnings.filterwarnings('ignore')

# Import des librairies GIS
print("📦 Chargement des librairies...")
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from shapely.geometry import Point, LineString, Polygon, box
from shapely.ops import unary_union

print(f"✅ Geopandas: {gpd.__version__}")
print(f"✅ Matplotlib: {plt.__version__}")
print(f"✅ Numpy: {np.__version__}")
print("")
print("✨ Fonctions utiles disponibles:")
print("   info_layer(gdf)     - Affiche les infos d'une couche")
print("   display_map(gdf)    - Affiche une carte")
print("   create_sample()     - Crée des données d'exemple")
print("")

# Définir les fonctions utiles
def info_layer(gdf):
    '''Affiche les informations d'une couche'''
    print(f"Type: {type(gdf)}")
    print(f"CRS: {gdf.crs}")
    print(f"Nombre d'entités: {len(gdf)}")
    print(f"Colonnes: {list(gdf.columns)}")
    if len(gdf) > 0:
        print(f"Étendue: {gdf.total_bounds}")
    return gdf

def display_map(gdf, title="Carte", column=None):
    '''Affiche une carte'''
    fig, ax = plt.subplots(figsize=(12, 8))
    if column and column in gdf.columns:
        gdf.plot(ax=ax, column=column, cmap='viridis', legend=True, edgecolor='black')
    else:
        gdf.plot(ax=ax, edgecolor='black', alpha=0.7)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
    return fig

def create_sample():
    '''Crée des données d'exemple'''
    villes = gpd.GeoDataFrame({
        'name': ['Paris', 'Lyon', 'Marseille', 'Toulouse', 'Bordeaux', 'Nantes'],
        'population': [2148000, 515000, 863000, 479000, 256000, 318000],
        'region': ['IDF', 'ARA', 'PACA', 'OCC', 'NAQ', 'PDL'],
        'geometry': [
            Point(2.35, 48.86),
            Point(4.84, 45.76),
            Point(5.38, 43.30),
            Point(1.44, 43.60),
            Point(-0.58, 44.84),
            Point(-1.55, 47.22)
        ]
    }, crs='EPSG:4326')
    print(f"✅ {len(villes)} villes créées")
    return villes

# Variable globale
gdf = None
print("💡 Astuce: gdf = create_sample() pour créer des données test")
print("")

# Lancer le shell interactif
import code
code.interact(local=locals())
"@
}

function Start-SpatialGIS {
    Write-Host "`n🚀 Lancement du logiciel spatial..." -ForegroundColor Green
    cd python
    python spatial_gis_ultimate.py
    cd ..
}

function Test-Function {
    Write-Host "`n🧪 Test rapide..." -ForegroundColor Yellow
    
    python -c @"
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point

print("Création des données test...")
villes = gpd.GeoDataFrame({
    'name': ['Paris', 'Lyon', 'Marseille'],
    'geometry': [Point(2.35, 48.86), Point(4.84, 45.76), Point(5.38, 43.30)]
}, crs='EPSG:4326')

print(f"✓ {len(villes)} villes créées")
print(villes)

print("\nCréation de la carte...")
fig, ax = plt.subplots(figsize=(10, 8))
villes.plot(ax=ax, color='red', markersize=100, edgecolor='white')

for idx, row in villes.iterrows():
    ax.annotate(row['name'], xy=row.geometry.coords[0],
                xytext=(5, 5), textcoords='offset points',
                color='white', fontsize=10, fontweight='bold')

ax.set_title('Test - Villes de France', fontsize=14)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

print("✅ Test réussi !")
"@
}

function Edit-Code {
    Write-Host "`n📝 Édition du code..." -ForegroundColor Green
    code python/spatial_gis_ultimate.py
}

function Show-Logs {
    $logFile = "$env:USERPROFILE\.spatial_gis\logs\spatial_gis_*.log"
    $latestLog = Get-ChildItem $logFile | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($latestLog) {
        Write-Host "`n📋 Dernier log: $($latestLog.Name)" -ForegroundColor Cyan
        Get-Content $latestLog -Tail 30
    } else {
        Write-Host "Aucun log trouvé" -ForegroundColor Yellow
    }
}

# Boucle interactive
while ($true) {
    $cmd = Read-Host "`n[GIS DEV] >> "
    
    switch ($cmd.ToLower()) {
        "py" { Start-PythonInteractive }
        "run" { Start-SpatialGIS }
        "test" { Test-Function }
        "edit" { Edit-Code }
        "log" { Show-Logs }
        "clear" { Clear-Host; Write-Host "✅ Écran nettoyé" -ForegroundColor Green }
        "help" { 
            Clear-Host
            Write-Host @"
╔═══════════════════════════════════════════════════════════════════════════════╗
║                              AIDE - COMMANDES                                 ║
╚═══════════════════════════════════════════════════════════════════════════════╝

  py      - Lance Python interactif avec les librairies GIS pré-chargées
  run     - Lance le logiciel spatial complet (interface QT)
  test    - Exécute un test rapide avec une carte
  edit    - Ouvre le code source dans VS Code
  log     - Affiche les derniers logs
  clear   - Nettoie l'écran
  help    - Affiche cette aide
  exit    - Quitte l'environnement

FONCTIONS DISPONIBLES DANS PYTHON:
────────────────────────────────────────────────────────────────────────────────
  info_layer(gdf)  - Affiche les infos d'une couche
  display_map(gdf) - Affiche une carte
  create_sample()  - Crée des données d'exemple

"@ -ForegroundColor Cyan
        }
        "exit" { 
            Write-Host "`n👋 Au revoir !" -ForegroundColor Green
            break 
        }
        "q" { 
            Write-Host "`n👋 Au revoir !" -ForegroundColor Green
            break 
        }
        default {
            if ($cmd) {
                Write-Host "❌ Commande inconnue: $cmd. Tapez 'help' pour la liste." -ForegroundColor Red
            }
        }
    }
}
