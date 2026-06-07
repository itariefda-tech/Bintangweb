from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path


HOST = "127.0.0.1"
PORT = int(os.environ.get("PORT", "8000"))
ROOT = Path(__file__).resolve().parent


class StaticHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def main():
    port = PORT
    server = None
    while server is None:
        try:
            server = ThreadingHTTPServer((HOST, port), StaticHandler)
        except OSError:
            port += 1

    print(f"Bintang Computer Feira dev server: http://{HOST}:{port}")
    if port != PORT:
        print(f"Port {PORT} was busy, using http://{HOST}:{port} instead.")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
