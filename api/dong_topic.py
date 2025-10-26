from http.server import BaseHTTPRequestHandler
import requests
import os
import json # <-- THÊM DÒNG NÀY

TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

topic_ids_str = os.environ.get('TOPIC_IDS_LIST', '') 
TOPIC_IDS = [int(tid) for tid in topic_ids_str.split(',') if tid.strip()]

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}/closeForumTopic"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        results = []
        if not TOPIC_IDS:
             print("LOI: Khong tim thay TOPIC_IDS_LIST") # <-- THÊM DÒNG NÀY
             return self.send_error(500, "TOPIC_IDS_LIST bi thieu")

        for topic_id in TOPIC_IDS:
            payload = { 'chat_id': CHAT_ID, 'message_thread_id': topic_id }
            try:
                r = requests.post(TELEGRAM_API_URL, data=payload)
                response_json = r.json()
                results.append(response_json)
                # Dòng print này sẽ in ra lỗi của Telegram
                print(f"Dong Topic {topic_id}: {response_json}") # <-- THÊM DÒNG NÀY
            except Exception as e:
                results.append({"error": str(e), "topic_id": topic_id})

        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.wfile.write(str({"status": "da chay lenh DONG topic", "results": results}).encode('utf-8'))
        return