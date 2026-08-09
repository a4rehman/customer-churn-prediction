#!/usr/bin/env pwsh
# Starts the Vite dev server on http://localhost:5173 (proxies /api -> :8000)
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "../frontend")
npm run dev
