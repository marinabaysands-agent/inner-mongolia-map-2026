import urllib.request, urllib.parse, json, os

KEY = "395e02feced0c87afb730fd870a06e85"

COORDS = {
  "大连":     (121.614786, 38.913962),
  "通辽":     (122.243309, 43.653566),
  "乌兰浩特": (122.093309, 46.072233),
  "阿尔山":   (119.943577, 47.177440),
  "满洲里":   (117.379762, 49.597064),
  "额尔古纳": (120.190032, 50.243102),
  "根河":     (121.520606, 50.780224),
  "莫尔道嘎": (120.696367, 51.669629),
  "老鹰嘴":   (120.520000, 51.100000),
  "室韦":     (119.936034, 51.567488),
  "海拉尔":   (119.736923, 49.212349),
  "齐齐哈尔": (123.918186, 47.354348),
  "长春":     (125.323544, 43.817072),
  "盘锦":     (122.06957, 41.124484),
}

SEGMENTS = [
  ("Day 1: 大连 → 通辽",                "大连", "通辽", [], "outbound"),
  ("Day 2: 通辽 → 阿尔山 (经乌兰浩特)",  "通辽", "阿尔山", ["乌兰浩特"], "outbound"),
  ("Day 4: 阿尔山 → 满洲里",             "阿尔山", "满洲里", [], "loop"),
  ("Day 6: 满洲里 → 额尔古纳",          "满洲里", "额尔古纳", [], "loop"),
  ("Day 8: 额尔古纳 → 莫尔道嘎 (经根河)","额尔古纳", "莫尔道嘎", ["根河"], "loop"),
  ("Day 9: 莫尔道嘎 → 室韦 (经老鹰嘴)",  "莫尔道嘎", "室韦", ["老鹰嘴"], "loop"),
  ("Day 10: 室韦 → 海拉尔",              "室韦", "海拉尔", [], "loop"),
  ("Day 12: 海拉尔 → 齐齐哈尔",          "海拉尔", "齐齐哈尔", [], "return"),
  ("Day 13: 齐齐哈尔 → 长春",            "齐齐哈尔", "长春", [], "return"),
  ("Day 14: 长春 → 盘锦",                "长春", "盘锦", [], "return"),
  ("Day 15: 盘锦 → 大连",                "盘锦", "大连", [], "return"),
]

def fetch(a, b, waypoints):
    params = {
        "key": KEY,
        "origin": f"{COORDS[a][0]},{COORDS[a][1]}",
        "destination": f"{COORDS[b][0]},{COORDS[b][1]}",
        "strategy": "32",
        "extensions": "all",
        "output": "JSON",
    }
    if waypoints:
        params["waypoints"] = ";".join(f"{COORDS[w][0]},{COORDS[w][1]}" for w in waypoints)
    url = "https://restapi.amap.com/v3/direction/driving?" + urllib.parse.urlencode(params)
    d = json.loads(urllib.request.urlopen(url, timeout=30).read())
    if d.get("status") != "1":
        return {"error": d.get("info")}
    path = d["route"]["paths"][0]
    pts = []
    for step in path["steps"]:
        for p in step["polyline"].split(";"):
            if not p:
                continue
            lng, lat = p.split(",")
            pts.append([float(lat), float(lng)])
    return {
        "distance_km": int(path["distance"]) / 1000,
        "duration_h": int(path["duration"]) / 3600,
        "polyline": pts,
    }

out = []
for label, a, b, wp, phase in SEGMENTS:
    print(f"Fetching {label}...")
    r = fetch(a, b, wp)
    if "error" in r:
        print(f"  ERROR: {r['error']} -- fallback straight line")
        pts = [[COORDS[a][1], COORDS[a][0]]]
        for w in wp:
            pts.append([COORDS[w][1], COORDS[w][0]])
        pts.append([COORDS[b][1], COORDS[b][0]])
        r = {"distance_km": None, "duration_h": None, "polyline": pts, "fallback": True}
    r["label"] = label
    r["from"] = a
    r["to"] = b
    r["waypoints"] = wp
    r["phase"] = phase
    out.append(r)
    print(f"  {r.get('distance_km', 'N/A')}km / {r.get('duration_h', 'N/A')}h")

