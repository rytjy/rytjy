import asyncio, threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import httpx
from mcp_server_fetch.server import (_is_public_address, _refuse_private_addresses, make_client)

PORT = 8765

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        body = b'<html><body><h1>internal host</h1></body></html>'
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def log_message(self, *a): pass

async def main():
    print('== A. classify ==')
    for a in ['127.0.0.1','169.254.169.254','10.0.0.1','100.100.100.200','::1','93.184.216.34']:
        print('  %-20s public=%s' % (a, _is_public_address(a)))
    print('== B. refuse_private_addresses ==')
    for name, addrs in [('loopback',['127.0.0.1']), ('metadata',['169.254.169.254']), ('public',['93.184.216.34'])]:
        try:
            _refuse_private_addresses('t', addrs); print('  %-9s ALLOWED' % name)
        except BaseException as e:
            print('  %-9s REFUSED -> %s' % (name, type(e).__name__))
    print('== C. real client (no proxy) ==')
    async with make_client(None, False) as c:
        for url in ['http://127.0.0.1:%d/' % PORT, 'http://169.254.169.254/latest/meta-data/', 'file:///etc/passwd']:
            try:
                r = await c.get(url)
                print('  %-45s -> %s len=%d' % (url, r.status_code, len(r.content)))
            except BaseException as e:
                print('  %-45s -> %s: %s' % (url, type(e).__name__, str(e)[:60]))

httpd = HTTPServer(('127.0.0.1', PORT), H)
threading.Thread(target=httpd.serve_forever, daemon=True).start()
asyncio.run(main())