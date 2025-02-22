import sys
import os
import requests
import threading
import time
import json
import random
from time import strftime
import telebot
from telebot import types
from datetime import datetime, timedelta

# Replace with your Telegram bot token
BOT_TOKEN = "7903504769:AAEMX3AUeOgGXvHNMQ5x7T7XcewuK90quNQ"
bot = telebot.TeleBot(BOT_TOKEN)

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.2; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.2210.144",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.259 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/21.0 Chrome/120.0.6099.259 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Brave/120.0.6099.259 Chrome/120.0.6099.259 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Vivaldi/6.2.3105.54 Chrome/120.0.6099.259 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.259 Safari/537.36 Vivaldi/6.2.3105.54",
    "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.259 Mobile Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Opera/99.0.4779.89 Chrome/120.0.6099.259 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; SM-A546U) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/20.0 Chrome/120.0.6099.259 Mobile Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.2210.144 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8a) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.259 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6099.280 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; Redmi Note 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.259 Mobile Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/20.0 Chrome/120.0.6099.259 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.259 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.2210.144",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/18.0 Chrome/119.0.6099.259 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.3) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1"
]

# Global stop flag for each chat
stop_sharing_flags = {}

# Daily share limit
DAILY_SHARE_LIMIT = 5000

# Track shares per chat ID
share_counts = {}  # {chat_id: count}
reset_times = {}   # {chat_id: datetime}

gome_token = []
def get_token(input_file):
    gome_token = []
    for cookie in input_file:
        cookie = cookie.strip()
        if not cookie:
            continue
        header_ = {
            'authority': 'business.facebook.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
            'cache-control': 'max-age=0',
            'cookie': cookie,
            'referer': 'https://www.facebook.com/',
            'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': random.choice(user_agents)
        }
        try:
            home_business = requests.get('https://business.facebook.com/content_management', headers=header_, timeout=15).text
            if 'EAAG' in home_business:
                token = home_business.split('EAAG')[1].split('","')[0]
                cookie_token = f'{cookie}|EAAG{token}'
                gome_token.append(cookie_token)
            else:
                print(f"[!] Không thể lấy token từ cookie: {cookie[:50]}... Cookie có thể không hợp lệ.")
        except requests.exceptions.RequestException as e:
            print(f"[!] Lỗi khi lấy token cho cookie: {cookie[:50]}... {e}")
        except Exception as e:
             print(f"[!] Lỗi không mong muốn khi lấy token cho cookie: {cookie[:50]}... {e}")
    return gome_token

