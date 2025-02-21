import random
import requests
from telebot import TeleBot, types

# Token cố định
TOKEN_BOT = "7903504769:AAFPy0G459oCKCs0s1xM7yi60mSSLAx9VAU"

bot = TeleBot(TOKEN_BOT, parse_mode="Markdown", disable_web_page_preview=True, num_threads=5)

# Tạo bàn phím chứa nút liên hệ
def lien_he_admin():
    key = types.InlineKeyboardMarkup(row_width=1)
    admin = types.InlineKeyboardButton("⦗ Liên hệ Admin ⦘", url="tg://user?id=6940071938")
    key.add(admin)
    return key

# Xử lý lệnh /start
@bot.message_handler(commands=["start"])
def bat_dau(message):
    chat_id = message.chat.id
    bot.send_photo(
        chat_id,
        photo="https://t.me/zizfif",
        caption='''*- Chào mừng bạn đến với Bot 🤖.
- Bot hỗ trợ tạo tài khoản Facebook Fake.
- Gửi lệnh /tao và chờ đợi...*''',
        reply_markup=lien_he_admin(),
        reply_to_message_id=message.message_id
    )

# Xử lý lệnh /tao
@bot.message_handler(commands=['tao', 'Tao'])
def tao_tai_khoan(message):
    danh_sach_mxh = ['hotmail.com', 'gmail.com', 'yahoo.com', 'aol.com', 'msn.com', 'outlook.com']
    chu_cai = 'abcdefghijklmnopqrstuvwxyz'
    email = ''.join(random.choice(chu_cai) for i in range(10)) + '@' + random.choice(danh_sach_mxh)
    mat_khau = "112233sada"

    url = 'https://web.facebook.com/ajax/register.php'
    headers = {
        "Accept": "*/*", 
        "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://web.facebook.com",
        "Referer": "https://web.facebook.com/r.php",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, như Gecko) Chrome/120.0.0.0 Safari/537.36",
    }
    du_lieu = {
        'jazoest': '2945',
        'lsd': 'AVrQPVBRqt8',
        'firstname': 'Nguyen',
        'lastname': 'Van A',
        'reg_email__': email,
        'reg_email_confirmation__': email,
        'reg_passwd__': mat_khau,
        'birthday_day': '20',
        'birthday_month': '6',
        'birthday_year': '2003',
        'sex': '2',
        'terms': 'on',
        '__user': '0',
        '__a': '1',
        '__req': 'h',
        '__hs': '19894.BP:DEFAULT.2.0..0.0',
        '__spin_r': '1014348293',
        '__spin_b': 'trunk',
        '__spin_t': '1718889560',
    }

    phan_hoi = requests.post(url, headers=headers, data=du_lieu).text

    if 'registration_succeeded":true' in phan_hoi:
        print("\n- Đã tạo tài khoản và gửi tới bot...")
        chat_id = message.chat.id
        bot.send_photo(
            chat_id,
            photo="https://t.me/zizfif",
            caption=f'''*[ ✅ Tạo tài khoản Facebook thành công! ]*
━━━━━━━━━━━━━━━
👤 *Tên đăng nhập:* `{email}`
🔑 *Mật khẩu:* `{mat_khau}`
📅 *Ngày sinh:* `{du_lieu["birthday_day"]}/{du_lieu["birthday_month"]}/{du_lieu["birthday_year"]}`
━━━━━━━━━━━━━━━
💡 *Liên hệ hỗ trợ:* 0376841471
''',
            reply_markup=lien_he_admin(),
            reply_to_message_id=message.message_id
        )
    else:
        print("Lỗi khi tạo tài khoản")
        bot.send_message(message.chat.id, "❌ Lỗi khi tạo tài khoản Facebook Fake!")

# Chạy bot
bot.infinity_polling()