# Arranca a API a partir da pasta backend (com venv activo)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path "..\.venv\Scripts\Activate.ps1") -and -not (Test-Path "..\venv\Scripts\Activate.ps1")) {
    Write-Host "Activa o venv primeiro: ..\venv\Scripts\Activate.ps1"
}

pip install -e . -q
uvicorn dev_agent.api.app:app --reload --port 8000
