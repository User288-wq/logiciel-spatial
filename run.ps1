# Activer l'environnement virtuel
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    .\venv\Scripts\Activate.ps1
}

Write-Host "╔════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   LOGICIEL SPATIAL - ENVIRONNEMENT ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "Commandes disponibles :" -ForegroundColor Yellow
Write-Host "  • python python/examples/distance.py  - Lancer l'exemple Terre-Lune"
Write-Host "  • python -m pytest tests/            - Lancer les tests"
Write-Host "  • deactivate                          - Quitter l'environnement"
Write-Host ""
