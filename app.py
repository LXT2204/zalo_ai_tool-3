from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
import threading
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from zalo_ai import get_ai_response
from config import GEMINI_API_KEY, AUTO_REPLY, CHECK_INTERVAL

app = Flask(__name__)

# Global variables for bot control
bot_running = False
bot_thread = None
chat_logs = []
keywords = []
driver = None
current_messages = []
zalo_window_opened = False

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

def extract_messages(driver):
    """Extract messages from current chat"""
    try:
        # Look for sent messages (your messages)
        sent_messages = driver.find_elements(By.CSS_SELECTOR, "div.message-item.sent .text")
        received_messages = driver.find_elements(By.CSS_SELECTOR, "div.message-item.received .text")
        
        messages = []
        
        # Add sent messages (your messages)
        for el in sent_messages:
            try:
                text = el.text.strip()
                if text:
                    messages.append(f"[Bạn] {text}")
            except:
                continue
                
        # Add received messages
        for el in received_messages:
            try:
                text = el.text.strip()
                if text:
                    messages.append(f"[Người khác] {text}")
            except:
                continue
                
        return messages
    except Exception as e:
        print(f"Error extracting messages: {e}")
        return []

def get_chat_list(driver):
    """Get list of chat items"""
    try:
        chats = driver.find_elements(By.CSS_SELECTOR, "div.conv-item")
        return chats[:5]  # Get first 5 chats
    except Exception as e:
        print(f"Error getting chat list: {e}")
        return []

def get_chat_name(driver):
    """Get current chat name"""
    try:
        name_el = driver.find_element(By.CLASS_NAME, "header-title")
        return name_el.text.strip()
    except Exception as e:
        print(f"Error getting chat name: {e}")
        return "unknown_chat"

def setup_driver():
    """Setup Chrome driver with visible window for user interaction"""
    options = Options()
    
    # Check if running in cloud environment
    import os
    is_cloud = os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('RENDER') or os.getenv('HEROKU')
    
    if is_cloud:
        # Cloud environment - use headless mode with Nix packages
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-images")
        print("🌐 Running in cloud environment - using headless mode")
    else:
        # Local environment - visible window
        options.add_argument("--start-maximized")
        print("🌐 Running locally - using visible window")
    
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    try:
        # Try to use webdriver-manager first
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        print("✅ Chrome driver setup successful with webdriver-manager")
    except Exception as e:
        print(f"⚠️  webdriver-manager failed: {e}")
        try:
            # Fallback to system ChromeDriver
            driver = webdriver.Chrome(options=options)
            print("✅ Chrome driver setup successful with system ChromeDriver")
        except Exception as e2:
            print(f"❌ System ChromeDriver failed: {e2}")
            return None
    
    # Remove automation flags
    try:
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    except:
        pass
    
    return driver

def bot_worker():
    """Main bot worker function"""
    global bot_running, chat_logs, driver, current_messages, zalo_window_opened
    
    print("🤖 Bot started...")
    
    # Setup driver
    driver = setup_driver()
    if not driver:
        print("❌ Failed to setup Chrome driver")
        return
    
    try:
        # Navigate to Zalo Web
        driver.get("https://chat.zalo.me")
        
        # Check if running in cloud environment
        import os
        is_cloud = os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('RENDER') or os.getenv('HEROKU')
        
        if is_cloud:
            print("🌐 Running in cloud environment - Zalo Web opened in headless mode")
            print("⚠️  Note: In cloud environments, you cannot manually log in")
            print("📱 The bot will monitor for messages but requires pre-authenticated session")
        else:
            print("🌐 Opened Zalo Web - Please log in manually")
            zalo_window_opened = True
        
        # Wait for user to login (only in local environment)
        if not is_cloud:
            print("⏳ Waiting for login... Please log in to your Zalo account")
        
        last_processed_messages = set()
        last_message_count = 0
        
        while bot_running:
            try:
                # Get current chat messages
                messages = extract_messages(driver)
                
                if messages:
                    # Update current messages for dashboard
                    current_messages = messages[-10:]  # Keep last 10 messages
                    
                    # Check for new messages
                    if len(messages) > last_message_count:
                        new_messages = messages[last_message_count:]
                        last_message_count = len(messages)
                        
                        for message in new_messages:
                            # Only process messages you sent (containing "[Bạn]")
                            if "[Bạn]" in message:
                                message_text = message.replace("[Bạn] ", "")
                                message_key = f"user:{message_text}"
                                
                                # Check if this message was already processed
                                if message_key not in last_processed_messages:
                                    last_processed_messages.add(message_key)
                                    
                                    print(f"📨 New message sent: {message_text}")
                                    
                                    # Check if message contains keywords
                                    if any(keyword in message_text.lower() for keyword in keywords):
                                        print(f"🔑 Keyword match found: {message_text}")
                                        
                                        # Get AI response
                                        ai_reply = get_ai_response(message_text)
                                        if ai_reply:
                                            print(f"🤖 AI Response: {ai_reply}")
                                            
                                            # Save to logs
                                            save_chat_log("Bạn", message_text, ai_reply)
                                            
                                            # Add AI response to current messages
                                            current_messages.append(f"[AI Bot] {ai_reply}")
                                            if len(current_messages) > 10:
                                                current_messages.pop(0)
                
                time.sleep(CHECK_INTERVAL)
                
            except Exception as e:
                print(f"Error in bot loop: {e}")
                time.sleep(CHECK_INTERVAL)
                
    except Exception as e:
        print(f"Critical error in bot worker: {e}")
    finally:
        if driver:
            driver.quit()
        zalo_window_opened = False
        print("🤖 Bot stopped.")

@app.route('/')
def index():
    return render_template('index.html', 
                         bot_running=bot_running,
                         keywords=keywords,
                         chat_logs=chat_logs[-10:],  # Show last 10 logs
                         current_messages=current_messages[-5:],  # Show last 5 current messages
                         auto_reply=AUTO_REPLY,
                         check_interval=CHECK_INTERVAL,
                         zalo_window_opened=zalo_window_opened)

@app.route('/api/start_bot', methods=['POST'])
def start_bot():
    global bot_running, bot_thread
    if not bot_running:
        bot_running = True
        bot_thread = threading.Thread(target=bot_worker)
        bot_thread.daemon = True
        bot_thread.start()
        return jsonify({"status": "success", "message": "Bot started successfully - Zalo window will open for login"})
    return jsonify({"status": "error", "message": "Bot is already running"})

@app.route('/api/stop_bot', methods=['POST'])
def stop_bot():
    global bot_running, driver
    bot_running = False
    if driver:
        try:
            driver.quit()
        except:
            pass
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

@app.route('/api/bot_status')
def get_bot_status():
    return jsonify({
        "bot_running": bot_running,
        "zalo_window_opened": zalo_window_opened,
        "message_count": len(current_messages)
    })

if __name__ == '__main__':
    load_keywords()
    load_chat_logs()
    app.run(debug=True, host='0.0.0.0', port=5000) 