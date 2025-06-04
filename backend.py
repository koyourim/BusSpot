from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import threading

app = Flask(__name__)

# 정류장 데이터
stations = {
    "33121": {
        "name": "한경국립대학교 (강남역 방면)",
        "buses": ["4401", "8200", "8201", "8204"],
        "previous_station": None
    },
    "34151": {
        "name": "중앙대.롯데캐슬아파트 (강남역 방면)",
        "buses": ["4401", "8200", "8201", "8204"],
        "previous_station": "33121"
    },
    "33061": {
        "name": "대림동산 (강남역 방면)",
        "buses": ["4401", "8200", "8201", "8204"],
        "previous_station": "34151"
    },
    "33789": {
        "name": "공도시외버스정류장 (강남역 방면)",
        "buses": ["4401", "8200", "8201", "8204"],
        "previous_station": "33061"
    },
    "33018": {
        "name": "주은.풍림아파트 (강남역 방면)",
        "buses": ["4401", "8200", "8201", "8204"],
        "previous_station": "33789"
    },
    "22297": {
        "name": "매헌시민의숲.양재꽃시장 (강남역 방면)",
        "buses": ["4401"],
        "previous_station": "33018"
    },
    "22002": {
        "name": "말죽거리공원사거리(중) (강남역 방면)",
        "buses": ["4401"],
        "previous_station": "22297"
    },
    "22004": {
        "name": "양재역.서초문화예술회관(중) (강남역 방면)",
        "buses": ["4401"],
        "previous_station": "22002"
    },
    "22006": {
        "name": "뱅뱅사거리(중) (강남역 방면)",
        "buses": ["4401"],
        "previous_station": "22004"
    },
    "22008": {
        "name": "래미안아파트.파이낸셜뉴스(중) (강남역 방면)",
        "buses": ["4401"],
        "previous_station": "22006"
    },
    "22010": {
        "name": "신분당선강남역(중) (회차)",
        "buses": ["4401"],
        "previous_station": "22008"
    },
    "33017": {
        "name": "주은.풍림아파트 (한경대 방면)",
        "buses": ["4401"],
        "previous_station": "22010"
    },
    "33668": {
        "name": "공도시외버스정류장 (한경대 방면)",
        "buses": ["4401"],
        "previous_station": "33017"
    },
    "33060": {
        "name": "대림동산 (한경대 방면)",
        "buses": ["4401"],
        "previous_station": "33668"
    },
    "34157": {
        "name": "중앙대.롯데캐슬아파트 (한경대 방면)",
        "buses": ["4401"],
        "previous_station": "33060"
    },
    "33120": {
        "name": "한경국립대학교 (한경대 방면)",
        "buses": ["4401"],
        "previous_station": "34157"
    }
}

# 대기자 리스트
waiting_data = {
    station_id: {bus: [] for bus in station["buses"]}
    for station_id, station in stations.items()
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/get_station", methods=["POST"])
def get_station():
    data = request.json
    station_id = data["station_id"]
    station = stations.get(station_id)
    if station:
        return jsonify({
            "name": station["name"],
            "buses": station["buses"]
        })
    else:
        return jsonify({"error": "정류장 없음!"}), 404

@app.route("/api/tag", methods=["POST"])
def tag():
    data = request.json
    station_id = data["station_id"]
    bus_no = data["bus_no"]
    user_id = data["user_id"]

    now = datetime.now()
    expire_time = now + timedelta(minutes=15)

    waiting_data[station_id][bus_no].append({
        "user_id": user_id,
        "expire_time": expire_time
    })

    return jsonify({
        "expire_time": expire_time.strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route("/api/status", methods=["POST"])
def status():
    data = request.json
    station_id = data["station_id"]
    bus_no = data["bus_no"]

    now = datetime.now()
    valid_waiting = [
        d for d in waiting_data[station_id][bus_no]
        if d["expire_time"] > now
    ]

    # 이전 정류장 대기자수 확인
    prev_station_id = stations[station_id]["previous_station"]
    if prev_station_id:
        prev_waiting = [
            d for d in waiting_data[prev_station_id][bus_no]
            if d["expire_time"] > now
        ]
        previous_count = len(prev_waiting)
    else:
        previous_count = "-"

    return jsonify({
        "current_count": len(valid_waiting),
        "previous_count": previous_count
    })

@app.route("/api/extend", methods=["POST"])
def extend():
    data = request.json
    station_id = data["station_id"]
    bus_no = data["bus_no"]
    user_id = data["user_id"]

    for d in waiting_data[station_id][bus_no]:
        if d["user_id"] == user_id:
            d["expire_time"] += timedelta(minutes=10)
            return jsonify({
                "new_expire_time": d["expire_time"].strftime("%Y-%m-%d %H:%M:%S")
            })

    return jsonify({"error": "사용자 없음"}), 404

# 만료자 제거 스레드
def cleanup():
    while True:
        now = datetime.now()
        for station_id in waiting_data:
            for bus_no in waiting_data[station_id]:
                waiting_data[station_id][bus_no] = [
                    d for d in waiting_data[station_id][bus_no]
                    if d["expire_time"] > now
                ]

threading.Thread(target=cleanup, daemon=True).start()

if __name__ == "__main__":
    app.run(port=5001)
