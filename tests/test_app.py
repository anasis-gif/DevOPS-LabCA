import pytest

import app as module


@pytest.fixture
def application(tmp_path):
    return module.create_app({'TESTING': True, 'DATABASE': str(tmp_path / 'links.db'),
                              'PUBLIC_BASE_URL': 'https://short.example'})


@pytest.fixture
def client(application):
    return application.test_client()


def create(client):
    return client.post('/api/shorten', json={'url': 'https://example.com/path?q=1'})


def test_create(client):
    response = create(client)
    assert response.status_code == 201
    data = response.get_json()
    assert data['short_url'] == f"https://short.example/{data['short_code']}"
    stats = client.get('/api/stats/' + data['short_code']).get_json()
    assert stats['original_url'] == 'https://example.com/path?q=1'
    assert stats['clicks'] == 0
    assert stats['created_at'].endswith('+00:00')


def test_redirect_and_clicks(client):
    code = create(client).get_json()['short_code']
    for count in (1, 2):
        response = client.get('/' + code)
        assert response.status_code == 302
        assert response.headers['Location'] == 'https://example.com/path?q=1'
        assert response.headers['Cache-Control'] == 'no-store'
        assert client.get('/api/stats/' + code).get_json()['clicks'] == count


@pytest.mark.parametrize('url', [None, '', 'ftp://example.com', 'javascript:alert(1)',
                                'https://', '//example.com', 'https://a b.com',
                                'https://user:pass@example.com', 'https://a.com:bad',
                                'https://a.com:0', 'https://a.com\\evil', 123, 'x' * 2049])
def test_invalid(client, url):
    assert client.post('/api/shorten', json={'url': url}).status_code == 400


@pytest.mark.parametrize('payload', [{}, [], None])
def test_missing(client, payload):
    assert client.post('/api/shorten', json=payload).status_code == 400


def test_unknown(client):
    assert client.get('/missing').status_code == 404
    assert client.get('/api/stats/missing').status_code == 404


def test_health_and_frontend(client):
    assert client.get('/health').get_json() == {'status': 'ok'}
    assert b'id="shorten-form"' in client.get('/').data
    assert client.get('/static/app.js').status_code == 200
    assert client.get('/static/style.css').status_code == 200


def test_collision(client, monkeypatch):
    monkeypatch.setattr(module, 'generate_code', lambda: 'same123')
    assert create(client).status_code == 201
    codes = iter(['same123', 'new1234'])
    monkeypatch.setattr(module, 'generate_code', lambda: next(codes))
    assert create(client).get_json()['short_code'] == 'new1234'


def test_collision_exhaustion(client, monkeypatch):
    monkeypatch.setattr(module, 'generate_code', lambda: 'same123')
    create(client)
    assert create(client).status_code == 503


def test_persistence(application, client):
    code = create(client).get_json()['short_code']
    client.get('/' + code)
    reopened = module.create_app(application.config).test_client()
    assert reopened.get('/api/stats/' + code).get_json()['clicks'] == 1


def test_sql_parameterization(client):
    assert client.get("/api/stats/'%20OR%201=1--").status_code == 404


def test_body_limit(client):
    assert client.post('/api/shorten', data='x' * 9000, content_type='application/json').status_code == 413


print("All tests passed!")