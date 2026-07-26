# Packages the extension into a distributable zip for GitHub Releases.
# Usage:  powershell -File extension/package.ps1 [-ApiUrl https://your-api.onrender.com]
param(
    [string]$ApiUrl = ""
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$manifest = Get-Content (Join-Path $root "manifest.json") | ConvertFrom-Json
$version = $manifest.version
$staging = Join-Path $env:TEMP "trivium-companion-pkg"
$outDir = Join-Path (Split-Path -Parent $root) "dist"
$zipPath = Join-Path $outDir "trivium-companion-v$version.zip"

if (Test-Path $staging) { Remove-Item $staging -Recurse -Force }
New-Item -ItemType Directory -Force $staging | Out-Null
New-Item -ItemType Directory -Force $outDir | Out-Null

# Copy everything shippable (no tests, no packaging script).
Copy-Item (Join-Path $root "manifest.json") $staging
Copy-Item (Join-Path $root "background.js") $staging
Copy-Item (Join-Path $root "popup.html") $staging
Copy-Item (Join-Path $root "popup.js") $staging
Copy-Item (Join-Path $root "README.md") $staging
Copy-Item (Join-Path $root "lib") (Join-Path $staging "lib") -Recurse
Copy-Item (Join-Path $root "icons") (Join-Path $staging "icons") -Recurse

# Optionally bake in the production server URL as the default.
if ($ApiUrl -ne "") {
    $bg = Join-Path $staging "background.js"
    (Get-Content $bg -Raw) -replace "const DEFAULT_API = 'http://localhost:8000'", "const DEFAULT_API = '$ApiUrl'" |
        Set-Content -Encoding utf8 $bg
    $popup = Join-Path $staging "popup.js"
    (Get-Content $popup -Raw) -replace "http://localhost:8000", $ApiUrl | Set-Content -Encoding utf8 $popup
    Write-Host "Default server URL set to $ApiUrl"
}

if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
Compress-Archive -Path (Join-Path $staging "*") -DestinationPath $zipPath
Remove-Item $staging -Recurse -Force
Write-Host "Packaged: $zipPath"
