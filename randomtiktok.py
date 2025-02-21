import telebot
import requests
import random
import os

# Nhập Bot Token của bạn
BOT_TOKEN = "7903504769:AAFPy0G459oCKCs0s1xM7yi60mSSLAx9VAU"

# Danh sách từ khóa tìm kiếm video
SEARCH_KEYWORDS = [
    "gái xinh", "hot girl", "pretty girl", "tiktok girl", "beauty girl", "cute girl"
]

# URL API tìm kiếm video TikTok
TIKTOK_SEARCH_API = "https://www.tiktok.com/api/search/general/?keyword={query}&count=10"

# Khởi tạo bot Telegram
bot = telebot.TeleBot(BOT_TOKEN)

def get_tiktok_video():
    """
    Tìm kiếm video TikTok bằng API chính thức của TikTok.
    """
    keyword = random.choice(SEARCH_KEYWORDS)
    search_url = TIKTOK_SEARCH_API.format(query=keyword.replace(" ", "%20"))

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Referer": "https://www.tiktok.com/"
    }

    try:
        response = requests.get(search_url, headers=headers).json()
        videos = response.get("data", {}).get("videos", [])
        
        if videos:
            video_data = random.choice(videos)  # Chọn video ngẫu nhiên
            video_url = video_data["play_addr"]
            video_author = video_data["author"]["nickname"]
            video_title = video_data["desc"]

            return video_url, video_author, video_title
    except Exception as e:
        print("Lỗi khi lấy video từ API TikTok:", e)
    
    return None, None, None

@bot.message_handler(commands=['randomvdgaixinh'])
def send_video(message):
    bot.reply_to(message, "🔎 Đang tìm video gái xinh TikTok...")

    video_url, author, title = get_tiktok_video()
    if video_url:
        video_path = "tiktok_video.mp4"
        try:
            # Tải video về máy chủ
            with open(video_path, "wb") as f:
                f.write(requests.get(video_url).content)

            # Gửi video trực tiếp lên Telegram
            with open(video_path, "rb") as video_file:
                bot.send_video(
                    message.chat.id,
                    video_file,
                    caption=f"🎥 **Video Gái Xinh TikTok** 🎥\n\n📌 **Tác giả**: {author}\n📝 **Tiêu đề**: {title}",
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