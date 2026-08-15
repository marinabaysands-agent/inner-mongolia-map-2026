"""Refresh driving geometry in routes.json without overwriting day details.

Usage:
  AMAP_API_KEY=... python3 fetch_routes.py
"""
import json
import os
import urllib.parse
import urllib.request
from pathlib import Path

KEY = os.environ["AMAP_API_KEY"]
HERE = Path(__file__).resolve().parent
ROUTES_FILE = HERE / "routes.json"

COORDS = {
    "大连": (121.614786, 38.913962),
    "鞍山": (122.99460, 41.10865),
    "白城": (122.83871, 45.61960),
    "乌兰浩特": (122.093309, 46.072233),
    "阿尔山": (119.943577, 47.177440),
    "满洲里": (117.379762, 49.597064),
    "额尔古纳": (120.190032, 50.243102),
    "根河": (121.520606, 50.780224),
    "莫尔道嘎": (120.696367, 51.669629),
    "老鹰嘴": (120.520000, 51.100000),
    "室韦": (119.936034, 51.567488),
    "海拉尔": (119.736923, 49.212349),
    "齐齐哈尔": (123.918186, 47.354348),
    "长春": (125.323544, 43.817072),
}

SEGMENTS = [
    ("Day 1", "大连", "鞍山", [], "outbound"),
    ("Day 2", "鞍山", "白城", [], "outbound"),
    ("Day 3", "白城", "阿尔山", ["乌兰浩特"], "outbound"),
    ("Day 5", "阿尔山", "满洲里", [], "loop"),
    ("Day 8", "满洲里", "额尔古纳", [], "loop"),
    ("Day 10", "额尔古纳", "莫尔道嘎", ["根河"], "loop"),
    ("Day 11", "莫尔道嘎", "室韦", ["老鹰嘴"], "loop"),
    ("Day 12", "室韦", "海拉尔", [], "loop"),
    ("Day 14", "海拉尔", "齐齐哈尔", [], "return"),
    ("Day 15", "齐齐哈尔", "长春", [], "return"),
    ("Day 16", "长春", "大连", [], "return"),
]


def fetch(start, end, waypoints):
    params = {
        "key": KEY,
        "origin": ",".join(map(str, COORDS[start])),
        "destination": ",".join(map(str, COORDS[end])),
        "strategy": "32",
        "extensions": "all",
        "output": "JSON",
    }
    if waypoints:
        params["waypoints"] = ";".join(",".join(map(str, COORDS[w])) for w in waypoints)
    url = "https://restapi.amap.com/v3/direction/driving?" + urllib.parse.urlencode(params)
    data = json.loads(urllib.request.urlopen(url, timeout=30).read())
    if data.get("status") != "1":
        raise RuntimeError(f"Amap error: {data.get('info')} ({data.get('infocode')})")
    path = data["route"]["paths"][0]
    points = []
    for step in path["steps"]:
        for point in step["polyline"].split(";"):
            if point:
                lng, lat = point.split(",")
                points.append([float(lat), float(lng)])
    return {
        "distance_km": int(path["distance"]) / 1000,
        "duration_h": int(path["duration"]) / 3600,
        "polyline": points,
    }


def main():
    current = json.loads(ROUTES_FILE.read_text())
    segments = []
    for label, start, end, waypoints, phase in SEGMENTS:
        print(f"Fetching {label}: {start} -> {end}")
        route = fetch(start, end, waypoints)
        route.update({
            "day_label": label,
            "from": start,
            "to": end,
            "waypoints": waypoints,
            "phase": phase,
        })
        segments.append(route)
    ROUTES_FILE.write_text(json.dumps({"segments": segments, "days": current["days"]}, ensure_ascii=False, separators=(",", ":")))
    print(f"Updated {ROUTES_FILE}; total {sum(x['distance_km'] for x in segments):.0f} km")


if __name__ == "__main__":
    main()
