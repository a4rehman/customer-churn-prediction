#!/usr/bin/env pwsh
# Starts the FastAPI backend on http://localhost:8000
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "../backend")
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
