# Rebuild the deck end to end.
#
#   pwsh scripts/render.ps1            rebuild figures + HTML
#   pwsh scripts/render.ps1 -Pdf       also refresh the print fallback
#
# The rendered HTML is self-contained, so docs/index.html is the only file
# needed to present.

[CmdletBinding()]
param(
    [switch]$Pdf
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Push-Location $root

try {
    Write-Host '==> Figures' -ForegroundColor Cyan
    python scripts/make_figures.py

    Write-Host '==> Quarto' -ForegroundColor Cyan
    quarto render slides/on-the-same-wavelength.qmd

    Copy-Item slides/index.html docs/index.html -Force
    $mb = [math]::Round((Get-Item docs/index.html).Length / 1MB, 2)
    Write-Host "==> docs/index.html  ($mb MB, self-contained)" -ForegroundColor Green

    if ($Pdf) {
        $chrome = @(
            "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
            "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
            "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
        ) | Where-Object { Test-Path $_ } | Select-Object -First 1

        if (-not $chrome) {
            Write-Warning 'Chrome not found; skipping the PDF.'
            return
        }

        # reveal.js only lays out for print under ?print-pdf, which needs a real
        # http origin -- Chrome will not apply it to a file:// URL.
        $port = 8931
        $server = Start-Process python `
            -ArgumentList '-m', 'http.server', $port, '--directory', 'docs' `
            -WindowStyle Hidden -PassThru
        try {
            Start-Sleep -Seconds 2
            $out = Join-Path $root 'docs/on-the-same-wavelength.pdf'
            & $chrome --headless=new --disable-gpu --no-pdf-header-footer `
                --virtual-time-budget=25000 --run-all-compositor-stages-before-draw `
                --print-to-pdf="$out" "http://127.0.0.1:$port/index.html?print-pdf" 2>$null | Out-Null
            Write-Host "==> docs/on-the-same-wavelength.pdf" -ForegroundColor Green
        }
        finally {
            Stop-Process -Id $server.Id -Force -ErrorAction SilentlyContinue
        }
    }
}
finally {
    Pop-Location
}
