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
import json
import logging
from typing import List, Dict, Optional

# Cấu hình logging để theo dõi
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
MAX_RETRIES = 5  # Số lần thử lại tối đa cho các yêu cầu
INITIAL_BACKOFF = 1  # Thời gian backoff ban đầu (giây)

# Danh sách user agents mở rộng với kiểm soát chất lượng
def lay_danh_sach_user_agents() -> List[str]:
    return [ua.random for _ in range(300)]  # Tạo 300 user agent ngẫu nhiên với độ đa dạng cao

user_agents = lay_danh_sach_user_agents()

# Quản lý trạng thái dừng chia sẻ cho từng người dùng
stop_sharing_flags: Dict[int, bool] = {}

# Thiết lập cơ sở dữ liệu SQLite bất đồng bộ
async def khoi_tao_co_so_du_lieu() -> None:
    async with aiosqlite.connect('bot_chia_se_an_danh.db') as conn:
        await conn.execute('''CREATE TABLE IF NOT EXISTS nguoi_dung 
                            (ma_nguoi_dung INTEGER PRIMARY KEY, so_luot_chia_se INTEGER DEFAULT 0, 
                             ngay_dat_lai TEXT, du_lieu TEXT, thoi_gian_cuoi_chia_se TEXT)''')
        await conn.commit()
    logger.info("Cơ sở dữ liệu đã được khởi tạo hoặc kiểm tra.")

# Hàm lấy header ngẫu nhiên với dấu vân tay nâng cao
def lay_header_ngau_nhien() -> Dict[str, str]:
    headers = {
        'authority': 'business.facebook.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': random.choice(['vi-VN', 'en-US', 'fr-FR', 'ja-JP']),
        'cache-control': 'max-age=0',
        'referer': f'https://www.facebook.com/{random.randint(1000000, 9999999)}',  # URL ngẫu nhiên
        'sec-ch-ua': f'"{fake.chrome(version_from=90, version_to=130)}";v="{random.randint(90, 130)}", "Not/A)Brand";v="99", "Chromium";v="130"',
        'sec-ch-ua-mobile': '?0' if random.random() > 0.5 else '?1',
        'sec-ch-ua-platform': f'"{random.choice(["Windows", "Linux", "macOS", "Android", "iOS"])}"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': random.choice(user_agents),
        'x-forwarded-for': f'{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}',  # IP giả lập
        'dnt': str(random.randint(0, 1)),  # Do Not Track ngẫu nhiên
    }
    return headers

# Hàm giả lập hành vi con người trước khi chia sẻ với retry nâng cao
async def gia_lap_hanh_vi_con_nguoi(cookie: str, id_chia_se: str) -> bool:
    for attempt in range(MAX_RETRIES):
        headers = lay_header_ngau_nhien()
        headers['cookie'] = cookie
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f'https://m.facebook.com/{id_chia_se}', headers=headers, timeout=15) as response:
                    if response.status == 200:
                        # Giả lập cuộn trang và tương tác ngẫu nhiên
                        await asyncio.sleep(random.uniform(1.5, 4.0))  # Chờ giống con người
                        # Thêm truy vấn ngẫu nhiên để tăng dấu vết
                        await session.get(f'https://m.facebook.com/{id_chia_se}/?sk=feed', headers=headers, timeout=10)
                        return True
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                logger.warning(f"[!] Lỗi giả lập hành vi (lần {attempt + 1}) cho ID {id_chia_se}: {e}")
                await asyncio.sleep(INITIAL_BACKOFF * (2 ** attempt) * random.uniform(0.9, 1.1))  # Backoff ngẫu nhiên
    logger.error(f"[!] Không thể giả lập hành vi con người cho ID: {id_chia_se} sau {MAX_RETRIES} lần thử.")
    return False

