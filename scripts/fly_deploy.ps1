#!/usr/bin/env pwsh
# Deploy both services to Fly.io from the repo root.
# Prereqs: flyctl installed + `flyctl auth login` completed.
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")
$fly = "$env:USERPROFILE\.fly\bin\flyctl.exe"

if (-not (Test-Path $fly)) { throw "flyctl not found. Install: powershell -ExecutionPolicy Bypass -Command `"Invoke-WebRequest https://fly.io/install.ps1 -UseBasicParsing | Invoke-Expression`"" }

Write-Host "==> Creating apps (safe to skip if they already exist)"
& $fly apps create churniq-backend 2>$null
& $fly apps create churniq-frontend 2>$null

Write-Host "==> Backend volume (idempotent)"
& $fly volumes create churniq_data --app churniq-backend --size 1 --region iad 2>$null

Write-Host "==> Setting backend secrets (replace with your own values)"
& $fly secrets set --config fly.backend.toml SECRET_KEY=replace-this-random-string ADMIN_PASSWORD=replace-this-admin-password

Write-Host "==> Deploying backend (remote build trains the model; takes a few minutes)"
& $fly deploy --config fly.backend.toml --remote-only

Write-Host "==> Deploying frontend"
& $fly deploy --config fly.frontend.toml --remote-only

Write-Host ""
Write-Host "Frontend:  https://churniq-frontend.fly.dev"
Write-Host "API docs:  https://churniq-backend.fly.dev/docs"
