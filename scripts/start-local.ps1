# Start independently of a temporary terminal session. Logs stay in ignored data/.
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    throw 'Create .venv and install requirements-dev.txt first; see README.md.'
}
if (Get-NetTCPConnection -LocalPort 8001 -State Listen -ErrorAction SilentlyContinue) {
    throw 'Port 8001 is already in use. Check the running server before starting another.'
}
$dataDirectory = Join-Path $projectRoot 'data'
New-Item -ItemType Directory -Force -Path $dataDirectory | Out-Null
$oldBaseUrl = $env:PUBLIC_BASE_URL
$oldDatabase = $env:DATABASE
try {
    $env:PUBLIC_BASE_URL = 'http://localhost:8001'
    $env:DATABASE = Join-Path $dataDirectory 'links.db'
    $server = Start-Process -FilePath $python -ArgumentList @('-m', 'flask', '--app', 'wsgi', 'run', '--host', '127.0.0.1', '--port', '8001') -WorkingDirectory $projectRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $dataDirectory 'local-server.log') -RedirectStandardError (Join-Path $dataDirectory 'local-server-error.log') -PassThru
    $server.Id | Set-Content -LiteralPath (Join-Path $dataDirectory 'local-server.pid')
    Write-Output "Started local server PID $($server.Id). Open http://localhost:8001."
    Write-Output 'Logs: data/local-server.log and data/local-server-error.log'
} finally {
    $env:PUBLIC_BASE_URL = $oldBaseUrl
    $env:DATABASE = $oldDatabase
}