# Hàm lấy token hợp lệ (bất đồng bộ với retry nâng cao)
async def lay_token(input_file: List[str]) -> List[str]:
    valid_tokens = []
    async with aiohttp.ClientSession() as session:
        for cookie in input_file:
            cookie = cookie.strip()
            if not cookie:
                continue

            for attempt in range(MAX_RETRIES):
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
                                logger.warning(f"[!] Không thể lấy token từ cookie: {cookie[:50]}... Cookie có thể không hợp lệ.")
                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    logger.warning(f"[!] Lỗi khi lấy token cho cookie: {cookie[:50]}... Lỗi (lần {attempt + 1}): {e}")
                    await asyncio.sleep(INITIAL_BACKOFF * (2 ** attempt) * random.uniform(0.9, 1.1))  # Backoff ngẫu nhiên
    return valid_tokens

# Hàm chia sẻ bài viết bất đồng bộ với hành vi ẩn danh và retry nâng cao
async def chia_se(cookie: str, token: str, id_chia_se: str) -> bool:
    if not await gia_lap_hanh_vi_con_nguoi(cookie, id_chia_se):
        logger.error(f"[!] Không thể giả lập hành vi con người cho ID: {id_chia_se}")
        return False

    for attempt in range(MAX_RETRIES):
        headers = lay_header_ngau_nhien()
        headers.update({
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'connection': 'keep-alive',
            'content-length': '0',
            'cookie': cookie,
            'host': 'graph.facebook.com',
            'referer': f'https://m.facebook.com/{id_chia_se}',
            'origin': 'https://m.facebook.com',
        })

        async with aiohttp.ClientSession() as session:
            try:
                # Ngẫu nhiên hóa thời gian để tránh phát hiện
                await asyncio.sleep(random.uniform(1.0, 5.0))
                async with session.post(f'https://graph.facebook.com/me/feed?link=https://m.facebook.com/{id_chia_se}&published=0&access_token={token}', 
                                      headers=headers, timeout=15) as response:
                    if response.status == 200:
                        data = await response.json()
                        if 'id' in data:
                            logger.info(f"[✓] Chia sẻ thành công cho ID: {id_chia_se}")
                            return True
                        logger.warning(f"[!] Phản hồi không mong muốn cho ID: {id_chia_se} - {data}")
                        return False
                    elif response.status == 429:  # Too Many Requests
                        logger.warning(f"[!] Phát hiện giới hạn tốc độ cho ID: {id_chia_se} (lần {attempt + 1})")
                        await asyncio.sleep(INITIAL_BACKOFF * (2 ** attempt) * random.uniform(0.9, 1.1))  # Backoff ngẫu nhiên
                    elif response.status in [403, 404, 500]:  # Lỗi khác
                        logger.error(f"[!] Lỗi HTTP {response.status} khi chia sẻ ID: {id_chia_se}")
                        return False
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                logger.error(f"[!] Lỗi khi chia sẻ: ID: {id_chia_se} - {e}")
                await asyncio.sleep(INITIAL_BACKOFF * (2 ** attempt) * random.uniform(0.9, 1.1))  # Backoff ngẫu nhiên
    logger.error(f"[!] Không thể chia sẻ ID: {id_chia_se} sau {MAX_RETRIES} lần thử.")
    return False

# Kiểm tra giới hạn giờ để tránh bị phát hiện
async def kiem_tra_gioi_han_gio(ma_nguoi_dung: int) -> bool:
    async with aiosqlite.connect('bot_chia_se_an_danh.db') as conn:
        async with await conn.execute("SELECT so_luot_chia_se, thoi_gian_cuoi_chia_se FROM nguoi_dung WHERE ma_nguoi_dung = ?", (ma_nguoi_dung,)) as cursor:
            result = await cursor.fetchone()
            if result:
                so_luot, thoi_gian_cuoi = result
                if thoi_gian_cuoi:
                    thoi_gian_cuoi = datetime.fromisoformat(thoi_gian_cuoi)
                    if (datetime.now(VN_TIMEZONE) - thoi_gian_cuoi).total_seconds() < 3600:  # 1 giờ
                        return so_luot >= GIOI_HAN_CHIA_SE_GIO
    return False

