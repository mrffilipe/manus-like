# Reset local dev stack: wipe Postgres, Qdrant, Redis, and client file volumes.
# Run from repository root: .\scripts\reset-dev.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "Stopping containers and removing volumes..." -ForegroundColor Yellow
docker compose down -v

$localDirs = @(
    "backend\agent\data\client-files",
    "backend\agent\data\attachments"
)
foreach ($dir in $localDirs) {
    $fullPath = Join-Path $Root $dir
    if (Test-Path $fullPath) {
        Write-Host "Removing $dir ..."
        Remove-Item -Recurse -Force $fullPath
    }
}

Write-Host "Starting stack (build)..." -ForegroundColor Yellow
docker compose up --build -d

Write-Host "Waiting for agent-api health..." -ForegroundColor Yellow
$maxAttempts = 60
for ($i = 0; $i -lt $maxAttempts; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 3
        if ($response.StatusCode -eq 200) {
            Write-Host ""
            Write-Host "Stack limpo e pronto." -ForegroundColor Green
            Write-Host "  Frontend: http://localhost:3000"
            Write-Host "  Clientes: http://localhost:3000/clients (cadastre clientes pela UI)"
            Write-Host "  API:      http://localhost:8000/agent/clients (lista vazia)"
            exit 0
        }
    } catch {
        Start-Sleep -Seconds 3
    }
}

Write-Host "agent-api did not become healthy in time. Check: docker compose ps" -ForegroundColor Red
exit 1
