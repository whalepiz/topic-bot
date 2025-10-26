from http.server import BaseHTTPRequestHandler
import requests
import os
import json
import datetime
import pytz

TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
topic_ids_str = os.environ.get('TOPIC_IDS_LIST', '') 

# Ánh xạ giữa giờ đóng (UTC) và thứ tự Topic ID trong list
# [Giờ UTC, Phút UTC, Thứ tự Topic (0-indexed)]
SCHEDULE_MAP = [
    [2, 30, 0],  # 02:30 UTC (09:30 VN) -> Dong Topic THU 1 (Index 0)
    [4, 30, 1],  # 04:30 UTC (11:30 VN) -> Dong Topic THU 2 (Index 1)
    [6, 30, 2],  # 06:30 UTC (13:30 VN) -> Dong Topic THU 3 (Index 2)
    [8, 30, 3],  # 08:30 UTC (15:30 VN) -> Dong Topic THU 4 (Index 3)
    [10, 30, 4]  # 10:30 UTC (17:30 VN) -> Dong Topic THU 5 (Index 4)
]

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}/closeForumTopic"

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        # Thiết lập múi giờ UTC để kiểm tra lịch chạy
        utc_now = datetime.datetime.now(pytz.utc)
        current_hour_utc = utc_now.hour
        current_minute_utc = utc_now.minute
        
        TOPIC_IDS = []
        
        # 1. Tách chuỗi ID thành danh sách
        try:
            full_topic_list = [int(tid) for tid in topic_ids_str.split(',') if tid.strip()]
            if not full_topic_list:
                raise ValueError("TOPIC_IDS_LIST is empty")
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Server Error: TOPIC_IDS_LIST bi loi. {e}".encode('utf-8'))
            return
            
        # 2. Tìm Topic ID cần chạy dựa trên giờ hiện tại
        target_index = -1
        for hour, minute, index in SCHEDULE_MAP:
            # Kiểm tra xem giờ và phút hiện tại có khớp với lịch đóng nào không
            if current_hour_utc == hour and current_minute_utc == minute:
                target_index = index
                break
        
        if target_index != -1 and target_index < len(full_topic_list):
            TOPIC_IDS.append(full_topic_list[target_index])
        else:
            # Nếu không khớp với giờ đóng nào, có thể là lỗi trễ.
            # KHÔNG NÊN CHẠY BẤT KỲ LỆNH NÀO NẾU KHÔNG KHỚP CHÍNH XÁC.
            self.send_response(200)
            self.end_headers()
            self.wfile.write("Khong khop voi gio dong nao. Bo qua.".encode('utf-8'))
            return

        # 3. Chạy lệnh đóng cho Topic đã tìm được
        results = []
        for topic_id in TOPIC_IDS:
            payload = { 'chat_id': CHAT_ID, 'message_thread_id': topic_id }
            try:
                r = requests.post(TELEGRAM_API_URL, data=payload)
                response_json = r.json()
                results.append(response_json)
                print(f"Dong Topic {topic_id}: {response_json}")
            except Exception as e:
                print(f"LOI khi goi API cho topic {topic_id}: {e}")
                results.append({"error": str(e), "topic_id": topic_id})
                
        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "da chay lenh DONG topic", "results": results}).encode('utf-8'))
        return