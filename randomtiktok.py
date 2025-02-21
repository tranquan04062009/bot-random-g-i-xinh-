import telebot
import os
import random
import re
from requests_html import HTMLSession
import requests

# Nhập Bot Token của bạn
BOT_TOKEN = "7903504769:AAFPy0G459oCKCs0s1xM7yi60mSSLAx9VAU"

# Danh sách từ khóa tìm kiếm video
SEARCH_KEYWORDS = [
    "gái xinh", "hot girl", "pretty girl", "tiktok girl", "beauty girl", "cute girl"
]

# URL tìm kiếm trên TikTok (sử dụng query URL)
TIKTOK_SEARCH_URL = "https://www.tiktok.com/search?q={query}"

# Khởi tạo bot Telegram
bot = telebot.TeleBot(BOT_TOKEN)

def search_tiktok_video():
    """
    Tìm kiếm video TikTok bằng cách render trang kết quả tìm kiếm và trích xuất link video.
    """
    keyword = random.choice(SEARCH_KEYWORDS)
    query = keyword.replace(" ", "%20")
    search_url = TIKTOK_SEARCH_URL.format(query=query)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Referer": "https://www.tiktok.com/"
    }

    session = HTMLSession()
    try:
        response = session.get(search_url, headers=headers)
        # Render trang để thực thi JS (chú ý: quá trình này có thể mất vài giây)
        response.html.render(timeout=20, sleep=2)
        html_content = response.html.html

        # Dùng regex trích xuất các link video (playAddr)
        # Mẫu regex tìm chuỗi bắt đầu bằng "playAddr":"(https://...)" cho đến dấu ngoặc kép
        video_links = re.findall(r'"playAddr":"(https://[^"]+)"', html_content)
        if video_links:
            # Chọn ngẫu nhiên một link và thay thế ký tự escape "\u0026" thành "&"
            video_url = random.choice(video_links).replace("\\u0026", "&")
            return video_url
    except Exception as e:
        print("Lỗi khi tìm kiếm video:", e)
    return None

@bot.message_handler(commands=['randomvdgaixinh'])
def send_video(message):
    bot.reply_to(message, "🔎 Đang tìm video gái xinh TikTok...")
    video_url = search_tiktok_video()
    if video_url:
        video_path = "tiktok_video.mp4"
        try:
            # Tải video về máy chủ
            with requests.get(video_url, stream=True) as r:
                r.raise_for_status()
                with open(video_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            # Gửi video trực tiếp lên Telegram
            with open(video_path, "rb") as video_file:
                bot.send_video(
                    message.chat.id,
                    video_file,
                    caption="🎥 Video Gái Xinh TikTok",
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