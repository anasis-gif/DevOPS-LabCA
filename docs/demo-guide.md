# Demonstration guide

Run Windows commands in PowerShell opened at the project folder. Linux commands belong in an SSH terminal on the deployment host. Capture real screenshots at each stage.

## 1. Explain the application (one minute)
“Our service creates a random short code, stores the original URL in SQLite, and sends a 302 redirect when somebody visits the short link. It counts visits without fetching the destination itself.”

## 2. Show automated checks — Windows
```powershell
.\.venv\Scripts\ruff.exe check .
.\.venv\Scripts\python.exe -m pytest -q
```
Explain isolated temporary databases and show the collision test.

## 3. Start the container — Windows
Start Docker Desktop first. Stop any Flask server using port 8000.
```powershell
docker compose build
docker compose up -d --wait
docker compose ps
docker compose logs --tail 30 web
.\.venv\Scripts\python.exe scripts/smoke.py
```
Open http://localhost:8000, paste an HTTPS URL, shorten it, copy it, and open the short URL in a new tab.

## 4. API and persistence — Windows
```powershell
$json = @{url='https://example.com/lab-demo'} | ConvertTo-Json
$saved = Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/shorten -ContentType application/json -Body $json
curl.exe -i $saved.short_url
Invoke-RestMethod "http://localhost:8000/api/stats/$($saved.short_code)"
docker compose down
docker compose up -d --wait
Invoke-RestMethod "http://localhost:8000/api/stats/$($saved.short_code)"
```
Show the unchanged short code and click count after recreation. Do not use `down -v`.

## 5. Show CI and publishing — GitHub browser
Open repository **Actions → Test, publish and deploy → latest run**. Show lint/tests/container smoke and the successful publish job. Open profile **Packages → repository image** and show the matching commit SHA tag. If no actual run exists, explain that this stage is configured but unverified; do not present a workflow file as a passing run.

## 6. Optional live CD — GitHub and Linux
Show the successful deployment job, open the public URL, then in the Linux SSH terminal:
```bash
cd /opt/url-shortener
export IMAGE="$(cat current-image.txt)"
docker compose ps
docker compose logs --tail 30 web
curl -f http://localhost:8000/health
```
Use the port configured in host `.env` if different. Only show live CD when a host was actually configured and deployment passed.

## 7. Finish
Explain rollback: `bash deploy.sh "$(cat previous-image.txt)"` on Linux. Show README setup instructions and evidence checklist. Stop the local stack with `docker compose down`.
