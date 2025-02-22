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
import queue
from faker import Faker  # Import Faker for fingerprinting

# Thay thế bằng token bot Telegram của bạn
BOT_TOKEN = "7903504769:AAEMX3AUeOgGXvHNMQ5x7T7XcewuK90quNQ"  # Thay thế bằng token thật của bạn
bot = telebot.TeleBot(BOT_TOKEN)

# Khởi tạo Faker (cho nhiều ngôn ngữ)
fake = Faker()
fake_vi = Faker('vi_VN')  # Phiên bản tiếng Việt

# Danh sách user agents (mở rộng, bao gồm các trình duyệt di động)
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


# Cờ dừng chia sẻ cho mỗi cuộc trò chuyện
stop_sharing_flags = {}

# Giới hạn chia sẻ hàng ngày
DAILY_SHARE_LIMIT = 5000

# Theo dõi số lượt chia sẻ trên mỗi ID cuộc trò chuyện
share_counts = {}  # {chat_id: count}
reset_times = {}   # {chat_id: datetime}

gome_token = []

# --- Định nghĩa hàm ---

def get_random_headers():
    """Tạo header ngẫu nhiên, bao gồm fingerprint trình duyệt."""
    headers = {
        'authority': 'business.facebook.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': fake.locale(),  # Ngôn ngữ ngẫu nhiên
        'cache-control': 'max-age=0',
        'referer': 'https://www.facebook.com/',
        'sec-ch-ua': f'"{fake.chrome(version_from=80, version_to=120)}";v="{random.randint(80, 120)}", "Not/A)Brand";v="99"',  # Biến thể
        'sec-ch-ua-mobile': '?0' if random.random() > 0.5 else '?1',  # Giả lập mobile/desktop
        'sec-ch-ua-platform': f'"{random.choice(["Windows", "Linux", "macOS"])}"', # Hệ điều hành
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': fake.user_agent(),  # User-agent ngẫu nhiên (quan trọng)
    }
    return headers

def get_token(input_file):
    local_gome_token = []
    for cookie in input_file:
        cookie = cookie.strip()
        if not cookie:
            continue

        headers = get_random_headers()  # Lấy header ngẫu nhiên cho mỗi cookie
        headers['cookie'] = cookie  # Thêm cookie vào header

        try:
            home_business = requests.get('https://business.facebook.com/content_management', headers=headers, timeout=15).text
            if 'EAAG' in home_business:
                token = home_business.split('EAAG')[1].split('","')[0]
                cookie_token = f'{cookie}|EAAG{token}'
                local_gome_token.append(cookie_token)
            else:
                print(f"[!] Không thể lấy token từ cookie: {cookie[:50]}... Cookie có thể không hợp lệ.")
        except requests.exceptions.RequestException as e:
            print(f"[!] Lỗi khi lấy token cho cookie: {cookie[:50]}... {e}")
        except Exception as e:
             print(f"[!] Lỗi không mong muốn khi lấy token cho cookie: {cookie[:50]}... {e}")
    return local_gome_token


