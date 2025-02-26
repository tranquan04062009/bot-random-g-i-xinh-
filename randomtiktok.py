import asyncio
import aiohttp
import aiosqlite
from telebot.async_telebot import AsyncTeleBot
from telebot import types
from faker import Faker
import random
import time
from datetime import datetime, timedelta, timezone
from fake_useragent import UserAgent

# Hardcode BOT_TOKEN (không khuyến nghị trong thực tế vì lý do bảo mật)
BOT_TOKEN = "7903504769:AAFeKxomzBB-QtDzwOXojBofz9vju2CsDKc"  # Thay thế bằng token thật của bạn

# Khởi tạo bot Telegram bất đồng bộ và Faker
bot = AsyncTeleBot(BOT_TOKEN)
fake = Faker('vi_VN')  # Phiên bản tiếng Việt
ua = UserAgent()  # Tạo user agent ngẫu nhiên

# Thiết lập múi giờ Việt Nam (GMT+7)
VN_TIMEZONE = timezone(timedelta(hours=7))

# Hằng số
GIOI_HAN_CHIA_SE_HANG_NGAY = 5000  # Giới hạn 5000 lượt chia sẻ mỗi ngày
GIOI_HAN_CHIA_SE_GIO = 100  # Giới hạn 100 lượt mỗi giờ để bắt chước con người
NGUONG_THAP = 1000  # Ngưỡng thấp để cảnh báo người dùng

# Danh sách user agents mở rộng (tự động tạo bằng UserAgent)
def lay_danh_sach_user_agents():
    return [ua.random for _ in range(200)]  # Tạo 200 user agent ngẫu nhiên

user_agents = lay_danh_sach_user_agents()

# Thiết lập cơ sở dữ liệu SQLite bất đồng bộ
async def khoi_tao_co_so_du_lieu():
    async with aiosqlite.connect('bot_chia_se_an_danh.db') as conn:
        await conn.execute('''CREATE TABLE IF NOT EXISTS nguoi_dung 
                            (ma_nguoi_dung INTEGER, so_luot_chia_se INTEGER, ngay_dat_lai TEXT, du_lieu TEXT, thoi_gian_cuoi_chia_se TEXT)''')
        await conn.commit()

# Hàm lấy header ngẫu nhiên với dấu vân tay cao
def lay_header_ngau_nhien():
    headers = {
        'authority': 'business.facebook.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': random.choice(['vi-VN', 'en-US', 'fr-FR']),
        'cache-control': 'max-age=0',
        'referer': f'https://www.facebook.com/{random.randint(1000000, 9999999)}',  # URL ngẫu nhiên
        'sec-ch-ua': f'"{fake.chrome(version_from=80, version_to=120)}";v="{random.randint(80, 120)}", "Not/A)Brand";v="99"',
        'sec-ch-ua-mobile': '?0' if random.random() > 0.5 else '?1',
        'sec-ch-ua-platform': f'"{random.choice(["Windows", "Linux", "macOS", "Android", "iOS"])}"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': random.choice(user_agents),
        'x-forwarded-for': f'{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}',  # IP giả lập
    }
    return headers

# Hàm giả lập hành vi con người trước khi chia sẻ với retry
async def gia_lap_hanh_vi_con_nguoi(cookie, id_chia_se, max_retries=3):
    for attempt in range(max_retries):
        headers = lay_header_ngau_nhien()
        headers['cookie'] = cookie
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f'https://m.facebook.com/{id_chia_se}', headers=headers, timeout=10) as response:
                    if response.status == 200:
                        await asyncio.sleep(random.uniform(1, 3))  # Chờ giống con người
                        return True
            except Exception as e:
                print(f"[!] Lỗi giả lập hành vi (lần {attempt + 1}): {e}")
                await asyncio.sleep(2 ** attempt)  # Backoff ngẫu nhiên
    return False

# Hàm lấy token hợp lệ (bất đồng bộ với retry)
async def lay_token(input_file, max_retries=3):
    valid_tokens = []
    async with aiohttp.ClientSession() as session:
        for cookie in input_file:
            cookie = cookie.strip()
            if not cookie:
                continue

            for attempt in range(max_retries):
                headers = lay_header_ngau_nhien()
                headers['cookie'] = cookie

                try:
                    async with session.get('https://business.facebook.com/content_management', headers=headers, timeout=15) as response:
                        if response.status == 200:
                            home_business = await response.text()
                            if 'EAAG' in home_business:
                                token = home_business.split('EAAG')[1].split('","')[0]
                                cookie_token = f'{cookie}|EAAG{token}'
                                valid_tokens.append(cookie_token)
                                break
                            else:
                                print(f"[!] Không thể lấy token từ cookie: {cookie[:50]}... Cookie có thể không hợp lệ.")
                except Exception as e:
                    print(f"[!] Lỗi khi lấy token cho cookie: {cookie[:50]}... Lỗi (lần {attempt + 1}): {e}")
                    await asyncio.sleep(2 ** attempt)  # Backoff ngẫu nhiên
    return valid_tokens