# Bắt đầu quá trình chia sẻ với tốc độ cao, ẩn danh, và theo dõi chi tiết
async def bat_dau_chia_se(ma_nguoi_dung: int, chat_id: int) -> None:
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
    if await kiem_tra_gioi_han_gio(ma_nguoi_dung):
        await bot.send_message(chat_id, "Đã đạt giới hạn chia sẻ trong giờ. Vui lòng chờ 1 giờ trước khi tiếp tục.")
        return

    stop_sharing_flags[ma_nguoi_dung] = False
    stt = 0
    so_luot_thanh_cong = 0
    while not stop_sharing_flags.get(ma_nguoi_dung, False):
        tasks = []
        for tach in all_tokens:
            if lay_so_luot_chia_se(ma_nguoi_dung) >= GIOI_HAN_CHIA_SE_HANG_NGAY:
                await bot.send_message(chat_id, f"Bạn đã đạt đến giới hạn chia sẻ hàng ngày là {GIOI_HAN_CHIA_SE_HANG_NGAY}. Vui lòng thử lại vào ngày mai.")
                stop_sharing_flags[ma_nguoi_dung] = True
                break

            tasks.append(chia_se(tach.split('|')[0], tach.split('|')[1], id_chia_se))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        for success in results:
            if isinstance(success, bool) and success:
                so_luot_thanh_cong += 1
                await cap_nhat_so_luot_chia_se(ma_nguoi_dung)
                await cap_nhat_thoi_gian_chia_se(ma_nguoi_dung)
            elif isinstance(success, Exception):
                logger.error(f"[!] Lỗi trong quá trình chia sẻ: {success}")

        if gioi_han_tong_luot > 0 and so_luot_thanh_cong >= gioi_han_tong_luot:
            stop_sharing_flags[ma_nguoi_dung] = True

        # Ngẫu nhiên hóa độ trễ giữa các chu kỳ để tránh phát hiện và giữ tốc độ cao
        await asyncio.sleep(random.uniform(max(0, do_tre - 2), do_tre + 2))

    await bot.send_message(chat_id, "Quá trình chia sẻ đã hoàn tất.")
    if gioi_han_tong_luot > 0 and so_luot_thanh_cong >= gioi_han_tong_luot:
        await bot.send_message(chat_id, f"Đã đạt đến giới hạn chia sẻ là {gioi_han_tong_luot} lượt.")
    await bot.send_message(chat_id, f"Tổng số lượt chia sẻ thành công: {so_luot_thanh_cong}.")
    await dat_lai_du_lieu_nguoi_dung(ma_nguoi_dung)

# Các hàm xử lý cơ sở dữ liệu (bất đồng bộ, chi tiết)
async def lay_du_lieu_nguoi_dung(ma_nguoi_dung: int) -> Optional[Dict]:
    async with aiosqlite.connect('bot_chia_se_an_danh.db') as conn:
        async with await conn.execute("SELECT du_lieu FROM nguoi_dung WHERE ma_nguoi_dung = ?", (ma_nguoi_dung,)) as cursor:
            result = await cursor.fetchone()
            return json.loads(result[0]) if result else None

async def cap_nhat_so_luot_chia_se(ma_nguoi_dung: int) -> None:
    async with aiosqlite.connect('bot_chia_se_an_danh.db') as conn:
        await conn.execute("UPDATE nguoi_dung SET so_luot_chia_se = so_luot_chia_se + 1 WHERE ma_nguoi_dung = ?", (ma_nguoi_dung,))
        await conn.commit()

