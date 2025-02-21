import telebot
import requests
import random
import os
import re
from bs4 import BeautifulSoup

# Nhập Bot Token của bạn
BOT_TOKEN = "7903504769:AAFPy0G459oCKCs0s1xM7yi60mSSLAx9VAU"

# Danh sách từ khóa tìm kiếm video gái xinh
SEARCH_KEYWORDS = ["gái xinh", "hot girl", "pretty girl", "tiktok girl", "beauty girl", "cute girl"]

# URL tìm kiếm TikTok
TIKTOK_SEARCH_URL = "https://www.tiktok.com/search?q={query}"

# Khởi tạo bot Telegram
bot = telebot.TeleBot(BOT_TOKEN)

# Hàm tìm kiếm video TikTok trực tiếp
def search_tiktok_videos():
    keyword = random.choice(SEARCH_KEYWORDS).replace(" ", "%20")  # Chọn từ khóa ngẫu nhiên
    search_url = TIKTOK_SEARCH_URL.format(query=keyword)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }

    response = requests.get(search_url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        # Tìm tất cả các video có trong trang
        video_links = re.findall(r'"playAddr":"(https://.+?)"', response.text)

        if video_links:
            return random.choice(video_links).replace("\\u0026", "&")  # Chọn video ngẫu nhiên và sửa URL
    return None

# Xử lý lệnh /randomvdgaixinh
@bot.message_handler(commands=['randomvdgaixinh'])
def send_video(message):
    bot.reply_to(message, "🔎 Đang tìm video gái xinh TikTok...")

    video_url = search_tiktok_videos()
    if video_url:
        video_path = "tiktok_video.mp4"

        # Tải video về máy chủ
        try:
            with open(video_path, "wb") as f:
                f.write(requests.get(video_url).content)

            # Gửi video trực tiếp lên Telegram
            with open(video_path, "rb") as video_file:
                bot.send_video(
                    message.chat.id,
                    video_file,
                    caption="🎥 **Video Gái Xinh** 🎥",
                    parse_mode="Markdown"
                )
        except Exception as e:
            bot.reply_to(message, f"❌ Lỗi khi tải hoặc gửi video: {e}")
        finally:
            # Xóa file sau khi gửi để tiết kiệm dung lượng
            if os.path.exists(video_path):
                os.remove(video_path)
    else:
        bot.reply_to(message, "❌ Không tìm thấy video nào, thử lại sau!")

# Chạy bot
print("Bot đang chạy...")
bot.polling(none_stop=True)