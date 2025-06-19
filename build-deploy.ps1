# Script PowerShell pour build Docker LOCAL uniquement
# Pas de registry - juste pour développement local

param(
    [string]$ImageName = "python-videogames-processor",
    [string]$Version = "latest",
    [string]$GitRepoUrl = "https://github.com/yannoushka74/Video_games_market.git",
    [switch]$SkipTest,
    [switch]$Rebuild
)

Write-Host ""
Write-Host "🎮 Build Docker LOCAL - Processeur de Jeux Vidéo" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier Docker
Write-Host "Vérification de Docker..." -ForegroundColor Yellow
docker --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker non trouvé ou non démarré" -ForegroundColor Red
    Write-Host "💡 Assurez-vous que Docker Desktop est lancé" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Docker OK" -ForegroundColor Green
Write-Host ""

# Configuration
Write-Host "⚙️ Configuration:" -ForegroundColor White
Write-Host "  Image: $ImageName" -ForegroundColor Yellow
Write-Host "  Version: $Version" -ForegroundColor Yellow
Write-Host "  Build context: $(Get-Location)" -ForegroundColor Yellow
Write-Host ""

# Vérifier si l'image existe déjà
$imageExists = docker images -q "$ImageName`:$Version" 2>$null
if ($imageExists -and -not $Rebuild) {
    Write-Host "⚠️ L'image $ImageName`:$Version existe déjà" -ForegroundColor Yellow
    $response = Read-Host "Rebuilder l'image? (y/N)"
    if ($response -notmatch "^[Yy]") {
        Write-Host "⏭️ Build ignoré - utilisation de l'image existante" -ForegroundColor Yellow
        $skipBuild = $true
    }
}

# Build de l'image (si nécessaire)
if (-not $skipBuild) {
    Write-Host "🏗️ Construction de l'image Docker..." -ForegroundColor Cyan
    
    # Arguments de build
    $buildArgs = @(
        "build",
        "--tag", "$ImageName`:$Version"
    )
    
    # Ajouter l'URL Git si spécifiée
    if ($GitRepoUrl) {
        $buildArgs += "--build-arg"
        $buildArgs += "GIT_REPO_URL=$GitRepoUrl"
    }
    
    # Ajouter le contexte (répertoire actuel)
    $buildArgs += "."
    
    Write-Host "Commande: docker $($buildArgs -join ' ')" -ForegroundColor Gray
    Write-Host ""
    
    # Exécuter le build
    & docker @buildArgs
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Image construite avec succès!" -ForegroundColor Green
    } else {
        Write-Host "❌ Erreur lors du build" -ForegroundColor Red
        exit 1
    }
    Write-Host ""
}

# Test de l'image (optionnel)
if (-not $SkipTest) {
    Write-Host "🧪 Test de l'image..." -ForegroundColor Cyan
    
    $currentDate = Get-Date -Format "yyyy-MM-dd"
    $runId = "test-$(Get-Date -Format 'yyyyMMddHHmmss')"
    
    $testCmd = @(
        "run", "--rm",
        "-e", "EXECUTION_DATE=$currentDate",
        "-e", "RUN_ID=$runId",
        "-e", "DAG_ID=test_dag",
        "-e", "TASK_ID=test_task",
        "-e", "TASK_TYPE=main",
        "$ImageName`:$Version"
    )
    
    Write-Host "Test en cours..." -ForegroundColor Yellow
    & docker @testCmd
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Test réussi!" -ForegroundColor Green
    } else {
        Write-Host "❌ Test échoué" -ForegroundColor Red
        Write-Host "💡 Vérifiez les logs ci-dessus" -ForegroundColor Yellow
    }
    Write-Host ""
} else {
    Write-Host "⏭️ Tests ignorés (-SkipTest spécifié)" -ForegroundColor Yellow
    Write-Host ""
}

# Afficher les images disponibles
Write-Host "📋 Images Docker locales:" -ForegroundColor Cyan
docker images | Select-String -Pattern $ImageName
Write-Host ""

# Instructions finales
Write-Host "🎉 Build terminé!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Étapes suivantes:" -ForegroundColor Cyan
Write-Host "1. L'image $ImageName`:$Version est maintenant disponible localement" -ForegroundColor White
Write-Host "2. Votre DAG Airflow peut utiliser cette image directement" -ForegroundColor White
Write-Host "3. Testez le DAG dans l'interface Airflow" -ForegroundColor White
Write-Host ""
Write-Host "🔧 Commandes utiles:" -ForegroundColor Cyan
Write-Host "  # Voir toutes les images:" -ForegroundColor Gray
Write-Host "  docker images" -ForegroundColor Yellow
Write-Host ""
Write-Host "  # Tester manuellement:" -ForegroundColor Gray
Write-Host "  docker run --rm -it $ImageName`:$Version" -ForegroundColor Yellow
Write-Host ""
Write-Host "  # Voir les logs d'un conteneur:" -ForegroundColor Gray
Write-Host "  docker logs [container_id]" -ForegroundColor Yellow
Write-Host ""
Write-Host "  # Supprimer l'image si besoin:" -ForegroundColor Gray
Write-Host "  docker rmi $ImageName`:$Version" -ForegroundColor Yellow
Write-Host ""

Write-Host "🏁 Terminé!" -ForegroundColor Green