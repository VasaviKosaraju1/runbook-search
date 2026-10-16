"""Exercise real HTTP requests against a loopback server on an ephemeral port."""
import json
from pathlib import Path
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import urlopen
from app import create_server
from build_demo import build


class HttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = create_server(port=0)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def get(self, path):
        try:
            with urlopen(self.base + path, timeout=5) as response:
                return response.status, response.read()
        except HTTPError as error:
            return error.code, error.read()

    def test_health(self):
        status, body = self.get('/health')
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body), {'status': 'ok', 'chunks': 6})

    def test_search_returns_source(self):
        status, body = self.get('/api/search?q=OOMKilled')
        self.assertEqual(status, 200)
        self.assertTrue(json.loads(body)['results'][0]['source'].startswith('runbook-memory.md'))

    def test_blank_query_rejected(self):
        self.assertEqual(self.get('/api/search?q=')[0], 400)

    def test_long_query_rejected(self):
        self.assertEqual(self.get('/api/search?q=' + 'x' * 501)[0], 400)

    def test_invalid_limits(self):
        for limit in ('0', '101', 'nope'):
            with self.subTest(limit=limit):
                self.assertEqual(self.get('/api/search?q=memory&limit=' + limit)[0], 400)

    def test_no_match_is_successful_empty_result(self):
        self.assertEqual(json.loads(self.get('/api/search?q=zzzzzz')[1]), {'results': []})

    def test_demo_html(self):
        status, body = self.get('/')
        self.assertEqual(status, 200)
        self.assertIn(b'Runbook Search', body)

    def test_private_paths_not_served(self):
        for path in ('/search.py', '/README.md', '/.env', '/../../etc/passwd'):
            with self.subTest(path=path):
                self.assertEqual(self.get(path)[0], 404)

    def test_dataset_is_generated_from_repository_fixtures(self):
        folder = Path(__file__).parent
        expected = build(folder)
        self.assertEqual(json.loads((folder / 'runbooks.json').read_text()), expected)


if __name__ == '__main__':
    unittest.main()
