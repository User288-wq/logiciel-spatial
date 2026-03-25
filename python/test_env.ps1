Write-Host "Test du script interactif" -ForegroundColor Green
Write-Host "Tapez 'run' pour exécuter, 'quit' pour quitter" -ForegroundColor Yellow

while ($true) {
    $cmd = Read-Host ">>> "
    if ($cmd -eq "run") {
        Write-Host "Exécution de la cellule..." -ForegroundColor Cyan
        python -c "print('Test réussi!')"
    } elseif ($cmd -eq "quit") {
        break
    } else {
        Write-Host "Commande inconnue: $cmd" -ForegroundColor Red
    }
}
