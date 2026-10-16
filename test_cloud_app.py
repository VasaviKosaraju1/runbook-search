import io
import json
from pathlib import Path
import tempfile
import unittest
from wsgiref.util import setup_testing_defaults
from wsgiref.validate import validator
from cloud_app import Application


class CloudAppTests(unittest.TestCase):
    def setUp(self):
        self.logs = []
        self.app = Application(logger=self.logs.append)

    def call(self, path='/', query='', method='GET'):
        environ = {}
        setup_testing_defaults(environ)
        environ.update(PATH_INFO=path, QUERY_STRING=query, REQUEST_METHOD=method,
                       **{'wsgi.input': io.BytesIO()})
        response = {}
        def start(status, headers, exc_info=None):
            response.update(status=int(status.split()[0]), headers=dict(headers))
        result = validator(self.app)(environ, start)
        try:
            response['body'] = b''.join(result)
        finally:
            if hasattr(result, 'close'):
                result.close()
        return response

    def test_health_and_search(self):
        self.assertEqual(self.call('/health')['status'], 200)
        result = json.loads(self.call('/api/search', 'q=OOMKilled')['body'])
        self.assertTrue(result['results'][0]['source'].startswith('runbook-memory.md'))

    def test_bad_inputs(self):
        for query in ('q=', 'q=' + 'x' * 501, 'q=memory&limit=0',
                      'q=memory&limit=101', 'q=memory&limit=bad'):
            self.assertEqual(self.call('/api/search', query)['status'], 400)

    def test_unknown_and_private_paths(self):
        for path in ('/.env', '/cloud_app.py', '/../search.py', '/unknown-secret'):
            self.assertEqual(self.call(path)['status'], 404)
        self.assertNotIn('unknown-secret', ''.join(self.logs))

    def test_methods_and_security_headers(self):
        response = self.call('/health', method='POST')
        self.assertEqual(response['status'], 405)
        self.assertEqual(response['headers']['Allow'], 'GET')
        self.assertEqual(response['headers']['X-Content-Type-Options'], 'nosniff')

    def test_metrics_and_log_privacy(self):
        self.call('/api/search', 'q=SECRET-MARKER')
        metrics = self.call('/metrics')['body'].decode()
        self.assertIn('route="/api/search",status="200"} 1', metrics)
        self.assertNotIn('SECRET-MARKER', metrics + ''.join(self.logs))
        self.assertEqual(len(self.logs), 1)  # scrapes do not create recursive traffic

    def test_assets(self):
        self.assertIn(b'Runbook Search', self.call()['body'])
        self.assertEqual(self.call('/web.js')['status'], 200)
        self.assertIsInstance(json.loads(self.call('/runbooks.json')['body']), list)

    def test_empty_corpus_unready(self):
        with tempfile.TemporaryDirectory() as folder:
            self.app = Application(Path(folder), logger=self.logs.append)
            self.assertEqual(self.call('/health')['status'], 503)

    def test_internal_error_is_generic(self):
        with tempfile.TemporaryDirectory() as folder:
            self.app = Application(Path(folder), logger=self.logs.append)
            result = self.call('/')
            self.assertEqual(result['status'], 500)
            self.assertEqual(json.loads(result['body']), {'error': 'internal error'})


if __name__ == '__main__':
    unittest.main()
