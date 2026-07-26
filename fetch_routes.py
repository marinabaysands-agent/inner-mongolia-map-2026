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
  ("Day 1", "大连", "通辽", [], "outbound"),
  ("Day 2", "通辽", "阿尔山", ["乌兰浩特"], "outbound"),
  ("Day 4", "阿尔山", "满洲里", [], "loop"),
  ("Day 6", "满洲里", "额尔古纳", [], "loop"),
  ("Day 8", "额尔古纳", "莫尔道嘎", ["根河"], "loop"),
  ("Day 9", "莫尔道嘎", "室韦", ["老鹰嘴"], "loop"),
  ("Day 10", "室韦", "海拉尔", [], "loop"),
  ("Day 12", "海拉尔", "齐齐哈尔", [], "return"),
  ("Day 13", "齐齐哈尔", "长春", [], "return"),
  ("Day 14", "长春", "盘锦", [], "return"),
  ("Day 15", "盘锦", "大连", [], "return"),
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
        print(f"  fallback: {r['error']}")
        pts = [[COORDS[a][1], COORDS[a][0]]]
        for w in wp:
            pts.append([COORDS[w][1], COORDS[w][0]])
        pts.append([COORDS[b][1], COORDS[b][0]])
        r = {"distance_km": None, "duration_h": None, "polyline": pts, "fallback": True}
    r["day_label"] = label
    r["from"] = a
    r["to"] = b
    r["waypoints"] = wp
    r["phase"] = phase
    out.append(r)

