import os
import random
import requests
import telebot
from TikTokApi import TikTokApi

# Nhập Bot Token của bạn
BOT_TOKEN = "7903504769:AAFPy0G459oCKCs0s1xM7yi60mSSLAx9VAU"

# Khởi tạo bot
bot = telebot.TeleBot(BOT_TOKEN)

# Khởi tạo TikTok API
api = TikTokApi()

# Danh sách hashtag ngẫu nhiên để lấy video gái xinh
hashtag_list = ["gaixinh", "hotgirl", "vitamingirl", "gái xinh", "sexy"]

def get_random_video():
    """Lấy một video TikTok ngẫu nhiên từ hashtag"""
    hashtag = random.choice(hashtag_list)
    results = api.search_for_hashtags(hashtag, count=10)  # Lấy 10 video

    if not results:
        return None

    video = random.choice(results)  # Chọn ngẫu nhiên 1 video
    video_data = {
        "id": video["id"],
        "desc": video["desc"],
        "video_url": video["video"]["downloadAddr"],
        "author": video["author"]["uniqueId"],
        "author_name": video["author"]["nickname"],
        "like_count": video["stats"]["diggCount"],
        "comment_count": video["stats"]["commentCount"],
        "share_count": video["stats"]["shareCount"]
    }
    return video_data

def download_video(url, filename):
    """Tải video TikTok về máy"""
    response = requests.get(url, stream=True)
    with open(filename, "wb") as file:
        for chunk in response.iter_content(chunk_size=1024):
            file.write(chunk)
    return filename

@bot.message_handler(commands=["randomgaixinh"])
def send_random_tiktok(message):
    """Gửi video TikTok ngẫu nhiên khi người dùng gõ lệnh /randomgaixinh"""
    video = get_random_video()
    if not video:
        bot.reply_to(message, "Không tìm thấy video nào, thử lại sau!")
        return

    filename = f"{video['id']}.mp4"
    download_video(video["video_url"], filename)

    caption = f"🔥 <b>Video Gái Xinh</b>\n\n" \
              f"🎥 <b>Mô tả:</b> {video['desc']}\n" \
              f"👤 <b>Người đăng:</b> @{video['author']} ({video['author_name']})\n" \
              f"❤️ <b>Likes:</b> {video['like_count']}\n" \
              f"💬 <b>Bình luận:</b> {video['comment_count']}\n" \
              f"🔄 <b>Chia sẻ:</b> {video['share_count']}\n" \
              f"🔗 <b>Link:</b> https://www.tiktok.com/@{video['author']}/video/{video['id']}"

    with open(filename, "rb") as video_file:
        bot.send_video(message.chat.id, video_file, caption=caption, parse_mode="HTML")

    os.remove(filename)  # Xóa video sau khi gửi

# Chạy bot
bot.polling()