def share(tach, id_share):
    cookie = tach.split('|')[0]
    token = tach.split('|')[1]
    he = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate',
        'connection': 'keep-alive',
        'content-length': '0',
        'cookie': cookie,
        'host': 'graph.facebook.com',
        'user-agent': random.choice(user_agents),
        'referer': f'https://m.facebook.com/{id_share}'
    }
    try:
        res = requests.post(f'https://graph.facebook.com/me/feed?link=https://m.facebook.com/{id_share}&published=0&access_token={token}', headers=he, timeout=10).json()
        if 'id' in res:
            return True
        else:
            print(f"[!] Share thất bại: ID: {id_share} - Phản hồi: {res}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"[!] Lỗi request share: ID: {id_share} - {e}")
        return False
    except Exception as e:
        print(f"[!] Lỗi không mong muốn khi share: ID: {id_share} - {e}")
        return False


def share_thread_telegram(tach, id_share, chat_id):
    if stop_sharing_flags.get(chat_id, False):
        return False # Stop sharing
    if share(tach, id_share):
        return True
    else:
        return False


# Telegram Bot Handlers
share_data = {}  # Store user-specific data

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Chào mừng! Sử dụng /share để bắt đầu.")

@bot.message_handler(commands=['share'])
def share_command(message):
    chat_id = message.chat.id

    # Check if daily limit is reached
    if chat_id in share_counts and share_counts[chat_id] >= DAILY_SHARE_LIMIT:
        bot.reply_to(message, f"Đã đạt giới hạn {DAILY_SHARE_LIMIT} share hàng ngày. Vui lòng thử lại sau.")
        return

    share_data[chat_id] = {}  # Initialize data for the user
    # Create a stop button
    markup = types.InlineKeyboardMarkup()
    stop_button = types.InlineKeyboardButton("Dừng Share", callback_data="stop_share")
    markup.add(stop_button)
    bot.send_message(chat_id, "Vui lòng gửi file chứa cookie (cookies.txt).", reply_markup=markup)
    bot.register_next_step_handler(message, process_cookie_file)

@bot.callback_query_handler(func=lambda call: call.data == "stop_share")
def stop_share_callback(call):
    chat_id = call.message.chat.id
    stop_sharing_flags[chat_id] = True  # Set the stop flag
    bot.send_message(chat_id, "Đã nhận lệnh dừng share. Vui lòng chờ quá trình hoàn tất.")

@bot.message_handler(commands=['reset'])
def reset_command(message):
    chat_id = message.chat.id
    try:
        bot.reset_data()
        bot.reply_to(message, "Bot đã được khởi động lại.")
    except Exception as e:
        bot.reply_to(message, f"Có lỗi xảy ra khi reset bot: {e}")


def process_cookie_file(message):
    chat_id = message.chat.id
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        file_content = downloaded_file.decode('utf-8').splitlines()
        share_data[chat_id]['cookie_file'] = file_content
        bot.send_message(chat_id, "Đã nhận file cookie. Vui lòng nhập ID bài viết cần share.")
        bot.register_next_step_handler(message, process_id)
    except Exception as e:
        bot.reply_to(message, f"Lỗi khi xử lý file: {e}")
        del share_data[chat_id]  # Clear data

def process_id(message):
    chat_id = message.chat.id
    id_share = message.text.strip()
    if not id_share.isdigit():
        bot.reply_to(message, "ID không hợp lệ. Vui lòng nhập lại ID bài viết cần share.")
        bot.register_next_step_handler(message, process_id)
        return

    share_data[chat_id]['id_share'] = id_share
    bot.send_message(chat_id, "Vui lòng nhập delay giữa các lần share (giây).")
    bot.register_next_step_handler(message, process_delay)


def process_delay(message):
    chat_id = message.chat.id
    delay_str = message.text.strip()
    try:
        delay = int(delay_str)
        if delay < 0:
              raise ValueError
    except ValueError:
        bot.reply_to(message, "Delay không hợp lệ. Vui lòng nhập lại delay (giây) là một số dương.")
        bot.register_next_step_handler(message, process_delay)
        return

    share_data[chat_id]['delay'] = delay
    bot.send_message(chat_id, "Vui lòng nhập tổng số lượng share (0 để không giới hạn).")
    bot.register_next_step_handler(message, process_total_shares)

def process_total_shares(message):
    chat_id = message.chat.id
    total_share_limit_str = message.text.strip()
    try:
        total_share_limit = int(total_share_limit_str)
        if total_share_limit < 0:
            raise ValueError
    except ValueError:
        bot.reply_to(message, "Số lượng share không hợp lệ. Vui lòng nhập lại tổng số lượng share (0 để không giới hạn) là một số dương.")
        bot.register_next_step_handler(message, process_total_shares)
        return

    share_data[chat_id]['total_share_limit'] = total_share_limit
    # Before starting, create the initial message
    markup = types.InlineKeyboardMarkup()
    stop_button = types.InlineKeyboardButton("Dừng Share", callback_data="stop_share")
    markup.add(stop_button)
    bot.send_message(chat_id, "Bắt đầu share...", reply_markup=markup) # Display 'Stop' button here
    start_sharing(chat_id)

def start_sharing(chat_id):
    data = share_data.get(chat_id)
    if not data:
        bot.send_message(chat_id, "Dữ liệu không đầy đủ. Vui lòng bắt đầu lại bằng lệnh /share.")
        return

    input_file = data['cookie_file']
    id_share = data['id_share']
    delay = data['delay']
    total_share_limit = data['total_share_limit']

    all_tokens = get_token(input_file)
    total_live = len(all_tokens)

    if total_live == 0:
        bot.send_message(chat_id, "Không tìm thấy token hợp lệ nào.")
        del share_data[chat_id]
        return

    bot.send_message(chat_id, f"Tìm thấy {total_live} token hợp lệ.")

    # Initialize or retrieve share count and reset time for this chat
    if chat_id not in share_counts:
        share_counts[chat_id] = 0
        reset_times[chat_id] = datetime.now().date()  # Today's date
    else:
        # Check if it's a new day, reset share count if needed
        if reset_times[chat_id] < datetime.now().date():
            share_counts[chat_id] = 0
            reset_times[chat_id] = datetime.now().date()

    stt = 0
    shared_count = 0
    successful_shares = 0 # Track successful shares
    continue_sharing = True
    stop_sharing_flags[chat_id] = False  # Reset stop flag at start
    while continue_sharing:
        for tach in all_tokens:
            if stop_sharing_flags.get(chat_id, False):
                continue_sharing = False
                break  # Exit inner loop

            # Check daily limit *before* attempting to share
            if share_counts[chat_id] >= DAILY_SHARE_LIMIT:
                bot.send_message(chat_id, f"Đã đạt giới hạn {DAILY_SHARE_LIMIT} share hàng ngày. Vui lòng thử lại sau.")
                continue_sharing = False
                break

            stt += 1
            success = share_thread_telegram(tach, id_share, chat_id)
            if success:
                successful_shares += 1
                share_counts[chat_id] += 1  # Increment the count
            time.sleep(delay)
            shared_count += 1

            if total_share_limit > 0 and shared_count >= total_share_limit:
                continue_sharing = False
                break


    bot.send_message(chat_id, "Quá trình share hoàn tất.")
    if total_share_limit > 0 and shared_count >= total_share_limit:
        bot.send_message(chat_id, f"Đạt giới hạn share là {total_share_limit} shares.")
    bot.send_message(chat_id, f"Tổng cộng {successful_shares} share thành công.") # Final count

    del share_data[chat_id]
    gome_token.clear()
    stop_sharing_flags[chat_id] = False  # Reset



if __name__ == "__main__":
    try:
        print("Bot is running...")
        bot.infinity_polling()
    except KeyboardInterrupt:
        print("Bot stopped.")
        sys.exit()