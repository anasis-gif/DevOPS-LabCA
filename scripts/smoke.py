"""Exercise a real HTTP server with only the Python standard library."""
import argparse
import json
import time
import urllib.error
import urllib.request


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base', default='http://localhost:8000')
    parser.add_argument('--wait', action='store_true')
    args = parser.parse_args()
    base = args.base.rstrip('/')
    for attempt in range(30 if args.wait else 1):
        try:
            with urllib.request.urlopen(base + '/health', timeout=2) as response:
                assert json.load(response)['status'] == 'ok'
            break
        except (OSError, AssertionError):
            if not args.wait or attempt == 29:
                raise
            time.sleep(1)
    request = urllib.request.Request(base + '/api/shorten',
                                     data=json.dumps({'url': 'https://example.com/demo'}).encode(),
                                     headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(request, timeout=5) as response:
        assert response.status == 201
        data = json.load(response)
    opener = urllib.request.build_opener(NoRedirect)
    try:
        opener.open(base + '/' + data['short_code'], timeout=5)
        raise AssertionError('Expected HTTP 302')
    except urllib.error.HTTPError as error:
        assert error.code == 302
        assert error.headers['Location'] == 'https://example.com/demo'
    with urllib.request.urlopen(base + '/api/stats/' + data['short_code'], timeout=5) as response:
        assert json.load(response)['clicks'] == 1
    with urllib.request.urlopen(base, timeout=5) as response:
        assert b'id="shorten-form"' in response.read()
    print('PASS: health, homepage, shortening, redirect and click count')


if __name__ == '__main__':
    main()