# 15 天详情：只保留"玩什么"+"为什么值得玩"
DAYS = [
  {"day": 1, "date": "9/19 六", "title": "大连 → 通辽",
   "lat": COORDS["通辽"][1], "lng": COORDS["通辽"][0], "phase": "outbound",
   "drive": "628km / 6.4h",
   "activities": [
     {"name": "全程高速直达通辽", "why": "过渡日，纯为第二天到阿尔山减压。通辽是科尔沁草原核心，虽然只过夜，出高速那一刻能感觉到景观开始变化——从东北平原进入蒙东。"}
   ]},
  {"day": 2, "date": "9/20 日", "title": "通辽 → 乌兰浩特 → 阿尔山",
   "lat": COORDS["阿尔山"][1], "lng": COORDS["阿尔山"][0], "phase": "outbound",
   "drive": "617km / 7.4h",
   "activities": [
     {"name": "乌兰浩特午餐+短逛", "why": "内蒙古自治区诞生地（1947 年「五一大会」就在这里开的），有内蒙古民族解放纪念馆和成吉思汗庙。中途歇脚顺便吃口正宗蒙餐。"},
     {"name": "傍晚抵达阿尔山，住天池服务区", "why": "住服务区省第二天进园 40km/1h 往返。阿尔山的秋色 9 月下旬开始，白桦金黄+落叶松橙红，是大兴安岭腹地最容易到的秋景样板。"}
   ]},
  {"day": 3, "date": "9/21 一", "title": "阿尔山森林公园",
   "lat": COORDS["阿尔山"][1]+0.1, "lng": COORDS["阿尔山"][0]-0.3, "phase": "loop",
   "drive": "园内 <100km",
   "activities": [
     {"name": "驼峰岭天池", "why": "阿尔山最美天池，火山口积水而成，形状像脚印，秋天四周落叶松金黄倒映水面，是整个行程的封面级景观。"},
     {"name": "大峡谷", "why": "300 万年前火山熔岩流冲刷形成的裂谷，栈道贴着峭壁走，两侧是原始白桦林，秋色浓时像走在金色隧道里。"},
     {"name": "杜鹃湖 + 石塘林", "why": "杜鹃湖清晨常有雾气，是拍水鸟和倒影的经典机位。石塘林是死火山遗迹上长出的森林，苔藓+熔岩+树根，很魔幻。"},
     {"name": "三潭峡", "why": "急流+瀑布+潭水三段景观压缩在 1km 步道里，是园内节奏变化最大的一段。"}
   ]},
  {"day": 4, "date": "9/22 二", "title": "阿尔山 → 满洲里",
   "lat": COORDS["满洲里"][1], "lng": COORDS["满洲里"][0], "phase": "loop",
   "drive": "427km / 5.8h",
   "activities": [
     {"name": "沿途 S203 草原公路", "why": "路上就是景。从阿尔山出来一路穿呼伦贝尔草原,9 月下旬草已变金,牧民赶着牛羊,随时可以停车拍照,没有围栏没有门票的那种野。"},
     {"name": "傍晚国门+夜景", "why": "满洲里的欧式建筑立面到夜里全部打灯,像被搬到东北的圣彼得堡缩小版,和白天完全两个城市。"}
   ]},
  {"day": 5, "date": "9/23 三", "title": "满洲里 + 俄罗斯半日",
   "lat": COORDS["满洲里"][1]+0.05, "lng": COORDS["满洲里"][0]-0.05, "phase": "loop",
   "drive": "0-100km",
   "activities": [
     {"name": "过境后贝加尔斯克", "why": "免签政策 2027-12-31 前有效,当天往返不用签证。这是唯一能让爸妈「踩过俄罗斯土地」的低成本方案——车不能过,报当地一日游团 ¥300-500/人含车导餐。"},
     {"name": "套娃景区 + 41 号界碑", "why": "套娃景区俗但拍照效果好,爸妈那代人对「到此一游」照片是有真需求的。41 号界碑是中俄边界最有仪式感的一个点。"}
   ]},
  {"day": 6, "date": "9/24 四", "title": "满洲里 → 额尔古纳",
   "lat": COORDS["额尔古纳"][1], "lng": COORDS["额尔古纳"][0], "phase": "loop",
   "drive": "256km / 3.6h",
   "activities": [
     {"name": "短程日,下午到", "why": "整个行程最松的一天,把爸妈的体力留给后面的莫尔道嘎和边境公路。"},
     {"name": "额尔古纳湿地(根河湿地)看晚霞", "why": "亚洲最大湿地,九曲十八弯的根河从草原上蜿蜒过,是呼伦贝尔的地标画面。18-19 点日落时河面金光,比正午看惊艳 10 倍。"}
   ]},
  {"day": 7, "date": "9/25 五", "title": "额尔古纳深度",
   "lat": COORDS["额尔古纳"][1]+0.03, "lng": COORDS["额尔古纳"][0]-0.05, "phase": "loop",
   "drive": "<100km",
   "activities": [
     {"name": "湿地清晨雾景", "why": "6 点前到湿地观景台,秋天晨雾从水面升起、慢慢被朝阳烤散——这是攻略里最难得的时段,大部分游客都在睡觉,雾散前你会以为整个湿地是你家的。"},
     {"name": "俄罗斯族家访", "why": "额尔古纳是全国唯一俄罗斯族聚居地。华俄后裔的家里能看到俄式火墙、萨莫瓦茶炊、老照片,主人会讲祖辈越境的故事——不是表演,是真实的家。"},
     {"name": "额尔古纳博物馆", "why": "小而精,讲清楚了呼伦贝尔「三大民族(蒙/俄/鄂温克)+ 五大部落」的关系,爸妈那代人对这段历史特别感兴趣。"}
   ]},
  {"day": 8, "date": "9/26 六", "title": "额尔古纳 → 根河 → 莫尔道嘎",
   "lat": COORDS["莫尔道嘎"][1], "lng": COORDS["莫尔道嘎"][0], "phase": "loop",
   "drive": "311km / 4.8h",
   "activities": [
     {"name": "根河兴安神鹿园", "why": "中国最后的驯鹿部落——敖鲁古雅使鹿鄂温克人的驯鹿。可以近距离喂食、拍照,鹿角在阳光下像树枝的分叉,是那种在别处根本见不到的活体标本。"},
     {"name": "莫尔道嘎大兴安岭腹地", "why": "全中国纬度最北的森林小镇之一,秋色深到 10 月初,松树+落叶松+白桦形成三层色板(墨绿+金黄+纯白树干),是整个行程最「重量级」的一天。"}
   ]},
  {"day": 9, "date": "9/27 日", "title": "莫尔道嘎 → 老鹰嘴 → 室韦",
   "lat": COORDS["室韦"][1], "lng": COORDS["室韦"][0], "phase": "loop",
   "drive": "~130km / 3h(边境)",
   "activities": [
     {"name": "莫尔道嘎森林公园(一目九岭)", "why": "站在观景台一次能看到九道连绵的山脊线,秋色时九层颜色渐变,是大兴安岭最出片的机位,没有之一。"},
     {"name": "老鹰嘴", "why": "额尔古纳河边的岩石像一只俯冲的老鹰,河对岸就是俄罗斯。夕阳时逆光轮廓最像,是边境公路上最戏剧化的一个自然景观。"},
     {"name": "室韦木刻楞民宿过夜", "why": "室韦是中俄边境的俄罗斯族小镇,木刻楞就是俄式尖顶原木木屋。住里面才是完整体验——木头香、火墙暖气、二楼小窗对着额尔古纳河,河对岸是俄罗斯灯火。"}
   ]},
  {"day": 10, "date": "9/28 一", "title": "室韦 → 莫日格勒河 → 海拉尔",
   "lat": COORDS["海拉尔"][1], "lng": COORDS["海拉尔"][0], "phase": "loop",
   "drive": "~380km / 5.5h(边境)",
   "activities": [
     {"name": "黑山头骑马(可选)", "why": "呼伦贝尔草原骑马体验最正宗的一片,爸妈想尝试可以短线 30 分钟,不勉强就跳过。"},
     {"name": "莫日格勒河瞭望台", "why": "老舍笔下「天下第一曲水」,从瞭望台俯瞰,河像一条银色缎带在无边草原上画 S。这是所有呼伦贝尔宣传片的封面画面。"},
     {"name": "傍晚到海拉尔市区", "why": "回到城市补给,准备回程。海拉尔是呼伦贝尔市府,城市不大但补给齐全,也是呼伦贝尔博物院所在。"}
   ]},
  {"day": 11, "date": "9/29 二", "title": "海拉尔深度",
   "lat": COORDS["海拉尔"][1]+0.02, "lng": COORDS["海拉尔"][0]+0.05, "phase": "loop",
   "drive": "<100km",
   "activities": [
     {"name": "缓冲+休整日", "why": "连续 10 天开车了,给爸妈留一天不动窝。可以睡到自然醒、洗车、补给零食、洗衣服。"},
     {"name": "反法西斯战争海拉尔纪念园", "why": "亚洲最大二战地下要塞遗址,日军侵华时的地下工事,爸妈那代人会很感兴趣。氛围沉重但内容扎实。"},
     {"name": "呼伦贝尔民族博物院", "why": "把 10 天在草原、湿地、林区看到的所有民族(蒙/俄/鄂温克/鄂伦春/达斡尔)历史串成一条线,是最好的「复盘馆」。"}
   ]},
  {"day": 12, "date": "9/30 三", "title": "海拉尔 → 齐齐哈尔",
   "lat": COORDS["齐齐哈尔"][1], "lng": COORDS["齐齐哈尔"][0], "phase": "return",
   "drive": "457km / 4.7h",
   "activities": [
     {"name": "下午到齐齐哈尔", "why": "过渡日,把车程留短,晚上早休息。"},
     {"name": "齐齐哈尔烤肉", "why": "东北烤肉的发源地,和韩式/日式完全不同的做法——粗豪、多油、蒜香。走过齐齐哈尔不吃烤肉就等于白来。"}
   ]},
  {"day": 13, "date": "10/1 四", "title": "扎龙丹顶鹤 → 长春",
   "lat": COORDS["长春"][1], "lng": COORDS["长春"][0], "phase": "return",
   "drive": "扎龙 30km 半日 + 500km / 5.4h",
   "activities": [
     {"name": "早上扎龙保护区看丹顶鹤放飞", "why": "中国最大的丹顶鹤栖息地,放飞时间准点(通常 9:30 和 14:00),几十只丹顶鹤从芦苇荡起飞,是那种「教科书上看过 20 年终于亲眼看到」的画面。"},
     {"name": "下午出发长春", "why": "国庆当天走高速可能堵,建议 12 点后出发避峰。长春只过夜,第二天继续走。"}
   ]},
  {"day": 14, "date": "10/2 五", "title": "长春 → 盘锦",
   "lat": COORDS["盘锦"][1], "lng": COORDS["盘锦"][0], "phase": "return",
   "drive": "438km / 4.7h",
   "activities": [
     {"name": "盘锦红海滩", "why": "整个行程最后的重磅景。碱蓬草秋季变红,10 万亩红色滩涂延伸到海边,像有人把地毯铺到了海里。9-10 月是唯一的观赏期,错过要等一年。日落时颜色最饱和。"},
     {"name": "盘锦河蟹", "why": "10 月是盘锦河蟹正季,黄满膏红,和阳澄湖是两种风味——盘锦蟹更咸鲜,直接清蒸就够。"}
   ]},
  {"day": 15, "date": "10/3 六", "title": "盘锦 → 大连(到家)",
   "lat": COORDS["大连"][1], "lng": COORDS["大连"][0], "phase": "return",
   "drive": "294km / 3.2h",
   "activities": [
     {"name": "短程,中午到家", "why": "15 天 5000km,以最轻松的一天收尾。回到家吃海鲜庆祝,车做一次保养。"}
   ]},
]

outpath = "/home/azureuser/.openclaw/workspace/projects/travel-2026-10-inner-mongolia/map/routes.json"
with open(outpath, "w") as f:
    json.dump({"segments": out, "days": DAYS}, f, ensure_ascii=False)
print(f"Saved routes.json ({os.path.getsize(outpath)} bytes)")
