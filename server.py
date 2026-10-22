#!/usr/bin/env python3
"""
Dublin Air & Noise Quality Live Monitor Web Server
Proxies and caches live sensor telemetry from Dublin City Council / Smart Dublin / Sonitus dataset.
"""

import http.server
import socketserver
import urllib.request
import urllib.error
import json
import time
import os
import sys

PORT = 8080
CACHE_TTL = 90  # seconds

cache = {
    "monitors": None,
    "last_fetched": 0
}

DATA_SOURCES = [
    {
        "url": "https://dublincityairandnoise.ie/assets/php/get-monitors.php",
        "headers": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    }
]

def fetch_live_data():
    now = time.time()
    if cache["monitors"] and (now - cache["last_fetched"] < CACHE_TTL):
        return cache["monitors"]

    headers = {"User-Agent": "Mozilla/5.0"}
    req = urllib.request.Request("https://dublincityairandnoise.ie/assets/php/get-monitors.php", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            if response.status == 200:
                raw = response.read().decode("utf-8")
                parsed = json.loads(raw)
                cache["monitors"] = parsed
                cache["last_fetched"] = now
                return parsed
    except Exception as e:
        print(f"Error fetching live feed: {e}", file=sys.stderr)
        if cache["monitors"]:
            return cache["monitors"]
        return []

class AirQualityHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Enable CORS for local testing if requested
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

    def do_GET(self):
        if self.path == '/api/monitors':
            monitors = fetch_live_data()
            payload = json.dumps({
                "status": "success",
                "source": "Smart Dublin / Dublin City Council Sonitus Dataset",
                "data_gov_ie_url": "https://data.gov.ie/dataset/sonitus",
                "smart_dublin_url": "https://data.smartdublin.ie/dataset/sonitus",
                "portal_url": "https://dublincityairandnoise.ie/",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
                "total_monitors": len(monitors) if monitors else 0,
                "data": monitors
            }).encode('utf-8')

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(payload)))
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(payload)
            return

        return super().do_GET()

def main():
    web_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(web_dir)
    print(f"Serving Dublin Air Quality Dashboard at http://localhost:{PORT}")
    with socketserver.TCPServer(("", PORT), AirQualityHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")

if __name__ == '__main__':
    main()
