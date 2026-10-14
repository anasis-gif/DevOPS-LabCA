# Real evidence checklist

Capture screenshots yourself after successful checks. Place them in a submission folder, with timestamps and captions. Do not manufacture screenshots or use placeholders as proof. Avoid showing private keys, tokens, secret values or personal unrelated data.

| Evidence | What must be visible | Status / file or run link |
|---|---|---|
| Homepage | URL input, generated short URL, Copy button | TODO |
| Redirect | Real short URL opens original destination; optionally 302 headers | TODO |
| Stats | Original URL, code, UTC creation time, click count | TODO |
| Tests | Actual pytest command, passing count and exit result | TODO |
| Lint | Actual Ruff command and successful result | TODO |
| Docker build | Completed build output | TODO |
| Container | Compose service running and healthy | TODO |
| Container API smoke | Successful real HTTP smoke check | TODO |
| Persistence | Same stats before and after container recreation | TODO |
| GitHub CI | Real passing ci job with branch and commit | TODO / unavailable until pushed |
| GHCR publishing | Passing publish job and matching SHA image tag | TODO / unavailable until pushed |
| Deployment | Passing deploy job with commit and healthy Compose service | TODO / only if host configured |
| Public health | Actual public /health response from deployment | TODO / only if host configured |
| Rollback | Previous SHA running and healthy, if demonstrated | OPTIONAL |

Use `docs/validation.md` to distinguish local executed checks from remote unverified stages. If no host exists, label deployment “configured, not executed” in the report and presentation.