async def cap_nhat_thoi_gian_chia_se(ma_nguoi_dung: int) -> None:
    async with aiosqlite.connect('bot_chia_se_an_danh.db') as conn:
        await conn.execute("UPDATE nguoi_dung SET thoi_gian_cuoi_chia_se = ? WHERE ma_nguoi_dung = ?", 
                          (datetime.now(VN_TIMEZONE).isoformat(), ma_nguoi_dung))
        await conn.commit()

async def dat_lai_du_lieu_nguoi_dung(ma_nguoi_dung: int) -> None:
    async with aiosqlite.connect('bot_chia_se_an_danh.db') as conn:
        await conn.execute("UPDATE nguoi_dung SET so_luot_chia_se = 0, ngay_dat_lai = ?, du_lieu = ?, thoi_gian_cuoi_chia_se = NULL WHERE ma_nguoi_dung = ?", 
                          (datetime.now(VN_TIMEZONE).date(), json.dumps({}), ma_nguoi_dung))
        await conn.commit()

async def kiem_tra_gioi_han_hang_ngay(ma_nguoi_dung: int) -> bool:
    async with aiosqlite.connect('bot_chia_se_an_danh.db') as conn:
        async with await conn.execute("SELECT so_luot_chia_se, ngay_dat_lai FROM nguoi_dung WHERE ma_nguoi_dung = ?", (ma_nguoi_dung,)) as cursor:
            result = await cursor.fetchone()
            if result:
                so_luot, ngay_dat_lai = result
                ngay_hien_tai = datetime.now(VN_TIMEZONE).date()
                return so_luot >= GIOI_HAN_CHIA_SE_HANG_NGAY and ngay_dat_lai == ngay_hien_tai
            return False

async def lay_so_luot_chia_se(ma_nguoi_dung: int) -> int:
    async with aiosqlite.connect('bot_chia_se_an_danh.db') as conn:
        async with await conn.execute("SELECT so_luot_chia_se FROM nguoi_dung WHERE ma_nguoi_dung = ?", (ma_nguoi_dung,)) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0

async def cap_nhat_du_lieu_nguoi_dung(ma_nguoi_dung: int, du_lieu: Dict) -> None:
    async with aiosqlite.connect('bot_chia_se_an_danh.db') as conn:
        await conn.execute("INSERT OR REPLACE INTO nguoi_dung (ma_nguoi_dung, so_luot_chia_se, ngay_dat_lai, du_lieu, thoi_gian_cuoi_chia_se) VALUES (?, 0, ?, ?, NULL)", 
                          (ma_nguoi_dung, datetime.now(VN_TIMEZONE).date(), json.dumps(du_lieu)))
        await conn.commit()

# Xử lý lệnh /chia_se chỉ trong nhóm
@bot.message_handler(commands=['chia_se'], chat_types=['group', 'supergroup'])
async def chia_se_lenh(message):
    ma_nguoi_dung = message.from_user.id
    chat_id = message.chat.id
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
    nut_dung = types.InlineKeyboardButton("Dừng Chia Sẻ", callback_data=f"dung_chia_se_{ma_nguoi_dung}")
    markup.add(nut_dung)
    await bot.send_message(chat_id, "Vui lòng gửi file cookie (cookies.txt).", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("dung_chia_se_"))
async def dung_chia_se_callback(call):
    ma_nguoi_dung = int(call.data.split("_")[-1])
    stop_sharing_flags[ma_nguoi_dung] = True
    await bot.send_message(call.message.chat.id, "Đã dừng chia sẻ. Vui lòng đợi quá trình hiện tại kết thúc.")

