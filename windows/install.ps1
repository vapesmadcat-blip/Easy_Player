[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$source = Split-Path -Parent $MyInvocation.MyCommand.Path
$target = Join-Path $env:LOCALAPPDATA "eazy"
$commandDir = $target

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    throw "Python não foi encontrado. Instale Python 3.10+ e marque 'Add Python to PATH'."
}

New-Item -ItemType Directory -Force -Path $target | Out-Null
Copy-Item -Force (Join-Path $source "eazy.py") (Join-Path $target "eazy.py")
Copy-Item -Force (Join-Path $source "README.md") (Join-Path $target "README.md")

$cmd = "@echo off`r`npy `"$target\eazy.py`" %*`r`n"
Set-Content -Path (Join-Path $target "eazy.cmd") -Value $cmd -Encoding ASCII

$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$parts = @()
if ($userPath) { $parts = $userPath -split ";" | Where-Object { $_ -and $_.Trim() } }
if ($parts -notcontains $commandDir) {
    [Environment]::SetEnvironmentVariable("Path", (($parts + $commandDir) -join ";"), "User")
}

Write-Host "eazy para Windows instalado em: $target" -ForegroundColor Green
Write-Host "Feche e abra o PowerShell novamente para atualizar o PATH." -ForegroundColor Yellow
Write-Host "Depois, execute: eazy" -ForegroundColor Cyan
