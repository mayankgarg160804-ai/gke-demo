from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import socket

PORT = int(os.environ.get("PORT", "8080"))

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        hostname = socket.gethostname()
        body = (
            "Hello from GKE!\n"
            f"Version: v1\n"
            f"Hostname: {hostname}\n"
            f"Path: {self.path}\n"
        ).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Listening on port {PORT}")
    print("Version v2")
    server.serve_forever()