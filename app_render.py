from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
import threading
import time
import random
from datetime import datetime
from zalo_ai import get_ai_response
from config import GEMINI_API_KEY, AUTO_REPLY, CHECK_INTERVAL

app = Flask(__name__)

# Global variables for bot control
bot_running = False
bot_thread = None
chat_logs = []
keywords = []
current_messages = []

# Sample messages for demonstration
SAMPLE_MESSAGES = [
    "Xin chào, tôi muốn hỏi về đơn hàng của mình",
    "Giá sản phẩm này là bao nhiêu?",
    "Tôi muốn hủy đơn hàng",
    "Phí ship đến Hà Nội là bao nhiêu?",
    "Tôi muốn thanh toán bằng thẻ tín dụng",
    "Sản phẩm có còn hàng không?",
    "Thời gian giao hàng mất bao lâu?",
    "Tôi có thể đổi trả sản phẩm không?",
    "Có chương trình khuyến mãi nào không?",
    "Tôi muốn đặt hàng qua điện thoại"
]

SAMPLE_CHAT_NAMES = [
    "Nguyễn Văn A",
    "Trần Thị B",
    "Lê Văn C",
    "Phạm Thị D",
    "Hoàng Văn E"
]

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
    """Simulated bot worker for Render deployment"""
    global bot_running, chat_logs, current_messages
    
    print("🤖 Bot started (Render mode - simulated messages)...")
    
    last_processed_messages = set()
    message_counter = 0
    
    while bot_running:
        try:
            # Simulate receiving messages
            if random.random() < 0.3:  # 30% chance to receive a message
                message = random.choice(SAMPLE_MESSAGES)
                chat_name = random.choice(SAMPLE_CHAT_NAMES)
                
                # Update current messages for dashboard
                current_messages.append(f"[{chat_name}] {message}")
                if len(current_messages) > 10:  # Keep only last 10 messages
                    current_messages.pop(0)
                
                message_key = f"{chat_name}:{message}"
                
                # Check if this message was already processed
                if message_key not in last_processed_messages:
                    last_processed_messages.add(message_key)
                    
                    # Check if message contains keywords
                    if any(keyword in message.lower() for keyword in keywords):
                        print(f"📨 Keyword match: [{chat_name}] {message}")
                        
                        # Get AI response
                        ai_reply = get_ai_response(message)
                        if ai_reply:
                            print(f"🤖 AI Response: {ai_reply}")
                            
                            # Save to logs
                            save_chat_log(chat_name, message, ai_reply)
                            
                            # Simulate auto reply
                            if AUTO_REPLY:
                                print(f"✅ Simulated reply to {chat_name}")
                                # Add the AI response to current messages
                                current_messages.append(f"[AI Bot] {ai_reply}")
                                if len(current_messages) > 10:
                                    current_messages.pop(0)
            
            time.sleep(CHECK_INTERVAL)
            
        except Exception as e:
            print(f"Error in bot loop: {e}")
            time.sleep(CHECK_INTERVAL)
    
    print("🤖 Bot stopped.")

@app.route('/')
def index():
    return render_template('index.html', 
                         bot_running=bot_running,
                         keywords=keywords,
                         chat_logs=chat_logs[-10:],  # Show last 10 logs
                         current_messages=current_messages[-5:],  # Show last 5 current messages
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
        return jsonify({"status": "success", "message": "Bot started successfully (Render mode)"})
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

@app.route('/api/current_messages')
def get_current_messages():
    return jsonify({"messages": current_messages})

@app.route('/api/clear_logs', methods=['POST'])
def clear_logs():
    global chat_logs
    chat_logs = []
    if os.path.exists("ai_response_log.json"):
        os.remove("ai_response_log.json")
    return jsonify({"status": "success", "message": "Logs cleared"})

@app.route('/api/add_test_message', methods=['POST'])
def add_test_message():
    """Add a test message manually"""
    global current_messages
    data = request.get_json()
    message = data.get('message', '')
    chat_name = data.get('chat_name', 'Test User')
    
    if message:
        current_messages.append(f"[{chat_name}] {message}")
        if len(current_messages) > 10:
            current_messages.pop(0)
        
        # Check if message contains keywords
        if any(keyword in message.lower() for keyword in keywords):
            ai_reply = get_ai_response(message)
            if ai_reply:
                save_chat_log(chat_name, message, ai_reply)
                current_messages.append(f"[AI Bot] {ai_reply}")
                if len(current_messages) > 10:
                    current_messages.pop(0)
        
        return jsonify({"status": "success", "message": "Test message added"})
    return jsonify({"status": "error", "message": "No message provided"})

if __name__ == '__main__':
    load_keywords()
    load_chat_logs()
    app.run(debug=True, host='0.0.0.0', port=5000) 