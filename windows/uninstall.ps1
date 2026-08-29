[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$target = Join-Path $env:LOCALAPPDATA "eazy"
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")

if ($userPath) {
    $parts = $userPath -split ";" | Where-Object { $_ -and $_.Trim() -and $_ -ne $target }
    [Environment]::SetEnvironmentVariable("Path", ($parts -join ";"), "User")
}

if (Test-Path $target) {
    Remove-Item -Recurse -Force $target
    Write-Host "eazy para Windows removido de: $target" -ForegroundColor Green
} else {
    Write-Host "A instalação Windows do eazy não foi encontrada." -ForegroundColor Yellow
}

Write-Host "A versão Linux/Bash do repositório não foi alterada." -ForegroundColor Cyan
