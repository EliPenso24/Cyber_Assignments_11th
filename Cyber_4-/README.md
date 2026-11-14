# HTTP Server with Performance Metrics

`Cyber_4+.py` extends the HTTP server from the course template by Barak Gonen and Nir Dweck. It listens on port 80 and serves files from `C:\WEBROOT`.

- Adds Date, Server, Connection and X-Response-Time headers.
- `GET /calculate-next` and `GET /calculate-area` (triangle).
- `POST /upload` saves a file to `C:\WEBROOT/uploads/`, and `GET /image?image-name=...` returns it.
- Blocks directory traversal in uploaded-file paths.
- Assertion tests run at startup.
