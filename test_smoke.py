import io
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from smoke_test import verify


def response(body):
    return io.BytesIO(body)


class SmokeTests(unittest.TestCase):
    def responses(self):
        return [response(b'{"status":"ok","chunks":6}'),
                response(b'{"results":[{"source":"runbook-memory.md#1"}]}'),
                response(b'runbook_http_requests_total 1'),
                HTTPError('http://127.0.0.1/.env', 404, 'Not Found', {}, None)]

    @patch('smoke_test.time.sleep')
    @patch('smoke_test.urlopen')
    def test_startup_reset_is_retried(self, open_url, sleep):
        open_url.side_effect = [ConnectionResetError('starting')] + self.responses()
        verify('http://127.0.0.1:8000')
        sleep.assert_called_once_with(2)
        self.assertEqual(open_url.call_count, 5)

    @patch('smoke_test.time.sleep')
    @patch('smoke_test.urlopen', side_effect=ConnectionResetError('unavailable'))
    def test_readiness_has_bounded_retries(self, open_url, sleep):
        with self.assertRaisesRegex(RuntimeError, 'Readiness'):
            verify('http://127.0.0.1:8000')
        self.assertEqual(open_url.call_count, 30)

    @patch('smoke_test.urlopen')
    def test_private_path_success_fails_check(self, open_url):
        cases = self.responses()
        cases[-1] = response(b'should not be public')
        open_url.side_effect = cases
        with self.assertRaisesRegex(RuntimeError, 'Private-path'):
            verify('http://127.0.0.1:8000')

    @patch('smoke_test.urlopen')
    def test_missing_retrieval_source_fails_check(self, open_url):
        open_url.side_effect = [response(b'{"status":"ok","chunks":6}'),
                                response(b'{"results":[]}')]
        with self.assertRaisesRegex(RuntimeError, 'Search source'):
            verify('http://127.0.0.1:8000')


if __name__ == '__main__':
    unittest.main()
