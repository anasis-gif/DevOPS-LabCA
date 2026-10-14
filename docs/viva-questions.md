# Viva questions and simple answers

1. **What does this project do?** It shortens web URLs and demonstrates automated testing, containerization and deployment.
2. **What is CI?** Continuous integration automatically checks changes using linting, tests and a container smoke check.
3. **What is CD here?** A successful main build can deploy a published commit image to a configured Linux host.
4. **Is publishing the same as deployment?** No. Publishing stores an image in GHCR; deployment starts that image on a server.
5. **Why Flask?** It provides a small Python web framework that is easy to understand and test.
6. **Why SQLite?** It stores records in a file without needing a separate database service, suitable for a small single-host lab.
7. **How is a short code generated?** Seven random letters/digits are chosen using the secrets module.
8. **What if codes collide?** The database rejects the duplicate primary key and the app tries another code, up to ten attempts.
9. **How do redirects work?** The server returns HTTP 302 with the destination in the Location header.
10. **Does the server download the target page?** No; the visitor's browser follows the redirect.
11. **How are clicks counted?** A SQL update increments the stored counter for each successful redirect request.
12. **What prevents SQL injection?** Values use parameterized queries rather than being inserted into SQL text.
13. **Why validate URLs?** Only HTTP(S) destinations are accepted, avoiding unsupported schemes and malformed inputs.
14. **What is Docker?** It packages the application and runtime into an image that runs as a container.
15. **Image versus container?** An image is a packaged template; a container is its running instance.
16. **Why use a volume?** Container files can disappear on replacement; the named volume keeps the database and clicks.
17. **Why Gunicorn and a non-root user?** Gunicorn serves the production Flask app; a non-root user reduces container privileges.
18. **What does the health check test?** The HTTP service responds and can query its links table.
19. **Why tag images with the commit SHA?** It identifies the source version and lets us deploy or roll back to a specific image.
20. **How are deployment credentials protected?** They are stored in GitHub secrets, with verified SSH host keys and no secret files committed.
21. **How are tests isolated?** Each test gets a temporary database rather than the real application database.
22. **What are the limitations?** One-host SQLite, brief deployment downtime, no abuse controls or TLS proxy, and live CD needs an actual host.
