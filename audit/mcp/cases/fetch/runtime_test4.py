"""CASE 002 补测：redirect→内网 / rebinding 模拟 / allow_private_ips=True
标注：D 组属单元级（直接调请求钩子）；E 组是模拟，不是真实 DNS rebinding；
F 组是端到端（本机 HTTP server + 真 client）。
"""
import asyncio
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import httpx
from mcp.server.mcpserver.exceptions import ToolError

for _k in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy", "NO_PROXY", "no_proxy"):
    os.environ.pop(_k, None)  # 环境里的 no_proxy 带 [::1] 会让 httpx 0.28 建 client 时报 Invalid port

import mcp_server_fetch.server as S
import mcp_server_fetch.pinning as P

HITS = []


class H(BaseHTTPRequestHandler):
    def do_GET(self):
        HITS.append(self.path)
        if self.path == "/r1":
            self.send_response(302)
            self.send_header("Location", "http://169.254.169.254/latest/meta-data/")
            self.end_headers()
        elif self.path == "/r2":
            self.send_response(302)
            self.send_header("Location", "/ok")
            self.end_headers()
        else:
            body = b"ok-private"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    def log_message(self, *a):
        pass


async def d_group():
    print("== D 重定向目标：请求钩子逐地址判定（单元级） ==")
    targets = [
        ("D1", "http://169.254.169.254/latest/meta-data/"),
        ("D2", "http://127.0.0.1:8765/"),
        ("D3", "http://100.100.100.200/latest/meta-data/"),
        ("D4", "http://[::1]/"),
        ("D5", "http://10.0.0.1/"),
        ("D6", "http://93.184.216.34/"),
    ]
    for tag, url in targets:
        req = httpx.Request("GET", url)
        try:
            await S._refuse_private_destination(req)
            print(f"{tag} {url} -> ALLOWED")
        except ToolError as e:
            print(f"{tag} {url} -> REFUSED: {str(e)[:80]}")


async def d2_group():
    print("== D7 重定向跳转是否逐跳经过请求钩子（端到端，记录器代替守卫） ==")
    seen = []

    async def recorder(request):
        seen.append(str(request.url))

    client = S.make_client(None, allow_private_ips=True)
    async with client as c:
        c.event_hooks = {"request": [recorder]}
        try:
            async with S.stream_get(c, "http://127.0.0.1:8765/r1", "test-agent") as r:
                print("D7 status:", r.status_code)
        except Exception as e:
            print("D7 exception:", type(e).__name__, str(e)[:80])
    print("D7 hops seen by hook:", seen)


async def e_group():
    print("== E rebinding（模拟：首查 public → 连接期 private，走真 client） ==")
    calls = {"n": 0}
    real_resolve = S._resolve_host
    real_vet = S._refuse_private_addresses
    vetted = {"n": 0}

    async def fake_resolve(host):
        calls["n"] += 1
        return ["93.184.216.34"] if calls["n"] % 2 == 1 else ["127.0.0.1"]

    def spy_vet(host, addresses):
        vetted["n"] += 1
        return real_vet(host, addresses)

    S._resolve_host = fake_resolve
    S._refuse_private_addresses = spy_vet
    try:
        client = S.make_client(None, allow_private_ips=False)
        async with client as c:
            # 与 server 的取页路径一致：钩子由取页函数挂上，make_client 只负责钉地址
            c.event_hooks = {"request": [S._refuse_private_destination]}
            try:
                async with S.stream_get(c, "http://rebind.test:8080/", "test-agent") as r:
                    print("E1 端到端 -> 未拦住, status", r.status_code)
            except ToolError as e:
                print("E1 端到端 -> REFUSED:", str(e)[:85])
            except Exception as e:
                print("E1 端到端 -> 其它异常:", type(e).__name__, str(e)[:60])
        print("E2 解析次数:", calls["n"], "| 连接期 vet 次数:", vetted["n"])
    finally:
        S._resolve_host = real_resolve
        S._refuse_private_addresses = real_vet
    src = open(S.__file__, encoding="utf-8").read()
    print("E3 源码: vet 传进 pin_direct_connections =", "_refuse_private_addresses" in src and "pin_direct_connections(" in src)


async def f_group():
    print("== F allow_private_ips=True（端到端） ==")
    async with S.make_client(None, allow_private_ips=True) as c:
        async with S.stream_get(c, "http://127.0.0.1:8765/ok", "test-agent") as r:
            body = await r.aread()
            print("F1 allow=True 127.0.0.1 ->", r.status_code, body[:20])
    async with S.make_client(None, allow_private_ips=False) as c:
        try:
            async with S.stream_get(c, "http://127.0.0.1:8765/ok", "test-agent") as r:
                print("F2 allow=False 127.0.0.1 ->", r.status_code)
        except ToolError as e:
            print("F2 allow=False 127.0.0.1 -> REFUSED:", str(e)[:70])


async def main():
    srv = HTTPServer(("127.0.0.1", 8765), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    await d_group()
    await d2_group()
    await e_group()
    await f_group()
    srv.shutdown()


asyncio.run(main())
