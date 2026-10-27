#!/usr/bin/env python
"""eEagle VPN 2API demo — read-only proxy over the vendor API.

Env: EAGLE_API_KEY (x-api-key from the target APK). No credentials are cached
or persisted by this server; every /api/config call re-signs upstream.
"""
import json
import os
import ssl
import urllib.error
import urllib.request

from flask import Flask, jsonify, request

BASE = "https://prod-api.eeaglevpn.com"
API_KEY = os.environ.get("EAGLE_API_KEY", "")
USER_ID = "11111111-2222-3333-4444-555555555555"
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

app = Flask(__name__, static_folder=None)
_servers_cache = None  # only the node list (no credentials)


def upstream(path):
    r = urllib.request.Request(BASE + path)
    r.add_header("x-api-key", API_KEY)
    r.add_header("x-user-id", USER_ID)
    try:
        resp = urllib.request.urlopen(r, context=CTX, timeout=25)
        return resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors="replace")[:300]


def servers():
    global _servers_cache
    if _servers_cache is None:
        s, body = upstream("/server")
        if s != 200:
            return None
        _servers_cache = json.loads(body)["data"]
    return _servers_cache


@app.get("/")
def index():
    return open(os.path.join(os.path.dirname(__file__), "demo.html"), encoding="utf-8").read()


@app.get("/api/servers")
def api_servers():
    data = servers()
    if data is None:
        return jsonify({"success": False, "error": "upstream unavailable"}), 502
    out = []
    for tier in ("free", "premium"):
        for c in data.get(tier, []):
            for loc in c.get("locations", []):
                out.append({
                    "tier": tier, "country": c["countryName"], "city": loc["name"],
                    "ip": loc.get("serverUrl"), "protocols": loc.get("availableProtocol"),
                    "category": loc.get("category"), "id": loc["_id"],
                })
    return jsonify({"success": True, "count": len(out), "servers": out})


@app.get("/api/config")
def api_config():
    sid = request.args.get("id", "")
    proto = request.args.get("type", "wireguard")
    if not sid or not sid.isalnum():
        return jsonify({"success": False, "error": "bad id"}), 400
    s, body = upstream(f"/configuration_file?id={sid}&type={proto}&app_version=2.12.9")
    return app.response_class(body, status=s, mimetype="text/plain")


if __name__ == "__main__":
    if not API_KEY:
        raise SystemExit("set EAGLE_API_KEY first")
    app.run(host="0.0.0.0", port=8902)
