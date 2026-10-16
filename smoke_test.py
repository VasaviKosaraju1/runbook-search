"""Exercise a running deployment; nonzero exit on failed readiness or API checks."""
import argparse
import json
from http.client import HTTPException
import time
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import urlopen


def verify(base):
    parsed = urlsplit(base)
    if parsed.scheme not in ('http', 'https') or not parsed.netloc or parsed.query or parsed.fragment:
        raise ValueError('Provide an HTTP(S) origin without a query or fragment')
    base = base.rstrip('/')
    for attempt in range(30):
        try:
            with urlopen(base + '/health', timeout=5) as response:
                health = json.load(response)
            if health.get('status') == 'ok' and health.get('chunks', 0) > 0:
                break
        except (OSError, HTTPException):
            pass
        time.sleep(2)
    else:
        raise RuntimeError('Readiness did not pass within 30 attempts')
    with urlopen(base + '/api/search?q=OOMKilled', timeout=10) as response:
        results = json.load(response)['results']
    if not results or not results[0]['source'].startswith('runbook-memory.md'):
        raise RuntimeError('Search source check failed')
    with urlopen(base + '/metrics', timeout=10) as response:
        if b'runbook_http_requests_total' not in response.read():
            raise RuntimeError('Metrics are missing')
    try:
        urlopen(base + '/.env', timeout=10).close()
    except HTTPError as error:
        if error.code != 404:
            raise RuntimeError('Private-path check returned unexpected status') from error
    else:
        raise RuntimeError('Private-path check unexpectedly succeeded')
    print('PASS: readiness, source retrieval, metrics, and private-path checks')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('base_url')
    args = parser.parse_args()
    verify(args.base_url)
