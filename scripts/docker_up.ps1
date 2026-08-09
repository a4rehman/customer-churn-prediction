#!/usr/bin/env pwsh
# Builds and starts the full stack with Docker Compose
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")
docker compose up --build -d
Write-Host "Frontend: http://localhost:8080"
Write-Host "Backend API + docs: http://localhost:8000/docs"
