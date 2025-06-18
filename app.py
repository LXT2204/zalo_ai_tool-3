from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
import threading
import time
from datetime import datetime
from zalo_ai import get_ai_response
from config import GEMINI_API_KEY, AUTO_REPLY, CHECK_INTERVAL

app = Flask(__name__)

# Global variables for bot control
bot_running = False
bot_thread = None
chat_logs = []
keywords = []

def load_keywords():
    global keywords
    try:
        with open("keywords.json", "r", encoding="utf-8") as f:
            keywords = json.load(f)
    except FileNotFoundError:
        keywords = ["đơn hàng", "hủy", "giá", "ship", "thanh toán"]
        save_keywords()

def save_keywords():
    with open("keywords.json", "w", encoding="utf-8") as f:
        json.dump(keywords, f, ensure_ascii=False, indent=2)

def load_chat_logs():
    global chat_logs
    try:
        with open("ai_response_log.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            chat_logs = []
            for key, response in data.items():
                if ":" in key:
                    chat_name, message = key.split(":", 1)
                    chat_logs.append({
                        "chat_name": chat_name,
                        "message": message,
                        "response": response,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
    except FileNotFoundError:
        chat_logs = []

def save_chat_log(chat_name, message, response):
    chat_logs.append({
        "chat_name": chat_name,
        "message": message,
        "response": response,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    
    # Save to file
    log_data = {}
    for log in chat_logs:
        key = f"{log['chat_name']}:{log['message']}"
        log_data[key] = log['response']
    
    with open("ai_response_log.json", "w", encoding="utf-8") as f:
        json.dump(log_data, f, ensure_ascii=False, indent=2)

def bot_worker():
    global bot_running, chat_logs
    print("🤖 Bot started...")
    
    # Simulate bot activity for demo
    while bot_running:
        # In a real implementation, this would connect to Zalo
        # For now, we'll simulate some activity
        time.sleep(CHECK_INTERVAL)
        
        if not bot_running:
            break
    
    print("🤖 Bot stopped.")

@app.route('/')
def index():
    return render_template('index.html', 
                         bot_running=bot_running,
                         keywords=keywords,
                         chat_logs=chat_logs[-10:],  # Show last 10 logs
                         auto_reply=AUTO_REPLY,
                         check_interval=CHECK_INTERVAL)

@app.route('/api/start_bot', methods=['POST'])
def start_bot():
    global bot_running, bot_thread
    if not bot_running:
        bot_running = True
        bot_thread = threading.Thread(target=bot_worker)
        bot_thread.daemon = True
        bot_thread.start()
        return jsonify({"status": "success", "message": "Bot started successfully"})
    return jsonify({"status": "error", "message": "Bot is already running"})

@app.route('/api/stop_bot', methods=['POST'])
def stop_bot():
    global bot_running
    bot_running = False
    return jsonify({"status": "success", "message": "Bot stopped successfully"})

@app.route('/api/keywords', methods=['GET', 'POST'])
def manage_keywords():
    global keywords
    if request.method == 'POST':
        data = request.get_json()
        keywords = data.get('keywords', [])
        save_keywords()
        return jsonify({"status": "success", "keywords": keywords})
    return jsonify({"keywords": keywords})

@app.route('/api/test_ai', methods=['POST'])
def test_ai():
    data = request.get_json()
    message = data.get('message', '')
    if message:
        response = get_ai_response(message)
        return jsonify({"status": "success", "response": response})
    return jsonify({"status": "error", "message": "No message provided"})

@app.route('/api/chat_logs')
def get_chat_logs():
    return jsonify({"logs": chat_logs})

@app.route('/api/clear_logs', methods=['POST'])
def clear_logs():
    global chat_logs
    chat_logs = []
    if os.path.exists("ai_response_log.json"):
        os.remove("ai_response_log.json")
    return jsonify({"status": "success", "message": "Logs cleared"})

if __name__ == '__main__':
    load_keywords()
    load_chat_logs()
    app.run(debug=True, host='0.0.0.0', port=5000) 