# Xử lý file cookie chỉ trong nhóm
@bot.message_handler(content_types=['document'], chat_types=['group', 'supergroup'])
async def xu_ly_tai_lieu(message):
    ma_nguoi_dung = message.from_user.id
    chat_id = message.chat.id
    du_lieu = await lay_du_lieu_nguoi_dung(ma_nguoi_dung)
    if not du_lieu or 'cookie_file' not in du_lieu:
        try:
            file_info = await bot.get_file(message.document.file_id)
            downloaded_file = await bot.download_file(file_info.file_path)
            cookie_file = downloaded_file.decode('utf-8').splitlines()
            du_lieu['cookie_file'] = cookie_file
            await cap_nhat_du_lieu_nguoi_dung(ma_nguoi_dung, du_lieu)
            await bot.send_message(chat_id, "Đã nhận file cookie. Vui lòng nhập ID bài viết cần chia sẻ.")
        except Exception as e:
            logger.error(f"[!] Lỗi khi xử lý file cho người dùng {ma_nguoi_dung}: {e}")
            await bot.reply_to(message, f"Lỗi khi xử lý file: {e}")
            await dat_lai_du_lieu_nguoi_dung(ma_nguoi_dung)

@bot.message_handler(content_types=['text'], chat_types=['group', 'supergroup'])
async def xu_ly_id_do_tre_gioi_han(message):
    ma_nguoi_dung = message.from_user.id
    chat_id = message.chat.id
    du_lieu = await lay_du_lieu_nguoi_dung(ma_nguoi_dung)
    if not du_lieu:
        return

    if 'cookie_file' not in du_lieu:
        await bot.reply_to(message, "Vui lòng gửi file cookie trước.")
        return
    elif 'id_chia_se' not in du_lieu:
        id_chia_se = message.text.strip()
        if not id_chia_se.isdigit():
            await bot.reply_to(message, "ID không hợp lệ. Vui lòng nhập lại ID bài viết.")
            return
        du_lieu['id_chia_se'] = id_chia_se
        await cap_nhat_du_lieu_nguoi_dung(ma_nguoi_dung, du_lieu)
        await bot.send_message(chat_id, "Vui lòng nhập độ trễ giữa các lần chia sẻ (tính bằng giây).")
    elif 'do_tre' not in du_lieu:
        try:
            do_tre = int(message.text.strip())
            if do_tre < 0:
                raise ValueError
            du_lieu['do_tre'] = do_tre
            await cap_nhat_du_lieu_nguoi_dung(ma_nguoi_dung, du_lieu)
            await bot.send_message(chat_id, "Vui lòng nhập tổng số lượt chia sẻ (0 để không giới hạn).")
        except ValueError:
            await bot.reply_to(message, "Độ trễ không hợp lệ. Vui lòng nhập độ trễ (tính bằng giây) là một số.")
    elif 'gioi_han_tong_luot' not in du_lieu:
        try:
            gioi_han_tong_luot = int(message.text.strip())
            if gioi_han_tong_luot < 0:
                raise ValueError
            du_lieu['gioi_han_tong_luot'] = gioi_han_tong_luot
            await cap_nhat_du_lieu_nguoi_dung(ma_nguoi_dung, du_lieu)
            markup = types.InlineKeyboardMarkup()
            nut_dung = types.InlineKeyboardButton("Dừng Chia Sẻ", callback_data=f"dung_chia_se_{ma_nguoi_dung}")
            markup.add(nut_dung)
            await bot.send_message(chat_id, "Bắt đầu chia sẻ...", reply_markup=markup)
            await bat_dau_chia_se(ma_nguoi_dung, chat_id)
        except ValueError:
            await bot.reply_to(message, "Giới hạn chia sẻ không hợp lệ. Vui lòng nhập tổng số lượt chia sẻ (0 để không giới hạn) là một số.")

# Hàm chính (bất đồng bộ, tối ưu hóa tốc độ và độ tin cậy)
async def main():
    await khoi_tao_co_so_du_lieu()
    try:
        await bot.polling(non_stop=True, timeout=10, allowed_updates=['message', 'callback_query'])
    except Exception as e:
        logger.error(f"[!] Lỗi khi polling bot: {e}")
        await asyncio.sleep(5)  # Chờ 5 giây trước khi thử lại
        await main()  # Thử lại polling

if __name__ == "__main__":
    asyncio.run(main())