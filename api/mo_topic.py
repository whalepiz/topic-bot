from http.server import BaseHTTPRequestHandler
import requests
import os

TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

# Đọc chuỗi ID từ Vercel (ví dụ: "2,4,7,9,11")
topic_ids_str = os.environ.get('TOPIC_IDS_LIST', '') 
# Chuyển chuỗi đó thành 1 danh sách (list)
TOPIC_IDS = [int(tid) for tid in topic_ids_str.split(',') if tid.strip()]

# API để MỞ topic
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}/reopenForumTopic"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        results = []
        if not TOPIC_IDS:
             # Nếu không tìm thấy ID nào (do quên cấu hình)
             return self.send_error(500, "TOPIC_IDS_LIST bi thieu")

        for topic_id in TOPIC_IDS:
            payload = { 'chat_id': CHAT_ID, 'message_thread_id': topic_id }
            try:
                r = requests.post(TELEGRAM_API_URL, data=payload)
                results.append(r.json())
            except Exception as e:
                results.append({"error": str(e), "topic_id": topic_id})
                
        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.end_headers()
        self.wfile.write(str({"status": "da chay lenh MO topic", "results": results}).encode('utf-8'))
        return