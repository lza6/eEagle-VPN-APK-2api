#!/usr/bin/env python
"""eEagle VPN node harvester — pulls the live server list and per-node configs.

Credentials are NOT embedded: pass your own API key via --api-key or EAGLE_API_KEY.
"""
import argparse
import json
import os
import ssl
import sys
import urllib.error
import urllib.request

BASE = "https://prod-api.eeaglevpn.com"
PROTOCOLS = ["wireguard", "ovpn", "ikev2", "ipsec", "amneziawg"]
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


def req(path, api_key, user_id, timeout=25):
    r = urllib.request.Request(BASE + path)
    r.add_header("x-api-key", api_key)
    r.add_header("x-user-id", user_id)
    try:
        resp = urllib.request.urlopen(r, context=CTX, timeout=timeout)
        return resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors="replace")[:300]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--api-key", default=os.environ.get("EAGLE_API_KEY", ""),
                    help="x-api-key value (from the target APK interceptor)")
    ap.add_argument("--user-id", default="11111111-2222-3333-4444-555555555555")
    ap.add_argument("--out", default="./harvest")
    ap.add_argument("--types", default="wireguard,ovpn", help="comma-separated config types")
    args = ap.parse_args()
    if not args.api_key:
        sys.exit("need --api-key or EAGLE_API_KEY")

    os.makedirs(args.out, exist_ok=True)
    s, body = req("/server", args.api_key, args.user_id)
    if s != 200:
        sys.exit(f"/server failed: {s} {body[:200]}")
    data = json.loads(body)["data"]
    json.dump(data, open(os.path.join(args.out, "servers.json"), "w"), indent=2)

    wanted = [t.strip() for t in args.types.split(",")]
    n = 0
    for tier in ("free", "premium"):
        for country in data.get(tier, []):
            for loc in country.get("locations", []):
                for proto in wanted:
                    qs = f"id={loc['_id']}&type={proto}&app_version=2.12.9"
                    s, body = req("/configuration_file?" + qs, args.api_key, args.user_id)
                    if s == 200:
                        name = f"{tier}_{country['countryName']}_{loc['name']}_{proto}.conf".replace(" ", "_")
                        open(os.path.join(args.out, name), "w").write(body)
                        n += 1
                        print("OK", name)
    print(f"total configs: {n}")


if __name__ == "__main__":
    main()
