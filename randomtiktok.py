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
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import DocumentAttributeFilename  # Import for filename checking
from queue import Queue
from faker import Faker



# --- REQUIRED: Telegram API ID and Hash ---
API_ID = 22656641
API_HASH = '8bb9b539dd910e0b033c6637b9788e90'

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

    # More advanced fingerprinting attributes
    platform = random.choice(["Windows NT 10.0; Win64; x64", "Macintosh; Intel Mac OS X 10_15_7", "X11; Linux x86_64"])
    accept_language = fake.locale().replace("_", "-")  # e.g., en-US, fr-FR
    screen_width = random.choice([1920, 1366, 1280, 1600])
    screen_height = random.choice([1080, 768, 800, 900])
    color_depth = random.choice([24, 32])
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
        fingerprint = generate_fingerprint()

        header_ = {
            'authority': 'business.facebook.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-language': fingerprint['accept_language'],
            'cache-control': 'max-age=0',
            'cookie': cookie,
            'referer': 'https://www.facebook.com/',
            'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': f'"{fingerprint["platform"].split(";")[0]}"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': fingerprint['user_agent'],
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
    fingerprint = generate_fingerprint()

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
        return False
    if share(tach, id_share):
        return True
    else:
        return False


# --- Telethon Event Handlers ---
message_queue = Queue()

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond("Chào mừng! Sử dụng /share để bắt đầu.")

@bot.on(events.NewMessage(pattern='/share'))
async def share_command(event):
    chat_id = event.chat_id
    user_id = event.sender_id

    if event.is_group or event.is_channel:
        user = await bot.get_entity(user_id)
        first_name = user.first_name if user.first_name else "User"
        await event.respond(
            f"@{first_name}, vui lòng chat riêng với bot để sử dụng tính năng /share.",
            buttons=[Button.url("Chat Riêng", f"https://t.me/{bot.me.username}")]
        )
        return

    if chat_id in share_counts and share_counts[chat_id] >= DAILY_SHARE_LIMIT:
        await event.respond(f"Đã đạt giới hạn {DAILY_SHARE_LIMIT} share hàng ngày. Vui lòng thử lại sau.")
        return

    share_data[chat_id] = {'waiting_for_file': True}  # Initialize AND set waiting_for_file
    await event.respond("Vui lòng gửi file chứa cookie (cookies.txt).", buttons=[Button.inline("Dừng Share", b"stop_share")])
    # NO message_queue.put here! We wait for the file in handle_all_messages



@bot.on(events.CallbackQuery(data=b"stop_share"))
async def stop_share_callback(event):
    chat_id = event.chat_id
    stop_sharing_flags[chat_id] = True
    await event.respond("Đã nhận lệnh dừng share. Vui lòng chờ quá trình hoàn tất.")
    await event.edit("Đã dừng chia sẻ.")


@bot.on(events.NewMessage(pattern='/reset'))
async def reset_command(event):
    chat_id = event.chat_id
    if event.is_group or event.is_channel:
        user = await bot.get_entity(event.sender_id)
        first_name = user.first_name if user.first_name else "User"
        await event.respond(
            f"@{first_name}, vui lòng chat riêng với bot để sử dụng tính năng /reset.",
            buttons=[Button.url("Chat Riêng", f"https://t.me/{bot.me.username}")]
        )
        return
    try:
        share_counts[chat_id] = 0
        reset_times[chat_id] = datetime.now().date()
        if chat_id in share_data:
            del share_data[chat_id]
        stop_sharing_flags[chat_id] = False
        await event.respond("Bot đã được khởi động lại.")
    except Exception as e:
        await event.respond(f"Có lỗi xảy ra khi reset bot: {e}")


# --- File Handling - Improved ---
@bot.on(events.NewMessage)
async def handle_all_messages(event):
    chat_id = event.chat_id
    # Only proceed if this chat is in the process of a /share session
    if chat_id in share_data and share_data[chat_id].get('waiting_for_file'): # Safely check for the key
        if event.message.media:
            # Check if it's a document (file)
            if hasattr(event.message.media, 'document'):
                # Check for filename attribute (more reliable)
                is_valid_file = False
                for attribute in event.message.media.document.attributes:
                    if isinstance(attribute, DocumentAttributeFilename):
                        # Basic filename check
                        if attribute.file_name.endswith('.txt'):
                           is_valid_file = True
                           break

                if is_valid_file:
                    message_queue.put((process_cookie_file, event)) # Put in queue
                    # We DO NOT remove waiting_for_file here; it's done in process_cookie_file
                else:
                     await event.reply("Vui lòng gửi file cookie có định dạng .txt.")
            else:
                await event.reply("Vui lòng gửi file cookie (cookies.txt).") #Not a document
        else:
            await event.reply("Vui lòng gửi file cookie (cookies.txt).") # Not media

async def process_cookie_file(event):
    chat_id = event.chat_id
    try:
        # Download the file
        file_content = await bot.download_file(event.message.media)
        if not file_content:
            await event.reply("File không hợp lệ hoặc không có nội dung. Vui lòng gửi lại file cookie (cookies.txt).")
            # DO NOT return; re-set waiting_for_file and re-prompt
            share_data[chat_id]['waiting_for_file'] = True
            await event.respond("Vui lòng gửi lại file chứa cookie (cookies.txt).")
            return # Ensure the function exits here

        file_content = file_content.decode('utf-8').splitlines()

        share_data[chat_id]['cookie_file'] = file_content
        # NOW we remove waiting_for_file.
        del share_data[chat_id]['waiting_for_file']
        await event.respond("Đã nhận file cookie. Vui lòng nhập ID bài viết cần share.")
        message_queue.put((process_id, event))

    except Exception as e:
        await event.reply(f"Lỗi khi xử lý file: {e}")
        if chat_id in share_data:
             # Reset waiting_for_file on error, too, so the user can try again
            if 'waiting_for_file' in share_data[chat_id]: # Check before deleting
                del share_data[chat_id]['waiting_for_file']



async def process_id(event):
    chat_id = event.chat_id
    id_share = event.message.text.strip()
    if not id_share.isdigit():
        await event.reply("ID không hợp lệ. Vui lòng nhập lại ID bài viết cần share.")
        message_queue.put((process_id, event))
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
        message_queue.put((process_delay, event))
        return

    share_data[chat_id]['delay'] = delay
    await event.respond("Vui lòng nhập tổng số lượng share (0 để không giới hạn).")
    message_queue.put((process_total_shares, event))

async def process_total_shares(event):
    chat_id = event.chat_id
    total_share_limit_str = event.message.text.strip()
    try:
        total_share_limit = int(total_share_limit_str)
        if delay < 0:
            raise ValueError
    except ValueError:
        await event.reply("Số lượng share không hợp lệ.  Vui lòng nhập lại tổng số lượng share (0 để không giới hạn) là một số dương.")
        message_queue.put((process_total_shares, event))
        return

    share_data[chat_id]['total_share_limit'] = total_share_limit
    await event.respond("Bắt đầu share...", buttons=[Button.inline("Dừng Share", b"stop_share")])
    start_sharing(chat_id)



def start_sharing(chat_id):
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

    if chat_id not in share_counts:
        share_counts[chat_id] = 0
        reset_times[chat_id] = datetime.now().date()
    else:
        if reset_times[chat_id] < datetime.now().date():
            share_counts[chat_id] = 0
            reset_times[chat_id] = datetime.now().date()

    stt = 0
    shared_count = 0
    successful_shares = 0
    continue_sharing = True
    stop_sharing_flags[chat_id] = False
    while continue_sharing:
        for tach in all_tokens:
            if stop_sharing_flags.get(chat_id, False):
                continue_sharing = False
                break

            if share_counts[chat_id] >= DAILY_SHARE_LIMIT:
                bot.send_message(chat_id, f"Đã đạt giới hạn {DAILY_SHARE_LIMIT} share hàng ngày. Vui lòng thử lại sau.")
                continue_sharing = False
                break

            stt += 1
            success = share_thread_telegram(tach, id_share, chat_id)
            if success:
                successful_shares += 1
                share_counts[chat_id] += 1
            time.sleep(delay)
            shared_count += 1

            if total_share_limit > 0 and shared_count >= total_share_limit:
                continue_sharing = False
                break


    bot.send_message(chat_id, "Quá trình share hoàn tất.")
    if total_share_limit > 0 and shared_count >= total_share_limit:
        bot.send_message(chat_id, f"Đạt giới hạn share là {total_share_limit} shares.")
    bot.send_message(chat_id, f"Tổng cộng {successful_shares} share thành công.")

    if chat_id in share_data:
        del share_data[chat_id]
    gome_token.clear()
    stop_sharing_flags[chat_id] = False

def process_message_queue():
    while True:
        if not message_queue.empty():
            handler, event = message_queue.get()
            bot.loop.run_until_complete(handler(event))
        else:
            time.sleep(0.1)

if __name__ == "__main__":
    try:
        print("Bot is running...")
        queue_thread = threading.Thread(target=process_message_queue)
        queue_thread.daemon = True
        queue_thread.start()

        bot.run_until_disconnected()
    except KeyboardInterrupt:
        print("Bot stopped.")
        sys.exit()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)