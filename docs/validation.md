# Actual validation record

## Recovery check — 14 October 2026

The initial temporary Python command-session server subsequently stopped accepting connections. The new `scripts/start-local.ps1` starts a separate hidden process with logs and a PID file. After the launcher command exited successfully, an independent request returned `{"status":"ok"}` from http://127.0.0.1:8001/health and the complete HTTP smoke check passed again. This does not configure startup after a Windows reboot.

The browser could load an old page but shortening requests hung. A direct `/health` request on port 8000 timed out after five seconds, and Docker reported it was unable to start. Docker Desktop restart also failed with a startup deadline exceeded error.

The frontend now aborts a request after ten seconds, explains that the server is unresponsive, and restores the button. Three Node regression tests passed for timeout, successful response and network failure. Backend tests passed again: 25 passed in 3.92 seconds; Ruff passed.

A temporary local Flask development server was started on port 8001 using `PUBLIC_BASE_URL=http://localhost:8001`. It uses the local `data/links.db`, separate from the Docker volume. Existing Docker links require Docker recovery; the volume was not deleted. Docker's old image needs rebuilding after recovery to include the frontend fix.

Date: 13 October 2026 (Asia/Calcutta).

## Executed locally

| Check | Actual outcome |
|---|---|
| Dependency installation | Successful in `.venv` using Python 3.12 |
| Dependency consistency | `python -m pip check`: No broken requirements found |
| Automated tests | Final run: **25 passed in 4.10 seconds**, exit code 0 |
| Lint | `ruff check .`: All checks passed, exit code 0 |
| Local Compose configuration | `docker compose config --quiet`: exit code 0 |
| Docker image build | Final application build succeeded, exit code 0 |
| Container health | Compose `up -d --wait` succeeded; service reported healthy |
| Real HTTP smoke | PASS: health, homepage, shortening, redirect and click count |
| Container recreation persistence | PASS: record, destination, timestamp and click count preserved after `down` and `up` |
| Persistence sample | Code `KvGw4C9`, URL `https://example.com/persistence-check`, clicks `1` before and after |
| Non-root runtime | `id`: uid=10001(app), gid=10001(app) |
| Production Compose config | Validated with placeholder commit image and public URL, exit code 0 |
| Deployment shell syntax | `bash -n /deploy.sh` inside Linux image: exit code 0 |

The final tested application image manifest was `sha256:88f03529967428f133dd603ba75a72836e63b91f570aa48dc1f3efc39cd8a008` (local build only). Docker Desktop was initially stopped; it was started and its Linux engine became available. The container is left running on http://localhost:8000. The virtual environment and database volume are local runtime artifacts, excluded from source control.

## Not executed remotely

There is no configured Git remote or supplied deployment host. The workflow and deployment configuration are implemented; production Compose and shell syntax were checked locally. The workflow has not been executed on GitHub and the SSH script has not deployed to a real host. No screenshot evidence or team contributions have been invented. All source changes remain uncommitted for review.

Remote GitHub Actions, GHCR publishing, SSH deployment, public health and rollback remain unverified until real services are configured and run. Evidence screenshots must be collected separately.
