from http.server import BaseHTTPRequestHandler
import requests
import os
import json

TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
topic_ids_str = os.environ.get('TOPIC_IDS_LIST', '') 

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}/reopenForumTopic"

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        results = []
        
        # 1. Tách chuỗi ID thành danh sách
        try:
            TOPIC_IDS = [int(tid) for tid in topic_ids_str.split(',') if tid.strip()]
            if not TOPIC_IDS:
                raise ValueError("TOPIC_IDS_LIST is empty")
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Server Error: TOPIC_IDS_LIST bi loi. {e}".encode('utf-8'))
            return

        # 2. Lặp qua TẤT CẢ các topic và chạy lệnh mở
        for topic_id in TOPIC_IDS:
            payload = { 'chat_id': CHAT_ID, 'message_thread_id': topic_id }
            try:
                r = requests.post(TELEGRAM_API_URL, data=payload)
                response_json = r.json()
                results.append(response_json)
                print(f"Mo Topic {topic_id}: {response_json}")
            except Exception as e:
                print(f"LOI khi goi API cho topic {topic_id}: {e}")
                results.append({"error": str(e), "topic_id": topic_id})
                
        # 3. Gửi phản hồi thành công
        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "da chay lenh MO toan bo topic", "results": results}).encode('utf-8'))
        return