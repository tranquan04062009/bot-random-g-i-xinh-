import sys
import os
import requests
import threading
import time
import json
import random
from time import strftime
from datetime import datetime, timedelta
from telethon import TelegramClient, events, sync, Button
from queue import Queue
from faker import Faker  # For more advanced fingerprinting


# --- REQUIRED: Telegram API ID and Hash ---
API_ID = 22656641  # Replace with your API ID
API_HASH = '8bb9b539dd910e0b033c6637b9788e90'  # Replace with your API Hash.  DO NOT SHARE THIS!

# Replace with your Telegram bot token
BOT_TOKEN = "7903504769:AAEMX3AUeOgGXvHNMQ5x7T7XcewuK90quNQ"

# Use Telethon's Bot Token authentication
bot = TelegramClient('bot', api_id=API_ID, api_hash=API_HASH).start(bot_token=BOT_TOKEN)


# --- Fingerprint Generation ---
fake = Faker()

def generate_fingerprint():
    """Generates a realistic browser fingerprint."""
    profile = fake.simple_profile()  # Get a basic user profile
    user_agent = fake.user_agent()  # Get a random user agent

    # More advanced fingerprinting attributes (can be expanded)
    platform = random.choice(["Windows NT 10.0; Win64; x64", "Macintosh; Intel Mac OS X 10_15_7", "X11; Linux x86_64"])
    accept_language = fake.locale().replace("_", "-")  # e.g., en-US, fr-FR
    screen_width = random.choice([1920, 1366, 1280, 1600])
    screen_height = random.choice([1080, 768, 800, 900])
    color_depth = random.choice([24, 32])
    # Example: Add more detailed platform information based on user-agent
    if "Windows" in user_agent:
          platform = random.choice(["Windows NT 10.0; Win64; x64; rv:122.0",
                                   "Windows NT 10.0; Win64; x64",
                                    "Windows NT 6.1; Win64; x64"])
    elif "Macintosh" in user_agent:
        platform = random.choice(["Macintosh; Intel Mac OS X 14.2; rv:122.0",
                                 "Macintosh; Intel Mac OS X 10_15_7",
                                  "Macintosh; Intel Mac OS X 14_2"])
    elif "Linux" in user_agent:
          platform = random.choice(["X11; Linux x86_64; rv:122.0",
                                 "X11; Linux x86_64",
                                   "X11; Ubuntu; Linux x86_64; rv:122.0"])

    fingerprint = {
        'user_agent': user_agent,
        'accept_language': accept_language,
        'platform': platform,
        'screen_width': screen_width,
        'screen_height': screen_height,
        'color_depth': color_depth,
        # Add other fingerprinting attributes as needed (e.g., WebGL, Canvas, etc.)
    }
    return fingerprint


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
        fingerprint = generate_fingerprint() # Generate a new fingerprint

        header_ = {
            'authority': 'business.facebook.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-language': fingerprint['accept_language'], # Use the generated language
            'cache-control': 'max-age=0',
            'cookie': cookie,
            'referer': 'https://www.facebook.com/',
            'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',  #This can also be randomized
            'sec-ch-ua-mobile': '?0',  # Consistent with desktop user agents
            'sec-ch-ua-platform': f'"{fingerprint["platform"].split(";")[0]}"',  # Extract platform
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': fingerprint['user_agent'], # Use generated User-Agent
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
    fingerprint = generate_fingerprint()  # Generate a new fingerprint for each share

    he = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate',
        'accept-language': fingerprint['accept_language'],
        'connection': 'keep-alive',
        'content-length': '0',
        'cookie': cookie,
        'host': 'graph.facebook.com',
        'user-agent': fingerprint['user_agent'],
        'referer': f'https://m.facebook.com/{id_share}',
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

# --- Telethon Event Handlers ---
message_queue = Queue()

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond("Chào mừng! Sử dụng /share để bắt đầu.")

@bot.on(events.NewMessage(pattern='/share'))
async def share_command(event):
    chat_id = event.chat_id

    # Check if daily limit is reached
    if chat_id in share_counts and share_counts[chat_id] >= DAILY_SHARE_LIMIT:
        await event.respond(f"Đã đạt giới hạn {DAILY_SHARE_LIMIT} share hàng ngày. Vui lòng thử lại sau.")
        return

    share_data[chat_id] = {}  # Initialize data for the user
    # Create a stop button
    await event.respond("Vui lòng gửi file chứa cookie (cookies.txt).", buttons=[Button.inline("Dừng Share", b"stop_share")])
    message_queue.put((process_cookie_file, event)) # Add to queue

@bot.on(events.CallbackQuery(data=b"stop_share"))
async def stop_share_callback(event):
    chat_id = event.chat_id
    stop_sharing_flags[chat_id] = True  # Set the stop flag
    await event.respond("Đã nhận lệnh dừng share. Vui lòng chờ quá trình hoàn tất.")
    await event.edit("Đã dừng chia sẻ.") # Acknowledge the button press


@bot.on(events.NewMessage(pattern='/reset'))
async def reset_command(event):
    chat_id = event.chat_id
    try:
        # Clear relevant data structures
        share_counts[chat_id] = 0
        reset_times[chat_id] = datetime.now().date()
        if chat_id in share_data:
            del share_data[chat_id]
        stop_sharing_flags[chat_id] = False
        await event.respond("Bot đã được khởi động lại.")
    except Exception as e:
        await event.respond(f"Có lỗi xảy ra khi reset bot: {e}")



async def process_cookie_file(event):
    chat_id = event.chat_id
    try:
        if not event.message.media:
            await event.reply("Vui lòng gửi file cookie (cookies.txt).")
            message_queue.put((process_cookie_file, event))  # Put back in the queue
            return

        file_content = await bot.download_file(event.message.media)
        file_content = file_content.decode('utf-8').splitlines()

        share_data[chat_id]['cookie_file'] = file_content
        await event.respond("Đã nhận file cookie. Vui lòng nhập ID bài viết cần share.")
        message_queue.put((process_id, event))
    except Exception as e:
        await event.reply(f"Lỗi khi xử lý file: {e}")
        if chat_id in share_data:  # Check if exists before deleting
            del share_data[chat_id]


async def process_id(event):
    chat_id = event.chat_id
    id_share = event.message.text.strip()
    if not id_share.isdigit():
        await event.reply("ID không hợp lệ. Vui lòng nhập lại ID bài viết cần share.")
        message_queue.put((process_id, event)) # Put back in queue for retry.
        return

    share_data[chat_id]['id_share'] = id_share
    await event.respond("Vui lòng nhập delay giữa các lần share (giây).")
    message_queue.put((process_delay, event))


async def process_delay(event):
    chat_id = event.chat_id
    delay_str = event.message.text.strip()
    try:
        delay = int(delay_str)
        if delay < 0:
            raise ValueError
    except ValueError:
        await event.reply("Delay không hợp lệ. Vui lòng nhập lại delay (giây) là một số dương.")
        message_queue.put((process_delay, event))  # Re-add to queue
        return

    share_data[chat_id]['delay'] = delay
    await event.respond("Vui lòng nhập tổng số lượng share (0 để không giới hạn).")
    message_queue.put((process_total_shares, event))

async def process_total_shares(event):
    chat_id = event.chat_id
    total_share_limit_str = event.message.text.strip()
    try:
        total_share_limit = int(total_share_limit_str)
        if total_share_limit < 0:
            raise ValueError
    except ValueError:
        await event.reply("Số lượng share không hợp lệ.  Vui lòng nhập lại tổng số lượng share (0 để không giới hạn) là một số dương.")
        message_queue.put((process_total_shares, event))
        return

    share_data[chat_id]['total_share_limit'] = total_share_limit
    await event.respond("Bắt đầu share...", buttons=[Button.inline("Dừng Share", b"stop_share")])
    start_sharing(chat_id)  # No 'await' here, as it blocks the event loop



def start_sharing(chat_id):
    # Run the actual sharing in a separate thread
    threading.Thread(target=share_task, args=(chat_id,)).start()


def share_task(chat_id):
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

    if chat_id in share_data:  # Check before deleting
        del share_data[chat_id]
    gome_token.clear()
    stop_sharing_flags[chat_id] = False  # Reset

def process_message_queue():
    while True:
        if not message_queue.empty():
            handler, event = message_queue.get()
            bot.loop.run_until_complete(handler(event))
        else:
            time.sleep(0.1)  # Check the queue periodically

if __name__ == "__main__":
    try:
        print("Bot is running...")
        # Start the message queue processor in a separate thread
        queue_thread = threading.Thread(target=process_message_queue)
        queue_thread.daemon = True  # Allow the program to exit even if the thread is running
        queue_thread.start()

        bot.run_until_disconnected()
    except KeyboardInterrupt:
        print("Bot stopped.")
        sys.exit()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)