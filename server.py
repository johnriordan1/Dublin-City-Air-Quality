#!/usr/bin/env python3
"""
Dublin Air Quality Live Monitor Web Server
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
import logging

PORT = 8080
CACHE_TTL = 300  # seconds (5 minutes)

# Enable detailed logging for troubleshooting
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

cache = {
    "monitors": [],
    "last_fetched": 0
}

DATA_SOURCES = [
    {
        "url": "https://dublincityairandnoise.ie/assets/php/get-monitors.php",
        "headers": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    }
]

def fetch_live_data():
    """Fetch live air quality monitor data from Dublin City Council API with TTL caching."""
    now = time.time()
    if cache["monitors"] and (now - cache["last_fetched"] < CACHE_TTL):
        logger.info(f"Serving cached monitor data ({int(now - cache['last_fetched'])}s old)")
        return cache["monitors"]

    headers = {"User-Agent": "Mozilla/5.0"}
    req = urllib.request.Request("https://dublincityairandnoise.ie/assets/php/get-monitors.php", headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            if response.status == 200:
                raw = response.read().decode("utf-8")
                logger.info(f"Fetched {len(raw)} bytes from API")
                
                # Parse the JSON response
                parsed = json.loads(raw)
                
                # Filter out noise monitors
                if isinstance(parsed, list):
                    air_monitors = [m for m in parsed if m.get("monitor_type", {}).get("category") != "noise"]
                    logger.info(f"Parsed {len(air_monitors)} air monitors (filtered out {len(parsed) - len(air_monitors)} noise monitors)")
                    cache["monitors"] = air_monitors
                    cache["last_fetched"] = time.time()
                    return air_monitors
                
                elif isinstance(parsed, dict) and "data" in parsed:
                    raw_list = parsed.get("data", [])
                    air_monitors = [m for m in raw_list if m.get("monitor_type", {}).get("category") != "noise"]
                    logger.info(f"Parsed {len(air_monitors)} air monitors from wrapped response")
                    cache["monitors"] = air_monitors
                    cache["last_fetched"] = time.time()
                    return air_monitors
                    
                else:
                    logger.warning(f"Unexpected response format: {type(parsed)}")
                    cache["monitors"] = []
                    cache["last_fetched"] = time.time()
                    return []
                    
    except urllib.error.URLError as e:
        logger.error(f"Network error - could not connect to the external API feed: {e}")
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response from API: {e}")
    except Exception as e:
        logger.error(f"Unexpected error fetching live feed: {type(e).__name__}: {e}")
    
    # Return cached data if available (even if empty)
    logger.info("Returning cached data (may be empty or stale)")
    return cache["monitors"]

class AirQualityHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Enable CORS for local testing
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
                "total_monitors": len(monitors),
                "data": monitors
            }).encode('utf-8')

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(payload)))
            self.send_header('Cache-Control', 'public, max-age=300, stale-while-revalidate=60')
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
