

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot

Set-Location $projectRoot

# ----------------------------------------------------------------------
# Authentification reelle
# ----------------------------------------------------------------------

$env:EASY_PROJET_DEV_AUTO_LOGIN = "0"
$env:EASY_PROJET_DEV_AUTO_LOGIN_EMAIL = ""

Write-Host "Mode authentification reelle"
Write-Host ""

Write-Host "Demarrage du tunnel Cloudflare..."

$varDirectory = Join-Path $projectRoot "var"

if (-not (Test-Path $varDirectory)) {
    New-Item `
        -ItemType Directory `
        -Path $varDirectory `
        -Force `
        | Out-Null
}

$cloudflaredStdout = Join-Path $varDirectory "cloudflared.out.log"
$cloudflaredStderr = Join-Path $varDirectory "cloudflared.err.log"

Remove-Item `
    $cloudflaredStdout `
    -Force `
    -ErrorAction SilentlyContinue

Remove-Item `
    $cloudflaredStderr `
    -Force `
    -ErrorAction SilentlyContinue

$cloudflaredProcess = Start-Process `
    -FilePath "cloudflared" `
    -ArgumentList @(
        "tunnel",
        "--url",
        "http://127.0.0.1:8000"
    ) `
    -RedirectStandardOutput $cloudflaredStdout `
    -RedirectStandardError $cloudflaredStderr `
    -PassThru `
    -WindowStyle Hidden

Write-Host "Attente de l'URL publique Cloudflare..."

$publicUrl = $null
$timeoutSeconds = 30
$startTime = Get-Date

while (-not $publicUrl) {

    $elapsedSeconds = (
        (Get-Date) - $startTime
    ).TotalSeconds

    if ($elapsedSeconds -gt $timeoutSeconds) {

        Stop-Process `
            -Id $cloudflaredProcess.Id `
            -Force `
            -ErrorAction SilentlyContinue

        throw "Impossible de recuperer l'URL Cloudflare apres $timeoutSeconds secondes."
    }

    $logFiles = @(
        $cloudflaredStdout,
        $cloudflaredStderr
    )

    foreach ($logFile in $logFiles) {

        if (-not (Test-Path $logFile)) {
            continue
        }

        $match = Select-String `
            -Path $logFile `
            -Pattern "https://[a-z0-9-]+\.trycloudflare\.com" `
            | Select-Object -First 1

        if ($match) {

            $publicUrl = (
                [regex]::Match(
                    $match.Line,
                    "https://[a-z0-9-]+\.trycloudflare\.com"
                )
            ).Value

            break
        }
    }

    if (-not $publicUrl) {
        Start-Sleep -Milliseconds 500
    }
}

$env:EASY_PROJET_PUBLIC_URL = $publicUrl

Write-Host ""
Write-Host "Tunnel Cloudflare actif :"
Write-Host $publicUrl
Write-Host ""
Write-Host "Demarrage Django sans auto-login..."
Write-Host ""

try {

    python manage.py runserver 127.0.0.1:8000

}
finally {

    Write-Host ""
    Write-Host "Arret du tunnel Cloudflare..."

    Stop-Process `
        -Id $cloudflaredProcess.Id `
        -Force `
        -ErrorAction SilentlyContinue
}