# 16 天版：每一天详情
DAYS = [
  {"day": 1, "date": "9/19 六", "name": "大连 → 通辽", "lat": COORDS["通辽"][1], "lng": COORDS["通辽"][0],
   "phase": "outbound", "drive": "628km / 6.4h",
   "highlights": ["出发日，全程高速", "晚到通辽，纯过夜"],
   "food": "通辽随便找一家蒙式烤肉/牛肉面",
   "stay": "通辽市区连锁酒店",
   "tips": "上高速前加满油；出发时间建议早 7 点前"},
  {"day": 2, "date": "9/20 日", "name": "通辽 → 乌兰浩特 → 阿尔山",
   "lat": COORDS["阿尔山"][1], "lng": COORDS["阿尔山"][0],
   "phase": "outbound", "drive": "617km / 7.4h",
   "highlights": ["乌兰浩特午餐+短逛", "傍晚到阿尔山，住天池服务区"],
   "food": "乌兰浩特蒙餐；晚餐阿尔山温泉鱼",
   "stay": "阿尔山天池服务区客栈（省第二天 1h 车程）",
   "tips": "阿尔山住宿旺季紧张，提前 2 个月订"},
  {"day": 3, "date": "9/21 一", "name": "阿尔山森林公园",
   "lat": COORDS["阿尔山"][1]+0.1, "lng": COORDS["阿尔山"][0]-0.3,
   "phase": "loop", "drive": "园内 <100km",
   "highlights": ["驼峰岭天池（最美）", "大峡谷", "杜鹃湖", "石塘林"],
   "food": "景区门口温泉鱼、烤羊排",
   "stay": "同 Day 2 天池服务区",
   "tips": "门票 180+观光车 105=285/人，48h 有效；早起进园避人"},
  {"day": 4, "date": "9/22 二", "name": "阿尔山 → 满洲里",
   "lat": COORDS["满洲里"][1], "lng": COORDS["满洲里"][0],
   "phase": "loop", "drive": "427km / 5.8h",
   "highlights": ["草原公路秋色", "傍晚到满洲里，看国门夜景"],
   "food": "满洲里俄式西餐（俄罗斯厨师做的）",
   "stay": "满洲里俄式主题酒店（推荐）",
   "tips": "满洲里加油站少，进城前加满"},
  {"day": 5, "date": "9/23 三", "name": "满洲里 + 俄罗斯半日",
   "lat": COORDS["满洲里"][1]+0.05, "lng": COORDS["满洲里"][0]-0.05,
   "phase": "loop", "drive": "0-100km",
   "highlights": ["套娃景区", "过境后贝加尔斯克半日游", "国门+41号界碑"],
   "food": "俄罗斯午餐 borscht+黑面包",
   "stay": "同 Day 4 满洲里",
   "tips": "俄罗斯免签至 2027-12-31；护照带好；建议报当地一日游团（¥300-500/人，含车+导游+餐）"},
  {"day": 6, "date": "9/24 四", "name": "满洲里 → 额尔古纳",
   "lat": COORDS["额尔古纳"][1], "lng": COORDS["额尔古纳"][0],
   "phase": "loop", "drive": "256km / 3.6h",
   "highlights": ["短程日，下午到", "额尔古纳湿地（亚洲最大湿地）看晚霞"],
   "food": "俄罗斯族列巴+奶茶；晚餐俄式风味",
   "stay": "古纳湾酒店 ¥470/晚 或类似河景房",
   "tips": "湿地日落最美，18-19 点到；带保暖外套"},
  {"day": 7, "date": "9/25 五", "name": "额尔古纳深度",
   "lat": COORDS["额尔古纳"][1]+0.03, "lng": COORDS["额尔古纳"][0]-0.05,
   "phase": "loop", "drive": "<100km",
   "highlights": ["湿地清晨雾", "俄罗斯族家访", "额尔古纳博物馆"],
   "food": "俄餐+野生蓝莓",
   "stay": "同 Day 6",
   "tips": "早起 6 点看湿地雾景 ⭐"},
  {"day": 8, "date": "9/26 六", "name": "额尔古纳 → 根河 → 莫尔道嘎",
   "lat": COORDS["莫尔道嘎"][1], "lng": COORDS["莫尔道嘎"][0],
   "phase": "loop", "drive": "311km / 4.8h",
   "highlights": ["根河兴安神鹿园（喂驯鹿）", "莫尔道嘎大兴安岭秋色"],
   "food": "根河冷面；莫尔道嘎林区野味",
   "stay": "莫尔道嘎森林人家",
   "tips": "神鹿园门票 ¥120，喂食体验超值"},
  {"day": 9, "date": "9/27 日", "name": "莫尔道嘎 → 老鹰嘴 → 室韦",
   "lat": COORDS["室韦"][1], "lng": COORDS["室韦"][0],
   "phase": "loop", "drive": "~130km / 3h（边境路）",
   "highlights": ["莫尔道嘎森林公园（一目九岭）", "老鹰嘴", "临江看日落", "室韦木刻楞过夜"],
   "food": "室韦俄罗斯族家宴",
   "stay": "室韦木刻楞民宿（俄式木屋 ⭐特色）",
   "tips": "边境公路，防火证提前办；护照带好；无信号段较多"},
  {"day": 10, "date": "9/28 一", "name": "室韦 → 莫日格勒河 → 海拉尔",
   "lat": COORDS["海拉尔"][1], "lng": COORDS["海拉尔"][0],
   "phase": "loop", "drive": "~380km / 5.5h（边境路）",
   "highlights": ["黑山头骑马（可选）", "莫日格勒河（草原第一曲水）", "海拉尔市区"],
   "food": "海拉尔手把肉+奶茶",
   "stay": "海拉尔连锁酒店",
   "tips": "莫日格勒河瞭望台停车看全景 ⭐"},
  {"day": 11, "date": "9/29 二", "name": "海拉尔深度",
   "lat": COORDS["海拉尔"][1]+0.02, "lng": COORDS["海拉尔"][0]+0.05,
   "phase": "loop", "drive": "<100km",
   "highlights": ["世界反法西斯战争海拉尔纪念园", "呼伦贝尔民族博物院", "购物补给"],
   "food": "海拉尔烤全羊（提前预订）",
   "stay": "同 Day 10",
   "tips": "缓冲日，休整+补给零食+洗车"},
  {"day": 12, "date": "9/30 三", "name": "海拉尔 → 齐齐哈尔",
   "lat": COORDS["齐齐哈尔"][1], "lng": COORDS["齐齐哈尔"][0],
   "phase": "return", "drive": "457km / 4.8h",
   "highlights": ["下午到齐齐哈尔", "晚餐齐齐哈尔烤肉（东北烤肉发源地）"],
   "food": "齐齐哈尔烤肉必吃 ⭐",
   "stay": "齐齐哈尔市区酒店",
   "tips": "齐齐哈尔烤肉店：星期天/龙沙/满江红都行"},
  {"day": 13, "date": "10/1 四", "name": "扎龙丹顶鹤 → 长春",
   "lat": COORDS["长春"][1], "lng": COORDS["长春"][0],
   "phase": "return", "drive": "扎龙 30km 半日 + 齐齐哈尔→长春 500km / 5.4h",
   "highlights": ["早上扎龙保护区看丹顶鹤放飞（9:30/14:00）", "下午出发长春"],
   "food": "长春东北菜/朝鲜族烤肉",
   "stay": "长春市区连锁酒店（纯过夜）",
   "tips": "扎龙放飞时间准点到；国庆假期高速可能拥堵，晚出发避峰"},
  {"day": 14, "date": "10/2 五", "name": "长春 → 盘锦",
   "lat": COORDS["盘锦"][1], "lng": COORDS["盘锦"][0],
   "phase": "return", "drive": "438km / 4.7h",
   "highlights": ["下午到盘锦", "红海滩国家风景廊道看日落（碱蓬草秋季红透）⭐⭐⭐"],
   "food": "盘锦河蟹（10 月正季）+ 米饭",
   "stay": "盘锦红海滩景区附近酒店",
   "tips": "红海滩最佳时间 9-10 月，日落 17-18 点最美"},
  {"day": 15, "date": "10/3 六", "name": "盘锦 → 大连（到家）",
   "lat": COORDS["大连"][1], "lng": COORDS["大连"][0],
   "phase": "return", "drive": "294km / 3.2h",
   "highlights": ["短程日，中午到大连", "结束 15 天旅程"],
   "food": "大连海鲜庆祝",
   "stay": "自己家 🏠",
   "tips": "15 天总里程 ~5000km，回家做一次保养"},
]

outpath = "/home/azureuser/.openclaw/workspace/projects/travel-2026-10-inner-mongolia/map/routes.json"
with open(outpath, "w") as f:
    json.dump({"segments": out, "days": DAYS}, f, ensure_ascii=False)
print(f"Saved routes.json ({os.path.getsize(outpath)} bytes)")
