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
from datetime import datetime, timedelta, timezone
import queue
from faker import Faker

# Thay thế bằng token bot Telegram của bạn
BOT_TOKEN = "7903504769:AAFeKxomzBB-QtDzwOXojBofz9vju2CsDKc"  # Thay thế bằng token thật của bạn
bot = telebot.TeleBot(BOT_TOKEN)

# Khởi tạo Faker
fake = Faker()
fake_vi = Faker('vi_VN')  # Phiên bản tiếng Việt

# Danh sách user agents (mở rộng)
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

# --- Hằng số ---
DAILY_SHARE_LIMIT = 5000
VN_TIMEZONE = timezone(timedelta(hours=7))  # Múi giờ Việt Nam (GMT+7)

# --- Cấu trúc dữ liệu ---
# Dữ liệu cho mỗi người dùng
share_counts = {}  # {user_id: count}
reset_times = {}  # {user_id: datetime}
stop_sharing_flags = {}  # {user_id: True/False}
share_data = {} # {user_id: {cookie_file: [], id_share: str, delay: int, total_share_limit: int}}

# ---  VIP USER IDs ---
VIP_USER_IDS = {123456789, 987654321}  # Thêm các user ID VIP vào đây


# --- Hàm hỗ trợ ---

def get_random_headers():
    """Tạo header ngẫu nhiên, bao gồm fingerprint trình duyệt."""
    headers = {
        'authority': 'business.facebook.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': fake.locale(),
        'cache-control': 'max-age=0',
        'referer': 'https://www.facebook.com/',
        'sec-ch-ua': f'"{fake.chrome(version_from=80, version_to=120)}";v="{random.randint(80, 120)}", "Not/A)Brand";v="99"',
        'sec-ch-ua-mobile': '?0' if random.random() > 0.5 else '?1',
        'sec-ch-ua-platform': f'"{random.choice(["Windows", "Linux", "macOS"])}"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': fake.user_agent(),
    }
    return headers

