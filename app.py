"""Local demo server with a search API and health endpoint. Not a production server."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from search import SearchIndex, load_documents


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, index, directory, **kwargs):
        self.index = index
        super().__init__(*args, directory=directory, **kwargs)

    def send_json(self, status, value):
        payload = json.dumps(value).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(payload)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        parsed = urlsplit(self.path)
        if parsed.path == '/health':
            self.send_json(200, {'status': 'ok', 'chunks': len(self.index.documents)})
        elif parsed.path == '/api/search':
            params = parse_qs(parsed.query, keep_blank_values=True)
            query = params.get('q', [''])[0].strip()
            if not query or len(query) > 500:
                self.send_json(400, {'error': 'q must contain 1 to 500 characters'})
                return
            try:
                limit = int(params.get('limit', ['3'])[0])
                hits = self.index.search(query, limit)
            except ValueError:
                self.send_json(400, {'error': 'limit must be an integer between 1 and 100'})
                return
            self.send_json(200, {'results': hits})
        elif parsed.path in ('/', '/index.html', '/web.js', '/runbooks.json'):
            super().do_GET()
        else:
            self.send_json(404, {'error': 'not found'})

    def do_HEAD(self):
        self.send_error(405, 'Use GET')

    def log_message(self, *args):
        # Do not write search queries to the terminal log.
        pass


def create_server(host='127.0.0.1', port=8000, directory=None):
    directory = Path(directory or Path(__file__).parent).resolve()
    index = SearchIndex(load_documents(directory))
    handler = partial(Handler, index=index, directory=str(directory))
    return ThreadingHTTPServer((host, port), handler)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    with create_server(args.host, args.port) as server:
        print(f'Runbook Search: http://{args.host}:{server.server_port}')
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()
