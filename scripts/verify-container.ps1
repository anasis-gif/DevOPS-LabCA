# Run in PowerShell from the project root after docker compose build.
param([string]$BaseUrl = 'http://localhost:8000')
$ErrorActionPreference = 'Stop'
docker compose up -d --wait
if ($LASTEXITCODE -ne 0) { throw 'Container failed to start healthy' }
.\.venv\Scripts\python.exe scripts/smoke.py --base $BaseUrl
if ($LASTEXITCODE -ne 0) { throw 'HTTP smoke check failed' }
$body = @{url='https://example.com/persistence-check'} | ConvertTo-Json
$link = Invoke-RestMethod -Method Post -Uri "$BaseUrl/api/shorten" -ContentType application/json -Body $body
curl.exe --fail --silent --output NUL "$BaseUrl/$($link.short_code)"
if ($LASTEXITCODE -ne 0) { throw 'Redirect request failed' }
$before = Invoke-RestMethod "$BaseUrl/api/stats/$($link.short_code)"
if ($before.clicks -ne 1) { throw 'Unexpected click count before recreation' }
docker compose down
if ($LASTEXITCODE -ne 0) { throw 'Container removal failed' }
docker compose up -d --wait
if ($LASTEXITCODE -ne 0) { throw 'Recreated container failed health check' }
$after = Invoke-RestMethod "$BaseUrl/api/stats/$($link.short_code)"
if ($after.short_code -ne $before.short_code -or $after.original_url -ne $before.original_url -or $after.created_at -ne $before.created_at -or $after.clicks -ne $before.clicks) {
    throw 'Persistence verification failed'
}
Write-Output 'PASS: database record and click count survived container removal and recreation'
$after | Format-List
docker compose ps