def share(tach, id_share):
    cookie = tach.split('|')[0]
    token = tach.split('|')[1]

    headers = get_random_headers() # Fingerprint cho mỗi request
    headers.update({ # Thêm các header cần thiết
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate',
        'connection': 'keep-alive',
        'content-length': '0',
        'cookie': cookie,
        'host': 'graph.facebook.com',
        'referer': f'https://m.facebook.com/{id_share}'
    })

    try:
        res = requests.post(f'https://graph.facebook.com/me/feed?link=https://m.facebook.com/{id_share}&published=0&access_token={token}', headers=headers, timeout=10).json()
        if 'id' in res:
            return True
        else:
            print(f"[!] Chia sẻ thất bại: ID: {id_share} - Phản hồi: {res}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"[!] Lỗi request chia sẻ: ID: {id_share} - {e}")
        return False
    except Exception as e:
        print(f"[!] Lỗi không mong muốn khi chia sẻ: ID: {id_share} - {e}")
        return False


def share_thread_telegram(tach, id_share, chat_id):
    if stop_sharing_flags.get(chat_id, False):
        return False  # Dừng chia sẻ
    return share(tach, id_share)



# --- Telegram Bot Handlers ---
share_data = {}  # Lưu trữ dữ liệu người dùng cụ thể

# Tạo hàng đợi tin nhắn
message_queue = queue.Queue()

def handle_message(message):
    """Xử lý một tin nhắn từ hàng đợi."""
    if message.content_type == 'text':
        if message.text.startswith('/'):
            command_handler(message)  # Xử lý lệnh trực tiếp
        else:
            # Định tuyến tin nhắn đến trình xử lý tương ứng dựa trên ngữ cảnh
            chat_id = message.chat.id
            if chat_id in share_data:
                if 'cookie_file' not in share_data[chat_id]:
                    bot.reply_to(message, "Vui lòng gửi file cookie trước.")
                    return
                elif 'id_share' not in share_data[chat_id]:
                    process_id(message)
                elif 'delay' not in share_data[chat_id]:
                    process_delay(message)
                elif 'total_share_limit' not in share_data[chat_id]:
                    process_total_shares(message)

            else: # nếu không có lệnh /share nào được bắt đầu
                bot.reply_to(message, "Vui lòng sử dụng lệnh /share để bắt đầu.")

    elif message.content_type == 'document':
        chat_id = message.chat.id
        if chat_id in share_data and 'cookie_file' not in share_data[chat_id]:
             process_cookie_file(message)
        else:
            bot.reply_to(message, "Vui lòng sử dụng lệnh /share để bắt đầu.")


def command_handler(message):
    """Xử lý các lệnh."""
    if message.text.startswith('/start'):
        start(message)
    elif message.text.startswith('/share'):
        share_command(message)
    elif message.text.startswith('/reset'):
        reset_command(message)
    # Thêm các trình xử lý lệnh khác nếu cần

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Chào mừng! Sử dụng /share để bắt đầu.")

@bot.message_handler(commands=['share'])
def share_command(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Kiểm tra xem tin nhắn có phải từ nhóm hoặc kênh không
    if message.chat.type in ['group', 'supergroup', 'channel']:
        bot.reply_to(message, "Lệnh /share chỉ hoạt động trong chat riêng. Vui lòng nhắn tin riêng cho bot để tiếp tục.")
        return  # Dừng xử lý tiếp cho các yêu cầu từ nhóm/kênh

    # Kiểm tra giới hạn chia sẻ hàng ngày (chỉ khi đó là cuộc trò chuyện riêng tư)
    if chat_id in share_counts and share_counts[chat_id] >= DAILY_SHARE_LIMIT:
        bot.reply_to(message, f"Đã đạt giới hạn {DAILY_SHARE_LIMIT} lượt chia sẻ hàng ngày. Vui lòng thử lại sau.")
        return

    share_data[chat_id] = {}  # Khởi tạo dữ liệu cho người dùng
    # Tạo nút dừng
    markup = types.InlineKeyboardMarkup()
    stop_button = types.InlineKeyboardButton("Dừng Chia sẻ", callback_data="stop_share")
    markup.add(stop_button)
    bot.send_message(chat_id, "Vui lòng gửi file chứa cookie (cookies.txt).", reply_markup=markup)
    # Không đăng ký trình xử lý bước tiếp theo ở đây. Hàng đợi sẽ xử lý nó.


@bot.callback_query_handler(func=lambda call: call.data == "stop_share")
def stop_share_callback(call):
    chat_id = call.message.chat.id
    stop_sharing_flags[chat_id] = True  # Đặt cờ dừng
    bot.send_message(chat_id, "Đã nhận lệnh dừng chia sẻ. Vui lòng chờ quá trình hoàn tất.")

@bot.message_handler(commands=['reset'])
def reset_command(message):
    chat_id = message.chat.id
    try:
        # Đặt lại mạnh mẽ hơn: Xóa tất cả các cấu trúc dữ liệu liên quan
        if chat_id in share_data:
            del share_data[chat_id]
        if chat_id in stop_sharing_flags:
            stop_sharing_flags[chat_id] = False
        if chat_id in share_counts:
            share_counts[chat_id] = 0
        if chat_id in reset_times:
            reset_times[chat_id] = datetime.now().date()
        gome_token.clear()  # Xóa danh sách token toàn cục
        bot.reply_to(message, "Bot đã được khởi động lại.")
    except Exception as e:
        bot.reply_to(message, f"Có lỗi xảy ra khi đặt lại bot: {e}")


def process_cookie_file(message):
    chat_id = message.chat.id
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        file_content = downloaded_file.decode('utf-8').splitlines()
        share_data[chat_id]['cookie_file'] = file_content
        bot.send_message(chat_id, "Đã nhận file cookie. Vui lòng nhập ID bài viết cần chia sẻ.")
        # Không đăng ký bước tiếp theo. Hàng đợi sẽ xử lý.
    except Exception as e:
        bot.reply_to(message, f"Lỗi khi xử lý file: {e}")
        if chat_id in share_data:  # Kiểm tra xem có tồn tại trước khi xóa
            del share_data[chat_id]  # Xóa dữ liệu

def process_id(message):
    chat_id = message.chat.id
    id_share = message.text.strip()
    if not id_share.isdigit():
        bot.reply_to(message, "ID không hợp lệ. Vui lòng nhập lại ID bài viết cần chia sẻ.")
        return # Không tiếp tục nếu ID không hợp lệ

    share_data[chat_id]['id_share'] = id_share
    bot.send_message(chat_id, "Vui lòng nhập độ trễ giữa các lần chia sẻ (giây).")
    # Không đăng ký bước tiếp theo. Hàng đợi sẽ xử lý.


def process_delay(message):
    chat_id = message.chat.id
    delay_str = message.text.strip()
    try:
        delay = int(delay_str)
        if delay < 0:
              raise ValueError
    except ValueError:
        bot.reply_to(message, "Độ trễ không hợp lệ. Vui lòng nhập lại độ trễ (giây) là một số dương.")
        return  # Không tiếp tục nếu độ trễ không hợp lệ

    share_data[chat_id]['delay'] = delay
    bot.send_message(chat_id, "Vui lòng nhập tổng số lượng chia sẻ (0 để không giới hạn).")
    # Không đăng ký bước tiếp theo. Hàng đợi sẽ xử lý.

def process_total_shares(message):
    chat_id = message.chat.id
    total_share_limit_str = message.text.strip()
    try:
        total_share_limit = int(total_share_limit_str)
        if total_share_limit < 0:
            raise ValueError
    except ValueError:
        bot.reply_to(message, "Số lượng chia sẻ không hợp lệ. Vui lòng nhập lại tổng số lượng chia sẻ (0 để không giới hạn) là một số dương.")
        return # Không tiếp tục nếu đầu vào không hợp lệ

    share_data[chat_id]['total_share_limit'] = total_share_limit
    # Trước khi bắt đầu, tạo tin nhắn ban đầu
    markup = types.InlineKeyboardMarkup()
    stop_button = types.InlineKeyboardButton("Dừng Chia sẻ", callback_data="stop_share")
    markup.add(stop_button)
    bot.send_message(chat_id, "Bắt đầu chia sẻ...", reply_markup=markup) # Hiển thị nút 'Dừng' ở đây
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
        if chat_id in share_data: # Kiểm tra sự tồn tại trước khi xóa
            del share_data[chat_id]
        return

    bot.send_message(chat_id, f"Tìm thấy {total_live} token hợp lệ.")

    # Khởi tạo hoặc truy xuất số lượt chia sẻ và thời gian đặt lại cho cuộc trò chuyện này
    if chat_id not in share_counts:
        share_counts[chat_id] = 0
        reset_times[chat_id] = datetime.now().date()  # Ngày hôm nay
    else:
        # Kiểm tra xem có phải là một ngày mới không, đặt lại số lượt chia sẻ nếu cần
        if reset_times[chat_id] < datetime.now().date():
            share_counts[chat_id] = 0
            reset_times[chat_id] = datetime.now().date()

    stt = 0
    shared_count = 0
    successful_shares = 0 # Theo dõi số lượt chia sẻ thành công
    continue_sharing = True
    stop_sharing_flags[chat_id] = False  # Đặt lại cờ dừng khi bắt đầu
    while continue_sharing:
        for tach in all_tokens:
            if stop_sharing_flags.get(chat_id, False):
                continue_sharing = False
                break  # Thoát vòng lặp bên trong

            # Kiểm tra giới hạn hàng ngày *trước khi* cố gắng chia sẻ
            if share_counts[chat_id] >= DAILY_SHARE_LIMIT:
                bot.send_message(chat_id, f"Đã đạt giới hạn {DAILY_SHARE_LIMIT} lượt chia sẻ hàng ngày. Vui lòng thử lại sau.")
                continue_sharing = False
                break

            stt += 1
            success = share_thread_telegram(tach, id_share, chat_id)
            if success:
                successful_shares += 1
                share_counts[chat_id] += 1  # Tăng số lượng
            time.sleep(delay)
            shared_count += 1

            if total_share_limit > 0 and shared_count >= total_share_limit:
                continue_sharing = False
                break


    bot.send_message(chat_id, "Quá trình chia sẻ hoàn tất.")
    if total_share_limit > 0 and shared_count >= total_share_limit:
        bot.send_message(chat_id, f"Đạt giới hạn chia sẻ là {total_share_limit} lượt chia sẻ.")
    bot.send_message(chat_id, f"Tổng cộng {successful_shares} lượt chia sẻ thành công.") # Số lượng cuối cùng

    if chat_id in share_data: # Kiểm tra sự tồn tại trước khi xóa
        del share_data[chat_id]
    gome_token.clear()
    stop_sharing_flags[chat_id] = False  # Đặt lại

# --- Vòng lặp chính và xử lý hàng đợi ---
def process_queue():
    """Xử lý tin nhắn từ hàng đợi trong một luồng riêng biệt."""
    while True:
        message = message_queue.get()  # Lấy tin nhắn từ hàng đợi
        try:
            handle_message(message)  # Xử lý tin nhắn
        except Exception as e:
            bot.reply_to(message, f"Đã xảy ra lỗi: {e}")
        finally:
            message_queue.task_done() # Báo hiệu hoàn thành

# Bắt đầu luồng xử lý hàng đợi
queue_thread = threading.Thread(target=process_queue, daemon=True)
queue_thread.start()

@bot.message_handler(func=lambda message: True, content_types=['text', 'document'])
def enqueue_message(message):
    """Thêm tin nhắn đến vào hàng đợi."""
    message_queue.put(message)



if __name__ == "__main__":
    try:
        print("Bot đang chạy...")
        bot.infinity_polling()
    except KeyboardInterrupt:
        print("Bot đã dừng.")
        sys.exit()