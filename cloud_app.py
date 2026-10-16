"""WSGI entry point for the container lab. Synthetic documents only."""
import json
import mimetypes
from pathlib import Path
import threading
import time
from urllib.parse import parse_qs
from search import SearchIndex, load_documents

ROOT = Path(__file__).parent


class Application:
    def __init__(self, directory=ROOT, logger=print):
        self.directory = Path(directory)
        self.index = SearchIndex(load_documents(self.directory))
        self.logger = logger
        self.lock = threading.Lock()
        self.counts = {}
        self.seconds = 0.0

    def route(self, environ):
        path = environ.get('PATH_INFO', '/')
        if environ.get('REQUEST_METHOD') != 'GET':
            return 405, 'application/json', {'error': 'Use GET'}
        if path == '/health':
            return (200 if self.index.documents else 503), 'application/json', {
                'status': 'ok' if self.index.documents else 'unavailable',
                'chunks': len(self.index.documents)}
        if path == '/metrics':
            with self.lock:
                lines = ['# TYPE runbook_http_requests_total counter']
                for (route, status), count in sorted(self.counts.items()):
                    lines.append(f'runbook_http_requests_total{{route="{route}",status="{status}"}} {count}')
                lines += ['# TYPE runbook_http_duration_seconds_total counter',
                          f'runbook_http_duration_seconds_total {self.seconds:.6f}']
            return 200, 'text/plain; version=0.0.4', '\n'.join(lines) + '\n'
        if path == '/api/search':
            params = parse_qs(environ.get('QUERY_STRING', ''), keep_blank_values=True)
            query = params.get('q', [''])[0].strip()
            if not query or len(query) > 500:
                return 400, 'application/json', {'error': 'q must contain 1 to 500 characters'}
            try:
                limit = int(params.get('limit', ['3'])[0])
                hits = self.index.search(query, limit)
            except ValueError:
                return 400, 'application/json', {'error': 'limit must be an integer between 1 and 100'}
            return 200, 'application/json', {'results': hits}
        assets = {'/': 'index.html', '/index.html': 'index.html',
                  '/web.js': 'web.js', '/runbooks.json': 'runbooks.json'}
        if path in assets:
            file = self.directory / assets[path]
            return 200, mimetypes.guess_type(file.name)[0] or 'application/octet-stream', file.read_bytes()
        return 404, 'application/json', {'error': 'not found'}

    def __call__(self, environ, start_response):
        started = time.monotonic()
        path = environ.get('PATH_INFO', '/')
        route = path if path in ('/', '/index.html', '/web.js', '/runbooks.json',
                                 '/health', '/metrics', '/api/search') else 'other'
        try:
            status, content_type, body = self.route(environ)
        except Exception:
            # A fixed message avoids leaking request contents, paths or credentials.
            status, content_type, body = 500, 'application/json', {'error': 'internal error'}
        if isinstance(body, dict):
            body = json.dumps(body).encode('utf-8')
        elif isinstance(body, str):
            body = body.encode('utf-8')
        duration = time.monotonic() - started
        if route != '/metrics':
            with self.lock:
                key = (route, status)
                self.counts[key] = self.counts.get(key, 0) + 1
                self.seconds += duration
            self.logger(json.dumps({'event': 'http_request', 'route': route,
                                    'status': status, 'duration_ms': round(duration * 1000, 3)}))
        reasons = {200: 'OK', 400: 'Bad Request', 404: 'Not Found',
                   405: 'Method Not Allowed', 500: 'Internal Server Error', 503: 'Service Unavailable'}
        headers = [('Content-Type', content_type), ('Content-Length', str(len(body))),
                   ('Cache-Control', 'no-store'), ('X-Content-Type-Options', 'nosniff')]
        if status == 405:
            headers.append(('Allow', 'GET'))
        start_response(f'{status} {reasons[status]}', headers)
        return [body]


application = Application()