# Hàm chia sẻ bài viết bất đồng bộ với hành vi ẩn danh và retry
async def chia_se(cookie, token, id_chia_se, max_retries=3):
    # Giả lập hành vi con người với retry
    if not await gia_lap_hanh_vi_con_nguoi(cookie, id_chia_se, max_retries):
        print(f"[!] Không thể giả lập hành vi con người cho ID: {id_chia_se}")
        return False

    for attempt in range(max_retries):
        headers = lay_header_ngau_nhien()
        headers.update({
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate',
            'connection': 'keep-alive',
            'content-length': '0',
            'cookie': cookie,
            'host': 'graph.facebook.com',
            'referer': f'https://m.facebook.com/{id_chia_se}'
        })

        async with aiohttp.ClientSession() as session:
            try:
                await asyncio.sleep(random.uniform(1, 5))  # Độ trễ ngẫu nhiên để tránh phát hiện
                async with session.post(f'https://graph.facebook.com/me/feed?link=https://m.facebook.com/{id_chia_se}&published=0&access_token={token}', 
                                      headers=headers, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        return 'id' in data
                    elif response.status == 429:  # Too Many Requests
                        print(f"[!] Phát hiện giới hạn tốc độ cho ID: {id_chia_se} (lần {attempt + 1})")
                        await asyncio.sleep(2 ** attempt)  # Backoff ngẫu nhiên
                    else:
                        print(f"[!] Lỗi HTTP {response.status} khi chia sẻ ID: {id_chia_se}")
                        return False
            except Exception as e:
                print(f"[!] Lỗi khi chia sẻ: ID: {id_chia_se} - {e}")
                await asyncio.sleep(2 ** attempt)  # Backoff ngẫu nhiên
    return False

# Kiểm tra giới hạn giờ để tránh bị phát hiện
def kiem_tra_gioi_han_gio(ma_nguoi_dung):
    with sqlite3.connect('bot_chia_se_an_danh.db') as conn:
        c = conn.cursor()
        c.execute("SELECT so_luot_chia_se, thoi_gian_cuoi_chia_se FROM nguoi_dung WHERE ma_nguoi_dung = ?", (ma_nguoi_dung,))
        result = c.fetchone()
        if result:
            so_luot, thoi_gian_cuoi = result
            if thoi_gian_cuoi:
                thoi_gian_cuoi = datetime.fromisoformat(thoi_gian_cuoi)
                if (datetime.now(VN_TIMEZONE) - thoi_gian_cuoi).total_seconds() < 3600:  # 1 giờ
                    return so_luot >= GIOI_HAN_CHIA_SE_GIO
    return False

# Bắt đầu quá trình chia sẻ với tốc độ cao và ẩn danh
async def bat_dau_chia_se(ma_nguoi_dung):
    chat_id = ma_nguoi_dung  # Giả sử chat_id = user_id trong group chat
    du_lieu = await lay_du_lieu_nguoi_dung(ma_nguoi_dung)
    if not du_lieu:
        await bot.send_message(chat_id, "Dữ liệu không đầy đủ. Vui lòng bắt đầu lại với /chia_se.")
        return

    input_file = du_lieu['cookie_file']
    id_chia_se = du_lieu['id_chia_se']
    do_tre = du_lieu['do_tre']
    gioi_han_tong_luot = du_lieu['gioi_han_tong_luot']

    all_tokens = await lay_token(input_file)
    if not all_tokens:
        await bot.send_message(chat_id, "Không tìm thấy token hợp lệ nào.")
        await dat_lai_du_lieu_nguoi_dung(ma_nguoi_dung)
        return

    await bot.send_message(chat_id, f"Tìm thấy {len(all_tokens)} token hợp lệ.")

    # Kiểm tra và đặt lại giới hạn
    if await kiem_tra_gioi_han_hang_ngay(ma_nguoi_dung):
        await dat_lai_du_lieu_nguoi_dung(ma_nguoi_dung)
    if kiem_tra_gioi_han_gio(ma_nguoi_dung):
        await bot.send_message(chat_id, "Đã đạt giới hạn chia sẻ trong giờ. Vui lòng chờ 1 giờ trước khi tiếp tục.")
        return

    stt = 0
    so_luot_thanh_cong = 0
    tiep_tuc_chia_se = True
    while tiep_tuc_chia_se:
        tasks = []
        for tach in all_tokens:
            if lay_dung_chia_se(ma_nguoi_dung):
                tiep_tuc_chia_se = False
                break

            if lay_so_luot_chia_se(ma_nguoi_dung) >= GIOI_HAN_CHIA_SE_HANG_NGAY:
                await bot.send_message(chat_id, f"Bạn đã đạt đến giới hạn chia sẻ hàng ngày là {GIOI_HAN_CHIA_SE_HANG_NGAY}. Vui lòng thử lại vào ngày mai.")
                tiep_tuc_chia_se = False
                break

            tasks.append(chia_se(tach.split('|')[0], tach.split('|')[1], id_chia_se))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        for success in results:
            if success:
                so_luot_thanh_cong += 1
                await cap_nhat_so_luot_chia_se(ma_nguoi_dung)
                await cap_nhat_thoi_gian_chia_se(ma_nguoi_dung)

        if gioi_han_tong_luot > 0 and so_luot_thanh_cong >= gioi_han_tong_luot:
            tiep_tuc_chia_se = False
            break

        # Ngẫu nhiên hóa độ trễ giữa các chu kỳ để tránh phát hiện và giữ tốc độ cao
        await asyncio.sleep(random.uniform(max(0, do_tre - 2), do_tre + 2))

    await bot.send_message(chat_id, "Quá trình chia sẻ đã hoàn tất.")
    if gioi_han_tong_luot > 0 and so_luot_thanh_cong >= gioi_han_tong_luot:
        await bot.send_message(chat_id, f"Đã đạt đến giới hạn chia sẻ là {gioi_han_tong_luot} lượt.")
    await bot.send_message(chat_id, f"Tổng số lượt chia sẻ thành công: {so_luot_thanh_cong}.")
    await dat_lai_du_lieu_nguoi_dung(ma_nguoi_dung)

# Các hàm xử lý cơ sở dữ liệu (bất đồng bộ)
async def lay_du_lieu_nguoi_dung(ma_nguoi_dung):
    async with aiosqlite.connect('bot_chia_se_an_danh.db') as conn:
        async with await conn.execute("SELECT du_lieu FROM nguoi_dung WHERE ma_nguoi_dung = ?", (ma_nguoi_dung,)) as cursor:
            result = await cursor.fetchone()
            return json.loads(result[0]) if result else None

async def cap_nhat_so_luot_chia_se(ma_nguoi_dung):
    async with aiosqlite.connect('bot_chia_se_an_danh.db') as conn:
        await conn.execute("UPDATE nguoi_dung SET so_luot_chia_se = so_luot_chia_se + 1 WHERE ma_nguoi_dung = ?", (ma_nguoi_dung,))
        await conn.commit()

async def cap_nhat_thoi_gian_chia_se(ma_nguoi_dung):
    async with aiosqlite.connect('bot_chia_se_an_danh.db') as conn:
        await conn.execute("UPDATE nguoi_dung SET thoi_gian_cuoi_chia_se = ? WHERE ma_nguoi_dung = ?", 
                          (datetime.now(VN_TIMEZONE).isoformat(), ma_nguoi_dung))
        await conn.commit()

async def dat_lai_du_lieu_nguoi_dung(ma_nguoi_dung):
    async with aiosqlite.connect('bot_chia_se_an_danh.db') as conn:
        await conn.execute("UPDATE nguoi_dung SET so_luot_chia_se = 0, ngay_dat_lai = ?, du_lieu = ?, thoi_gian_cuoi_chia_se = NULL WHERE ma_nguoi_dung = ?", 
                          (datetime.now(VN_TIMEZONE).date(), json.dumps({}), ma_nguoi_dung))
        await conn.commit()

# Kiểm tra giới hạn hàng ngày (bất đồng bộ)
async def kiem_tra_gioi_han_hang_ngay(ma_nguoi_dung):
    async with aiosqlite.connect('bot_chia_se_an_danh.db') as conn:
        async with await conn.execute("SELECT so_luot_chia_se, ngay_dat_lai FROM nguoi_dung WHERE ma_nguoi_dung = ?", (ma_nguoi_dung,)) as cursor:
            result = await cursor.fetchone()
            if result:
                so_luot, ngay_dat_lai = result
                ngay_hien_tai = datetime.now(VN_TIMEZONE).date()
                return so_luot >= GIOI_HAN_CHIA_SE_HANG_NGAY and ngay_dat_lai == ngay_hien_tai
            return False

# Xử lý lệnh /chia_se chỉ trong nhóm
@bot.message_handler(commands=['chia_se'], chat_types=['group', 'supergroup'])
async def chia_se_lenh(message):
    ma_nguoi_dung = message.from_user.id
    if message.chat.type not in ['group', 'supergroup']:
        await bot.reply_to(message, "Lệnh /chia_se chỉ hoạt động trong các nhóm. Vui lòng sử dụng trong nhóm Telegram.")
        return

    so_luot_hien_tai = await lay_so_luot_chia_se(ma_nguoi_dung)
    if so_luot_hien_tai >= GIOI_HAN_CHIA_SE_HANG_NGAY:
        await bot.reply_to(message, f"Bạn đã đạt đến giới hạn chia sẻ hàng ngày là {GIOI_HAN_CHIA_SE_HANG_NGAY}. Vui lòng thử lại vào ngày mai.")
        return

    du_lieu = await lay_du_lieu_nguoi_dung(ma_nguoi_dung) or {}
    du_lieu.clear()
    await cap_nhat_du_lieu_nguoi_dung(ma_nguoi_dung, du_lieu)

    markup = types.InlineKeyboardMarkup()
    nut_dung = types.InlineKeyboardButton("Dừng Chia Sẻ", callback_data="dung_chia_se")
    markup.add(nut_dung)
    await bot.send_message(message.chat.id, "Vui lòng gửi file cookie (cookies.txt).", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "dung_chia_se")
async def dung_chia_se_callback(call):
    ma_nguoi_dung = call.from_user.id
    dat_dung_chia_se(ma_nguoi_dung, True)
    await bot.send_message(call.message.chat.id, "Đã dừng chia sẻ. Vui lòng đợi quá trình hiện tại kết thúc.")

# Xử lý file cookie chỉ trong nhóm
@bot.message_handler(content_types=['document'], chat_types=['group', 'supergroup'])
async def xu_ly_tai_lieu(message):
    ma_nguoi_dung = message.from_user.id
    du_lieu = await lay_du_lieu_nguoi_dung(ma_nguoi_dung)
    if not du_lieu or 'cookie_file' not in du_lieu:
        try:
            file_info = await bot.get_file(message.document.file_id)
            downloaded_file = await bot.download_file(file_info.file_path)
            cookie_file = downloaded_file.decode('utf-8').splitlines()
            du_lieu['cookie_file'] = cookie_file
            await cap_nhat_du_lieu_nguoi_dung(ma_nguoi_dung, du_lieu)
            await bot.send_message(message.chat.id, "Đã nhận file cookie. Vui lòng nhập ID bài viết cần chia sẻ.")
        except Exception as e:
            await bot.reply_to(message, f"Lỗi khi xử lý file: {e}")
            await dat_lai_du_lieu_nguoi_dung(ma_nguoi_dung)

# Hàm chính (bất đồng bộ, tối ưu hóa tốc độ)
async def main():
    await khoi_tao_co_so_du_lieu()
    await bot.polling(non_stop=True, timeout=10)  # Tăng timeout để giảm lỗi kết nối

if __name__ == "__main__":
    asyncio.run(main())

# Hàm phụ trợ (giữ nguyên logic nhưng thêm vào đây để hoàn chỉnh)
async def lay_so_luot_chia_se(ma_nguoi_dung):
    async with aiosqlite.connect('bot_chia_se_an_danh.db') as conn:
        async with await conn.execute("SELECT so_luot_chia_se FROM nguoi_dung WHERE ma_nguoi_dung = ?", (ma_nguoi_dung,)) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0

async def cap_nhat_du_lieu_nguoi_dung(ma_nguoi_dung, du_lieu):
    async with aiosqlite.connect('bot_chia_se_an_danh.db') as conn:
        await conn.execute("INSERT OR REPLACE INTO nguoi_dung (ma_nguoi_dung, so_luot_chia_se, ngay_dat_lai, du_lieu, thoi_gian_cuoi_chia_se) VALUES (?, 0, ?, ?, NULL)", 
                          (ma_nguoi_dung, datetime.now(VN_TIMEZONE).date(), json.dumps(du_lieu)))
        await conn.commit()

def lay_dung_chia_se(ma_nguoi_dung):
    # Logic giả định (cần triển khai dựa trên dữ liệu cụ thể)
    return False  # Placeholder, cần thay bằng logic thực tế

def dat_dung_chia_se(ma_nguoi_dung, gia_tri):
    # Logic giả định (cần triển khai dựa trên dữ liệu cụ thể)
    pass  # Placeholder, cần thay bằng logic thực tế