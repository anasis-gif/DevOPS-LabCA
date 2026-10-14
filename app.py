"""Small Flask URL shortener; redirects never fetch destination content."""
import os
import secrets
import sqlite3
import string
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from flask import Flask, jsonify, redirect, render_template, request


def generate_code():
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(7))


def valid_url(value):
    if not isinstance(value, str) or len(value) > 2048:
        return False
    if any(ord(char) <= 32 or ord(char) == 127 for char in value) or '\\' in value:
        return False
    try:
        parsed = urlsplit(value)
        return (parsed.scheme.lower() in {'http', 'https'} and bool(parsed.hostname)
                and parsed.username is None and parsed.password is None
                and (parsed.port is None or 1 <= parsed.port <= 65535))
    except ValueError:
        return False


def create_app(config=None):
    app = Flask(__name__)
    app.config.update(DATABASE=os.getenv('DATABASE', 'data/links.db'),
                      PUBLIC_BASE_URL=os.getenv('PUBLIC_BASE_URL', 'http://localhost:8000').rstrip('/'),
                      MAX_CONTENT_LENGTH=8192)
    if config:
        app.config.update(config)
    if not valid_url(app.config['PUBLIC_BASE_URL']):
        raise ValueError('PUBLIC_BASE_URL must be an absolute HTTP(S) URL')
    Path(app.config['DATABASE']).parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def connect():
        db = sqlite3.connect(app.config['DATABASE'], timeout=10)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    with connect() as db:
        db.execute('PRAGMA journal_mode=WAL')
        db.execute('''CREATE TABLE IF NOT EXISTS links (
            short_code TEXT PRIMARY KEY, original_url TEXT NOT NULL,
            created_at TEXT NOT NULL, clicks INTEGER NOT NULL DEFAULT 0)''')

    @app.get('/')
    def home():
        return render_template('index.html')

    @app.post('/api/shorten')
    def shorten():
        payload = request.get_json(silent=True)
        url = payload.get('url') if isinstance(payload, dict) else None
        if not valid_url(url):
            return jsonify(error='Provide a valid HTTP or HTTPS URL without spaces or credentials.'), 400
        created = datetime.now(timezone.utc).isoformat()
        with connect() as db:
            for _ in range(10):
                code = generate_code()
                try:
                    db.execute('INSERT INTO links (short_code, original_url, created_at) VALUES (?, ?, ?)',
                               (code, url, created))
                    break
                except sqlite3.IntegrityError:
                    continue
            else:
                return jsonify(error='Could not allocate a short code. Please retry.'), 503
        return jsonify(short_code=code, short_url=f"{app.config['PUBLIC_BASE_URL']}/{code}"), 201

    @app.get('/api/stats/<short_code>')
    def stats(short_code):
        with connect() as db:
            row = db.execute('SELECT * FROM links WHERE short_code = ?', (short_code,)).fetchone()
        if row is None:
            return jsonify(error='Short code not found.'), 404
        return jsonify(dict(row))

    @app.get('/<short_code>')
    def follow(short_code):
        with connect() as db:
            row = db.execute('SELECT original_url FROM links WHERE short_code = ?', (short_code,)).fetchone()
            if row is None:
                return jsonify(error='Short code not found.'), 404
            db.execute('UPDATE links SET clicks = clicks + 1 WHERE short_code = ?', (short_code,))
        response = redirect(row['original_url'], code=302)
        response.headers['Cache-Control'] = 'no-store'
        return response

    @app.get('/health')
    def health():
        try:
            with connect() as db:
                db.execute('SELECT count(*) FROM links').fetchone()
        except sqlite3.Error:
            return jsonify(status='unhealthy'), 503
        return jsonify(status='ok')

    @app.errorhandler(413)
    def too_large(error):
        return jsonify(error='Request body is too large.'), 413

    return app
