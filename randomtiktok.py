import telebot
import requests
import random
import os

# Nhập Bot Token của bạn
BOT_TOKEN = "7903504769:AAFPy0G459oCKCs0s1xM7yi60mSSLAx9VAU"

# API tải video TikTok
TIKTOK_API = "https://www.tikwm.com/api/feed/search"

# Danh sách từ khóa tìm kiếm video gái xinh
SEARCH_KEYWORDS = ["gái xinh", "hot girl", "pretty girl", "tiktok girl"]

# Khởi tạo bot Telegram
bot = telebot.TeleBot(BOT_TOKEN)

# Hàm lấy 1 video duy nhất từ TikTok
def get_tiktok_video():
    try:
        keyword = random.choice(SEARCH_KEYWORDS)  # Chọn từ khóa ngẫu nhiên
        params = {"keyword": keyword, "count": 5}  # Lấy tối đa 5 video
        response = requests.get(TIKTOK_API, params=params)
        data = response.json()

        if "data" in data and data["data"]:
            video = data["data"][0]  # Chỉ lấy video đầu tiên
            return {
                "video_url": video["play"],  # Link tải video
                "author": video["author"]["nickname"],
                "video_id": video["video_id"]
            }
    except Exception as e:
        print(f"Lỗi khi lấy video: {e}")
    
    return None

# Xử lý lệnh /randomvdgaixinh
@bot.message_handler(commands=['randomvdgaixinh'])
def send_video(message):
    bot.reply_to(message, "🔎 Đang tìm video gái xinh TikTok...")

    video = get_tiktok_video()
    if video:
        video_url = video["video_url"]
        video_path = f"tiktok_{video['video_id']}.mp4"

        # Tải video về máy chủ
        try:
            with open(video_path, "wb") as f:
                f.write(requests.get(video_url).content)

            # Gửi video trực tiếp lên Telegram
            with open(video_path, "rb") as video_file:
                bot.send_video(
                    message.chat.id,
                    video_file,
                    caption=(
                        f"🎥 **Video Gái Xinh** 🎥\n"
                        f"- **Chủ Video:** {video['author']}\n"
                        f"- **ID Video:** {video['video_id']}"
                    ),
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
