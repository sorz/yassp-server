from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from http.client import parse_headers
import json


class PushAPIHTTPRequestHandler(BaseHTTPRequestHandler):
    key = 'test123'

    def do_POST(self):
        url = urlparse(self.path)
        qs = parse_qs(url.query)
        if qs.get('token', [''])[0] != self.key:
            self.send_error(401, 'Not Authorized', 'No or wrong token.')
            return
        if url.path != '/instances':
            self.send_error(404)
            return
        body = self.rfile.read(int(self.headers.getheader('content-length')))
        req = json.loads(body)
        print(req)

        self.send_response(200)
        self.end_headers()


class YaSSPAPIServer:
    def __init__(self, yassp, key, bind=('', 8080)):
        self._key = key
        self._yassp = yassp
        PushAPIHTTPRequestHandler.key = key
        self._server = HTTPServer(bind, PushAPIHTTPRequestHandler)

    def serve_forever(self):
        self._server.serve_forever()


def main():
    s = YaSSPAPIServer(None, 'test123')
    s.serve_forever()

if __name__ == '__main__':
    main()
