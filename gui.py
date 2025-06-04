import tkinter as tk
import requests
import threading
import time

station_id = "34151"
station_name = "중대앞 버스정류장"
buses = ["4401", "8200", "8201", "8204"]
selected_bus = None
user_id = "user1"  # 예시 이름/학번

def select_bus(bus_no):
    global selected_bus
    selected_bus = bus_no
    update_status()

def update_status():
    if selected_bus:
        res = requests.get(f"http://localhost:5000/api/status/{station_id}/{selected_bus}")
        data = res.json()
        count_label.config(text=f"현재 대기자수: {data['count']}명")
        expire_label.config(text=f"만료 시간: {', '.join(data['expire_times'])}")

def tag_user():
    if selected_bus:
        res = requests.post("http://localhost:5000/api/tag", json={
            "station_id": station_id,
            "bus_no": selected_bus,
            "user_id": user_id
        })
        data = res.json()
        result_label.config(text=f"{data['message']} (순번: {data['position']}, 전 정류장: {data['previous_count']}명)")
        update_status()

def extend_time():
    if selected_bus:
        res = requests.post("http://localhost:5000/api/extend", json={
            "station_id": station_id,
            "bus_no": selected_bus,
            "user_id": user_id
        })
        data = res.json()
        result_label.config(text=data["message"])
        update_status()

def auto_update():
    while True:
        update_status()
        time.sleep(5)

root = tk.Tk()
root.title("버스 대기자 관리")

tk.Label(root, text=f"정류장: {station_name}").pack()

for bus in buses:
    tk.Button(root, text=bus, command=lambda b=bus: select_bus(b)).pack()

tk.Button(root, text="대기자 등록", command=tag_user).pack()
tk.Button(root, text="유효시간 연장", command=extend_time).pack()

count_label = tk.Label(root, text="현재 대기자수: -명")
count_label.pack()

expire_label = tk.Label(root, text="만료 시간: -")
expire_label.pack()

result_label = tk.Label(root, text="")
result_label.pack()

threading.Thread(target=auto_update, daemon=True).start()
root.mainloop()