def get_token(input_file):
    """Lấy token hợp lệ từ danh sách cookie."""
    valid_tokens = []
    for cookie in input_file:
        cookie = cookie.strip()
        if not cookie:  # Bỏ qua dòng trống
            continue

        headers = get_random_headers()
        headers['cookie'] = cookie

        try:
            response = requests.get('https://business.facebook.com/content_management', headers=headers, timeout=15)
            response.raise_for_status()

            if response.ok: # Check for successful status code
                home_business = response.text
                if 'EAAG' in home_business:
                    token = home_business.split('EAAG')[1].split('","')[0]
                    cookie_token = f'{cookie}|EAAG{token}'
                    valid_tokens.append(cookie_token)
                else:
                    print(f"[!] Không thể lấy token từ cookie: {cookie[:50]}... Cookie có thể không hợp lệ.")
            else:
                print(f"[!] Lỗi khi lấy token cho cookie: {cookie[:50]}... Status Code: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"[!] Lỗi khi lấy token cho cookie: {cookie[:50]}... Lỗi request: {e}")
        except Exception as e:
            print(f"[!] Lỗi không mong muốn khi lấy token cho cookie: {cookie[:50]}...: {e}")
    return valid_tokens



def share(tach, id_share):
    """Chia sẻ bài viết sử dụng cookie và token đã cho."""
    cookie = tach.split('|')[0]
    token = tach.split('|')[1]

    headers = get_random_headers()
    headers.update({
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate',
        'connection': 'keep-alive',
        'content-length': '0',
        'cookie': cookie,
        'host': 'graph.facebook.com',
        'referer': f'https://m.facebook.com/{id_share}'
    })

    try:
        res = requests.post(f'https://graph.facebook.com/me/feed?link=https://m.facebook.com/{id_share}&published=0&access_token={token}', headers=headers, timeout=10)
        res.raise_for_status()
        if res.ok:  # Explicitly check for successful status
            response_json = res.json()
            if 'id' in response_json:
                return True
            else:
                print(f"[!] Chia sẻ thất bại: ID: {id_share} - Phản hồi: {response_json}")
                return False
        else:
            print(f"[!] Chia sẻ thất bại: ID: {id_share} - Status Code: {res.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"[!] Lỗi request chia sẻ: ID: {id_share} - {e}")
        return False
    except Exception as e:
        print(f"[!] Lỗi không mong muốn khi chia sẻ: ID: {id_share} - {e}")
        return False



def share_thread_telegram(tach, id_share, user_id):
    """Chia sẻ bài viết, kiểm tra cờ dừng."""
    if stop_sharing_flags.get(user_id, False):
        return False
    return share(tach, id_share)


def reset_user_data(user_id):
    """Đặt lại dữ liệu chia sẻ cho một người dùng cụ thể."""
    if user_id in share_data:
        del share_data[user_id]
    if user_id in stop_sharing_flags:
        stop_sharing_flags[user_id] = False
    if user_id in share_counts:
        share_counts[user_id] = 0
    reset_times[user_id] = datetime.now(VN_TIMEZONE).date()

# --- Bộ xử lý Bot Telegram ---
@bot.message_handler(func=lambda message: True, content_types=['text', 'document'])
def handle_message(message):
    """Xử lý một tin nhắn, định tuyến dựa trên loại nội dung và trạng thái."""
    if not (message.chat.type == 'private' or (message.chat.type in ['group', 'supergroup', 'channel'] and message.text.startswith('/'))):
        return  # Bỏ qua nếu không phải là tin nhắn riêng tư hoặc lệnh trong nhóm

    user_id = message.from_user.id

    if message.content_type == 'document':
        # Xử lý tài liệu *trước* nếu đang trong quá trình /share
        if message.chat.type == 'private' and user_id in share_data and 'cookie_file' not in share_data[user_id]:
            process_cookie_file(message)
            return  # Quan trọng: return ở đây để không xử lý tin nhắn văn bản sau khi đã nhận file

    elif message.content_type == 'text':
        if message.text.startswith('/'):
            command_handler(message)  # Luôn xử lý lệnh
        elif user_id in share_data:
            # Xử lý tin nhắn văn bản nếu đang trong quá trình /share
            if 'cookie_file' not in share_data[user_id]:
                bot.reply_to(message, "Vui lòng gửi file cookie trước.")
            elif 'id_share' not in share_data[user_id]:
                process_id(message)
            elif 'delay' not in share_data[user_id]:
                process_delay(message)
            elif 'total_share_limit' not in share_data[user_id]:
                process_total_shares(message)



def command_handler(message):
    """Xử lý các lệnh (/start, /share, /reset)."""
    try:
        if message.text.startswith('/start'):
            start(message)
        elif message.text.startswith('/share'):
            share_command(message)
        elif message.text.startswith('/reset'):
            reset_command(message)
    except Exception as e:
        bot.reply_to(message, f"Đã xảy ra lỗi khi xử lý lệnh của bạn: {e}")

@bot.message_handler(commands=['start'])
def start(message):
    """Xử lý lệnh /start."""
    bot.reply_to(message, "Chào mừng! Sử dụng /share để bắt đầu chia sẻ.")

@bot.message_handler(commands=['share'])
def share_command(message):
    """Xử lý lệnh /share."""
    user_id = message.from_user.id

    # Bắt buộc trò chuyện riêng tư cho /share
    if message.chat.type != 'private':
        bot.reply_to(message, "Lệnh /share chỉ hoạt động trong các cuộc trò chuyện riêng tư. Vui lòng nhắn tin trực tiếp cho bot.")
        return

    # Kiểm tra giới hạn hàng ngày và VIP
    if user_id not in VIP_USER_IDS and user_id in share_counts and share_counts[user_id] >= DAILY_SHARE_LIMIT:
        bot.reply_to(message, f"Bạn đã đạt đến giới hạn chia sẻ hàng ngày là {DAILY_SHARE_LIMIT}. Vui lòng thử lại vào ngày mai hoặc nâng cấp lên VIP để không giới hạn.")
        return

    # Thông báo cho người dùng VIP
    if user_id in VIP_USER_IDS:
        bot.send_message(message.chat.id, "Bạn là người dùng VIP, không có giới hạn chia sẻ hàng ngày.")

    # Khởi tạo dữ liệu chia sẻ
    share_data[user_id] = {}
    markup = types.InlineKeyboardMarkup()
    stop_button = types.InlineKeyboardButton("Dừng Chia Sẻ", callback_data="stop_share")
    markup.add(stop_button)
    bot.send_message(message.chat.id, "Vui lòng gửi file cookie (cookies.txt).", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "stop_share")
def stop_share_callback(call):
    """Xử lý sự kiện nhấn nút 'Dừng Chia sẻ'."""
    user_id = call.from_user.id
    stop_sharing_flags[user_id] = True
    bot.edit_message_text("Đã dừng chia sẻ. Vui lòng đợi quá trình hiện tại kết thúc.", call.message.chat.id, call.message.message_id)


@bot.message_handler(commands=['reset'])
def reset_command(message):
    """Xử lý lệnh /reset."""
    user_id = message.from_user.id
    reset_user_data(user_id)  # Sử dụng hàm hỗ trợ
    bot.reply_to(message, "Bot đã được đặt lại cho bạn.")




def process_cookie_file(message):
    """Xử lý file cookie đã tải lên."""
    user_id = message.from_user.id
    chat_id = message.chat.id
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        file_content = downloaded_file.decode('utf-8').splitlines()
        share_data[user_id]['cookie_file'] = file_content
        bot.send_message(chat_id, "Đã nhận file cookie. Vui lòng nhập ID bài viết cần chia sẻ.")
    except Exception as e:
        bot.reply_to(message, f"Lỗi khi xử lý file: {e}")
        reset_user_data(user_id)  # Đặt lại nếu có lỗi


def process_id(message):
    """Xử lý ID bài viết."""
    user_id = message.from_user.id
    chat_id = message.chat.id
    id_share = message.text.strip()
    if not id_share.isdigit():
        bot.reply_to(message, "ID không hợp lệ. Vui lòng nhập lại ID bài viết.")
        return

    share_data[user_id]['id_share'] = id_share
    bot.send_message(chat_id, "Vui lòng nhập độ trễ giữa các lần chia sẻ (tính bằng giây).")


def process_delay(message):
    """Xử lý độ trễ."""
    user_id = message.from_user.id
    chat_id = message.chat.id
    delay_str = message.text.strip()
    try:
        delay = int(delay_str)
        if delay < 0:
            raise ValueError
    except ValueError:
        bot.reply_to(message, "Độ trễ không hợp lệ. Vui lòng nhập độ trễ (tính bằng giây) là một số.")
        return

    share_data[user_id]['delay'] = delay
    bot.send_message(chat_id, "Vui lòng nhập tổng số lượt chia sẻ (0 để không giới hạn).")


def process_total_shares(message):
    """Xử lý giới hạn tổng số lượt chia sẻ."""
    user_id = message.from_user.id
    chat_id = message.chat.id
    total_share_limit_str = message.text.strip()
    try:
        total_share_limit = int(total_share_limit_str)
        if total_share_limit < 0:
            raise ValueError
    except ValueError:
        bot.reply_to(message, "Giới hạn chia sẻ không hợp lệ. Vui lòng nhập tổng số lượt chia sẻ (0 để không giới hạn) là một số.")
        return

    share_data[user_id]['total_share_limit'] = total_share_limit
    markup = types.InlineKeyboardMarkup()
    stop_button = types.InlineKeyboardButton("Dừng Chia sẻ", callback_data="stop_share")
    markup.add(stop_button)
    bot.send_message(chat_id, "Bắt đầu chia sẻ...", reply_markup=markup)
    start_sharing(user_id)



def start_sharing(user_id):
    """Bắt đầu quá trình chia sẻ."""
    chat_id = bot.get_chat(user_id).id # Cần chat id để gửi tin nhắn
    data = share_data.get(user_id)
    if not data:
        bot.send_message(chat_id, "Dữ liệu không đầy đủ. Vui lòng bắt đầu lại với /share.")
        return

    input_file = data['cookie_file']
    id_share = data['id_share']
    delay = data['delay']
    total_share_limit = data['total_share_limit']

    all_tokens = get_token(input_file)
    total_live = len(all_tokens)

    if total_live == 0:
        bot.send_message(chat_id, "Không tìm thấy token hợp lệ nào.")
        reset_user_data(user_id)
        return

    bot.send_message(chat_id, f"Tìm thấy {total_live} token hợp lệ.")

    # Khởi tạo hoặc đặt lại số lượt đếm hàng ngày, trừ VIP
    if user_id not in VIP_USER_IDS and (user_id not in share_counts or reset_times.get(user_id) != datetime.now(VN_TIMEZONE).date()):
          reset_user_data(user_id)


    stt = 0
    shared_count = 0
    successful_shares = 0
    continue_sharing = True
    stop_sharing_flags[user_id] = False

    while continue_sharing:
        current_date = datetime.now(VN_TIMEZONE).date()
        # Reset if the date has changed (for non-VIPs)
        if user_id not in VIP_USER_IDS and reset_times.get(user_id) != current_date:
            reset_user_data(user_id)
        for tach in all_tokens:
            if stop_sharing_flags.get(user_id, False):
                continue_sharing = False
                break
            # --- CRITICAL DAILY LIMIT CHECK (with VIP bypass) ---
            if user_id not in VIP_USER_IDS and share_counts.get(user_id, 0) >= DAILY_SHARE_LIMIT:
                bot.send_message(chat_id, f"Bạn đã đạt đến giới hạn chia sẻ hàng ngày là {DAILY_SHARE_LIMIT}. Vui lòng thử lại vào ngày mai hoặc nâng cấp lên VIP để không giới hạn.")
                continue_sharing = False
                break  # Exit the inner loop immediately
            # --- END CRITICAL CHECK ---
            stt += 1
            success = share_thread_telegram(tach, id_share, user_id)  # Truyền user_id
            if success:
                successful_shares += 1
                # --- CORRECT INCREMENT (with VIP bypass) ---
                if user_id not in VIP_USER_IDS:
                    share_counts[user_id] = share_counts.get(user_id, 0) + 1
                # --- END CORRECT INCREMENT ---

            # Check if total share limit reached
            if total_share_limit > 0 and shared_count + 1 > total_share_limit:
                continue_sharing = False
                break

            shared_count += 1 #Increment the count of attempted share
            time.sleep(delay)



    bot.send_message(chat_id, "Quá trình chia sẻ hoàn tất.")
    if total_share_limit > 0:
      bot.send_message(chat_id, f"Đã thực hiện {shared_count} lượt chia sẻ / Giới hạn: {total_share_limit} lượt.")
    bot.send_message(chat_id, f"Tổng số lượt chia sẻ thành công: {successful_shares}.")
    reset_user_data(user_id)


# ---  Vòng lặp chính ---

if __name__ == "__main__":
    print("Bot đang chạy...")
    while True:
        try:
            # Sử dụng bot.polling() với timeout
            bot.polling(timeout=10, none_stop = True)  # Kiểm tra cập nhật mỗi 10 giây
        except Exception as e:
            print(f"Lỗi trong quá trình polling: {e}")
            time.sleep(5)  # Đợi 5 giây trước khi thử lại