import json
import os
import time
import unicodedata
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from config import AUTO_REPLY, CHECK_INTERVAL
from zalo_ai import get_ai_response

# Load từ khóa
with open("keywords.json", "r", encoding="utf-8") as f:
    KEYWORDS = set([kw.lower() for kw in json.load(f)])

def slugify(text):
    text = unicodedata.normalize('NFKD', text)
    text = re.sub(r'[^\w\s-]', '', text.lower())
    return re.sub(r'[\s]+', '_', text)

def extract_messages(driver):
    message_elements = driver.find_elements(By.CLASS_NAME, 'text')
    messages = []

    for el in message_elements:
        try:
            text = el.text.strip()
            if text:
                messages.append(text)
        except:
            continue
    return messages

def get_chat_list(driver):
    chats = driver.find_elements(By.CSS_SELECTOR, "div.conv-item")
    return chats[:3]  

def get_chat_name(driver):
    try:
        name_el = driver.find_element(By.CLASS_NAME, "header-title")
        return name_el.text.strip()
    except Exception as e:
        print(f"[WARN] Không lấy được tên đoạn chat: {e}")
        return "unknown_chat"



def reply_to_last_message(driver, reply_text):
    try:
        input_box = driver.find_element(By.CSS_SELECTOR, "div.input")
        input_box.click()
        input_box.send_keys(reply_text)
        input_box.send_keys(Keys.ENTER)
    except Exception as e:
        print(f"[REPLY ERROR] {e}")

def main():
    print("Mở trình duyệt...")
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://chat.zalo.me")

    input("🔑 Vui lòng đăng nhập Zalo và nhấn Enter...")

    log = {}

    while True:
        print("🔍 Đang quét các đoạn chat...")
        chat_items = get_chat_list(driver)

        for chat in chat_items:
            try:
                chat.click()
                time.sleep(1)
                chat_name = get_chat_name(driver)
                messages = extract_messages(driver)

                if not messages:
                    continue

                last_msg = messages[-1]

                if any(keyword in last_msg.lower() for keyword in KEYWORDS):
                    key = f"{chat_name}:{last_msg}"
                    if key not in log:
                        print(f"📨 Tin nhắn khớp: [{chat_name}] {last_msg}")

                        ai_reply = get_ai_response(last_msg)
                        print(f"Trả lời: {ai_reply}")

                        if AUTO_REPLY and ai_reply:
                            reply_to_last_message(driver, ai_reply)

                        log[key] = ai_reply
                        with open("ai_response_log.json", "w", encoding="utf-8") as f:
                            json.dump(log, f, ensure_ascii=False, indent=2)

                time.sleep(1)

            except Exception as e:
                print(f"[ERROR] {e}")
                continue

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
