# ============================================================================
# INTERACTIVE GIS DEV ENVIRONMENT - VS CODE VERSION
# ============================================================================

# Configuration
$script:WorkspacePath = "C:\Users\User\OneDrive\Desktop\logiciel_spatial\python"
$script:HistoryFile = "$WorkspacePath\.dev_history.json"
$script:CurrentCell = 0
$script:Cells = @()
$script:Running = $true
$script:OutputMode = "compact"

# ============================================================================
# FONCTIONS
# ============================================================================

function Show-DevInterface {
    Clear-Host
    Write-Host @"
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    🚀 SPATIAL GIS - DEV INTERACTIVE                           ║
║                         (VS Code Edition)                                     ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan
    
    Write-Host @"
┌─ Commands ────────────────────────────────────────────────────────────────────┐
│  run      - Exécuter cellule courante                                        │
│  new      - Créer nouvelle cellule                                           │
│  edit     - Éditer cellule courante                                          │
│  up       - Déplacer cellule vers le haut                                    │
│  down     - Déplacer cellule vers le bas                                     │
│  clear    - Effacer la sortie de la cellule                                  │
│  snippet  - Insérer un snippet                                               │
│  save     - Sauvegarder le workspace                                         │
│  load     - Charger le workspace                                             │
│  list     - Lister les cellules                                              │
│  help     - Afficher l'aide                                                  │
│  quit     - Quitter                                                          │
└────────────────────────────────────────────────────────────────────────────────┘
"@ -ForegroundColor Yellow
    
    Write-Host ""
    Write-Host "📊 État: $($script:Cells.Count) cellules | Cellule courante: $($script:CurrentCell+1)" -ForegroundColor Green
    Write-Host ""
    
    if ($script:Cells.Count -gt 0) {
        $cell = $script:Cells[$script:CurrentCell]
        Display-CellPreview -Cell $cell -Index $script:CurrentCell
    } else {
        Write-Host "Aucune cellule. Tapez 'new' pour créer une cellule." -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host ">>> " -ForegroundColor Cyan -NoNewline
}

function Display-CellPreview {
    param(
        [PSCustomObject]$Cell,
        [int]$Index
    )
    
    $borderColor = "Green"
    
    Write-Host "┌─ Cell $($Index+1) ────────────────────────────────────────────────────────────────" -ForegroundColor $borderColor
    
    $lines = $Cell.Content -split "`r`n|`n"
    $maxLines = 8
    $lineCount = 0
    
    foreach ($line in $lines) {
        if ($lineCount -ge $maxLines) {
            Write-Host "│ ..." -ForegroundColor $borderColor
            break
        }
        $displayLine = if ($line.Length -gt 80) { $line.Substring(0, 77) + "..." } else { $line }
        Write-Host "│ " -NoNewline -ForegroundColor $borderColor
        Write-Host $displayLine -ForegroundColor White
        $lineCount++
    }
    
    if ($Cell.Output) {
        Write-Host "├─ Output ────────────────────────────────────────────────────────────────────" -ForegroundColor $borderColor
        $outputLines = $Cell.Output -split "`r`n|`n"
        foreach ($line in $outputLines[0..4]) {
            $displayLine = if ($line.Length -gt 80) { $line.Substring(0, 77) + "..." } else { $line }
            Write-Host "│ " -NoNewline -ForegroundColor $borderColor
            Write-Host $displayLine -ForegroundColor Cyan
        }
    }
    
    if ($Cell.Error) {
        Write-Host "├─ Error ─────────────────────────────────────────────────────────────────────" -ForegroundColor Red
        $errorLines = $Cell.Error -split "`r`n|`n"
        foreach ($line in $errorLines[0..2]) {
            Write-Host "│ " -NoNewline -ForegroundColor Red
            Write-Host $line -ForegroundColor Red
        }
    }
    
    Write-Host "└────────────────────────────────────────────────────────────────────────────────────" -ForegroundColor $borderColor
}

function New-Cell {
    param(
        [string]$Content = "# Nouvelle cellule`n`n# Écrivez votre code ici`n",
        [int]$Position = $script:CurrentCell + 1
    )
    
    $newCell = [PSCustomObject]@{
        Content = $Content
        Output = $null
        Error = $null
    }
    
    if ($Position -ge $script:Cells.Count) {
        $script:Cells += $newCell
    } else {
        $script:Cells = $script:Cells[0..$Position] + @($newCell) + $script:Cells[($Position+1)..($script:Cells.Count-1)]
    }
    $script:CurrentCell = $Position
    Write-Host "✓ Nouvelle cellule créée" -ForegroundColor Green
    Start-Sleep -Milliseconds 500
    Show-DevInterface
}

function Edit-CurrentCell {
    $cell = $script:Cells[$script:CurrentCell]
    
    Write-Host "`n✏️ Édition de la cellule $($script:CurrentCell+1)" -ForegroundColor Yellow
    Write-Host "Tapez votre code (tapez '---' sur une ligne vide pour terminer):`n" -ForegroundColor DarkGray
    
    $lines = @()
    while ($true) {
        $line = Read-Host
        if ($line -eq "---") { break }
        $lines += $line
    }
    
    if ($lines.Count -gt 0) {
        $newContent = $lines -join "`n"
        $cell.Content = $newContent
        Write-Host "✓ Cellule mise à jour" -ForegroundColor Green
    }
    
    Start-Sleep -Milliseconds 500
    Show-DevInterface
}

function Run-CurrentCell {
    $cell = $script:Cells[$script:CurrentCell]
    
    Write-Host "`n⚙️ Exécution de la cellule $($script:CurrentCell+1)..." -ForegroundColor Yellow
    Write-Host "----------------------------------------" -ForegroundColor DarkGray
    
    $tempFile = [System.IO.Path]::GetTempFileName() + ".py"
    
    $commonImports = @"
import sys
import os
import io
import pandas as pd
import numpy as np

try:
    import geopandas as gpd
    import matplotlib.pyplot as plt
    from shapely.geometry import Point, LineString, Polygon
    import warnings
    warnings.filterwarnings('ignore')
    
    plt.style.use('dark_background')
    plt.rcParams['figure.figsize'] = (12, 8)
    
    def info_layer(gdf):
        print(f"Type: {type(gdf)}")
        print(f"CRS: {gdf.crs}")
        print(f"Entités: {len(gdf)}")
        print(f"Colonnes: {list(gdf.columns)}")
        return gdf
    
    def display_map(gdf, title="Carte"):
        if hasattr(gdf, 'plot'):
            fig, ax = plt.subplots(figsize=(12, 8))
            gdf.plot(ax=ax, edgecolor='black', alpha=0.7)
            ax.set_title(title)
            ax.grid(True, alpha=0.3)
            plt.show()
        return gdf
    
    print("✓ Bibliothèques chargées")
    
except ImportError as e:
    print(f"⚠️ Erreur: {e}")
    print("pip install geopandas matplotlib shapely")

"@
    
    $fullCode = @"
import sys
import io
from contextlib import redirect_stdout, redirect_stderr

stdout_capture = io.StringIO()
stderr_capture = io.StringIO()

try:
    with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
        exec("""$($commonImports -replace '"', '\"')
        
# === CODE UTILISATEUR ===
$($cell.Content -replace '"', '\"')
""")
    output = stdout_capture.getvalue()
    error = stderr_capture.getvalue()
except Exception as e:
    output = stdout_capture.getvalue()
    error = f"{stderr_capture.getvalue()}\nErreur: {str(e)}"

print("=== RÉSULTAT ===")
if output:
    print(output)
if error:
    print("=== ERREUR ===")
    print(error)
"@
    
    $fullCode | Out-File -FilePath $tempFile -Encoding UTF8
    
    $output = & python $tempFile 2>&1
    $outputText = $output -join "`n"
    
    if ($outputText -match "=== RÉSULTAT ===\n(.*?)(?:\n=== ERREUR ===|$)") {
        $cell.Output = $matches[1].Trim()
    } else {
        $cell.Output = $outputText
    }
    
    if ($outputText -match "=== ERREUR ===\n(.*?)$") {
        $cell.Error = $matches[1].Trim()
    } else {
        $cell.Error = $null
    }
    
    Write-Host ""
    if ($cell.Output) { Write-Host $cell.Output -ForegroundColor Green }
    if ($cell.Error) { Write-Host $cell.Error -ForegroundColor Red }
    
    Remove-Item $tempFile -Force
    
    Write-Host ""
    Write-Host "----------------------------------------" -ForegroundColor DarkGray
    Write-Host "✓ Exécution terminée" -ForegroundColor Green
    Write-Host ""
    Write-Host "Appuyez sur Entrée pour continuer..." -ForegroundColor DarkGray
    Read-Host
    Show-DevInterface
}

function Save-Workspace {
    $data = @{
        Cells = @()
        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        CurrentCell = $script:CurrentCell
    }
    
    foreach ($cell in $script:Cells) {
        $data.Cells += @{
            Content = $cell.Content
            Output = $cell.Output
            Error = $cell.Error
        }
    }
    
    try {
        $data | ConvertTo-Json -Depth 10 | Out-File -FilePath $script:HistoryFile -Encoding UTF8
        Write-Host "✓ Workspace sauvegardé" -ForegroundColor Green
    } catch {
        Write-Host "✗ Erreur: $_" -ForegroundColor Red
    }
    
    Start-Sleep -Milliseconds 1000
    Show-DevInterface
}

function Load-Workspace {
    if (Test-Path $script:HistoryFile) {
        try {
            $data = Get-Content $script:HistoryFile -Raw | ConvertFrom-Json
            $script:Cells = @()
            foreach ($cell in $data.Cells) {
                $script:Cells += [PSCustomObject]@{
                    Content = $cell.Content
                    Output = $cell.Output
                    Error = $cell.Error
                }
            }
            $script:CurrentCell = if ($data.CurrentCell) { $data.CurrentCell } else { 0 }
            Write-Host "✓ Workspace chargé: $($script:Cells.Count) cellules" -ForegroundColor Green
        } catch {
            Write-Host "✗ Erreur, création nouveau workspace" -ForegroundColor Red
            Initialize-Workspace
        }
    } else {
        Initialize-Workspace
    }
}

function Initialize-Workspace {
    $script:Cells = @(
        [PSCustomObject]@{
            Content = @"
# Cellule 1: Test des librairies

import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point

print(f'Geopandas: {gpd.__version__}')
print(f'Matplotlib: {plt.__version__}')

p = Point(2.35, 48.86)
print(f'Point: {p}')

print('✅ Tout fonctionne!')
"@
            Output = $null
            Error = $null
        },
        [PSCustomObject]@{
            Content = @"
# Cellule 2: Créer des données

villes = gpd.GeoDataFrame({
    'name': ['Paris', 'Lyon', 'Marseille'],
    'geometry': [
        Point(2.35, 48.86),
        Point(4.84, 45.76),
        Point(5.38, 43.30)
    ]
}, crs='EPSG:4326')

print(f"✓ {len(villes)} villes")
print(villes)
info_layer(villes)
"@
            Output = $null
            Error = $null
        }
    )
    $script:CurrentCell = 0
}

function Move-CellUp {
    if ($script:CurrentCell -gt 0) {
        $temp = $script:Cells[$script:CurrentCell]
        $script:Cells[$script:CurrentCell] = $script:Cells[$script:CurrentCell - 1]
        $script:Cells[$script:CurrentCell - 1] = $temp
        $script:CurrentCell--
        Write-Host "✓ Cellule déplacée vers le haut" -ForegroundColor Green
    } else {
        Write-Host "✗ Déjà en haut" -ForegroundColor Yellow
    }
    Start-Sleep -Milliseconds 500
    Show-DevInterface
}

function Move-CellDown {
    if ($script:CurrentCell -lt $script:Cells.Count - 1) {
        $temp = $script:Cells[$script:CurrentCell]
        $script:Cells[$script:CurrentCell] = $script:Cells[$script:CurrentCell + 1]
        $script:Cells[$script:CurrentCell + 1] = $temp
        $script:CurrentCell++
        Write-Host "✓ Cellule déplacée vers le bas" -ForegroundColor Green
    } else {
        Write-Host "✗ Déjà en bas" -ForegroundColor Yellow
    }
    Start-Sleep -Milliseconds 500
    Show-DevInterface
}

function Clear-CurrentOutput {
    $script:Cells[$script:CurrentCell].Output = $null
    $script:Cells[$script:CurrentCell].Error = $null
    Write-Host "✓ Sortie effacée" -ForegroundColor Green
    Start-Sleep -Milliseconds 500
    Show-DevInterface
}

function List-Cells {
    Clear-Host
    Write-Host "=== LISTE DES CELLULES ===" -ForegroundColor Cyan
    Write-Host ""
    
    for ($i = 0; $i -lt $script:Cells.Count; $i++) {
        $cell = $script:Cells[$i]
        $indicator = if ($i -eq $script:CurrentCell) { "▶" } else { "  " }
        $status = if ($cell.Output) { "✓" } else { "○" }
        
        $firstLine = ($cell.Content -split "`r`n|`n")[0]
        if ($firstLine.Length -gt 60) { $firstLine = $firstLine.Substring(0, 57) + "..." }
        
        Write-Host "$indicator [$status] Cell $($i+1): $firstLine" -ForegroundColor $(if ($i -eq $script:CurrentCell) { "Green" } else { "White" })
    }
    
    Write-Host ""
    Write-Host "Appuyez sur Entrée pour continuer..." -ForegroundColor DarkGray
    Read-Host
    Show-DevInterface
}

function Add-Snippet {
    Clear-Host
    Write-Host @"
╔═══════════════════════════════════════════════════════════════════════════════╗
║                          INSÉRER UN SNIPPET                                   ║
╚═══════════════════════════════════════════════════════════════════════════════╝

1. Charger un fichier shapefile
2. Créer un buffer
3. Visualisation avancée
4. Exporter les données

Choisissez (1-4): 
"@ -ForegroundColor Cyan
    
    $choice = Read-Host
    $snippet = ""
    
    switch ($choice) {
        "1" {
            $snippet = @"
# Charger un fichier
file_path = r"C:\Users\User\OneDrive\Desktop\logiciel_spatial\data\mon_fichier.shp"

try:
    gdf = gpd.read_file(file_path)
    print(f"✓ Chargé: {len(gdf)} entités")
    print(f"CRS: {gdf.crs}")
    print(gdf.head())
except Exception as e:
    print(f"Erreur: {e}")
"@
        }
        "2" {
            $snippet = @"
# Créer un buffer
distance = 0.05  # degrés

gdf['buffer'] = gdf.geometry.buffer(distance)

fig, ax = plt.subplots()
gdf['buffer'].plot(ax=ax, alpha=0.5, label='Buffer')
gdf.plot(ax=ax, color='red', label='Original')
ax.legend()
plt.show()
"@
        }
        "3" {
            $snippet = @"
# Visualisation avancée
fig, ax = plt.subplots(figsize=(12, 8))

if 'population' in gdf.columns:
    gdf.plot(ax=ax, column='population', cmap='viridis', 
             legend=True, edgecolor='black')
else:
    gdf.plot(ax=ax, edgecolor='black', alpha=0.7)

ax.set_title('Ma Carte')
ax.grid(True, alpha=0.3)
plt.show()
"@
        }
        "4" {
            $snippet = @"
# Exporter
output = r"C:\Users\User\OneDrive\Desktop\logiciel_spatial\data\export.shp"
gdf.to_file(output)
print(f"✓ Exporté: {output}")
"@
        }
    }
    
    if ($snippet) {
        $script:Cells[$script:CurrentCell].Content = $snippet
        Write-Host "✓ Snippet inséré" -ForegroundColor Green
    }
    
    Start-Sleep -Milliseconds 1000
    Show-DevInterface
}

function Show-Help {
    Clear-Host
    Write-Host @"
╔═══════════════════════════════════════════════════════════════════════════════╗
║                              AIDE INTERACTIVE                                 ║
╚═══════════════════════════════════════════════════════════════════════════════╝

COMMANDES:
  run      - Exécuter la cellule courante
  new      - Créer une nouvelle cellule
  edit     - Éditer la cellule courante
  up       - Déplacer la cellule vers le haut
  down     - Déplacer la cellule vers le bas
  clear    - Effacer la sortie
  snippet  - Insérer un snippet
  save     - Sauvegarder le workspace
  load     - Charger le workspace
  list     - Lister les cellules
  help     - Afficher cette aide
  quit     - Quitter

FONCTIONS DISPONIBLES:
  info_layer(gdf)  - Infos d'une couche
  display_map(gdf) - Afficher une carte

"@ -ForegroundColor Cyan
    
    Write-Host "Appuyez sur Entrée pour continuer..." -ForegroundColor Yellow
    Read-Host
    Show-DevInterface
}

# ============================================================================
# DÉMARRAGE
# ============================================================================

Load-Workspace
Show-DevInterface

while ($true) {
    $command = Read-Host
    $command = $command.ToLower().Trim()
    
    switch ($command) {
        "run" { Run-CurrentCell }
        "new" { New-Cell }
        "edit" { Edit-CurrentCell }
        "up" { Move-CellUp }
        "down" { Move-CellDown }
        "clear" { Clear-CurrentOutput }
        "snippet" { Add-Snippet }
        "save" { Save-Workspace }
        "load" { Load-Workspace; Show-DevInterface }
        "list" { List-Cells }
        "help" { Show-Help }
        "quit" { Write-Host "Au revoir !" -ForegroundColor Green; break }
        "q" { Write-Host "Au revoir !" -ForegroundColor Green; break }
        default { 
            if ($command) {
                Write-Host "Commande inconnue. Tapez 'help'" -ForegroundColor Red
                Start-Sleep 1
                Show-DevInterface
            }
        }
    }
}
