import telebot
import requests
from bs4 import BeautifulSoup
import re
import asyncio
import aiohttp
import logging
import json
import random
import time
import os

# --- Cấu hình ---
BOT_TOKEN = "7903504769:AAFPy0G459oCKCs0s1xM7yi60mSSLAx9VAU" # Thay thế bằng token bot Telegram của bạn
PROXY_SOURCES_HTTP = [
    "https://www.proxy-list.download/http",
    "https://free-proxy-list.net/",
    "https://www.sslproxies.org/",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http",
    "https://proxylist.geonode.com/api/proxy-lists?limit=500&page=1&sort_by=last_checked&sort_type=desc", # JSON API
    "https://proxylist.geonode.com/api/proxy-lists?limit=500&page=2&sort_by=last_checked&sort_type=desc", # JSON API Page 2
    "https://proxylist.geonode.com/api/proxy-lists?limit=500&page=3&sort_by=last_checked&sort_type=desc", # JSON API Page 3
    "https://proxylist.geonode.com/api/proxy-lists?limit=500&page=4&sort_by=last_checked&sort_type=desc", # JSON API Page 4
    "https://proxylist.geonode.com/api/proxy-lists?limit=500&page=5&sort_by=last_checked&sort_type=desc", # JSON API Page 5
    "https://proxylist.geonode.com/api/proxy-lists?limit=500&page=6&sort_by=last_checked&sort_type=desc", # JSON API Page 6
    "https://proxylist.geonode.com/api/proxy-lists?limit=500&page=7&sort_by=last_checked&sort_type=desc", # JSON API Page 7
    "https://proxylist.geonode.com/api/proxy-lists?limit=500&page=8&sort_by=last_checked&sort_type=desc", # JSON API Page 8
    "https://proxylist.geonode.com/api/proxy-lists?limit=500&page=9&sort_by=last_checked&sort_type=desc", # JSON API Page 9
    "https://proxylist.geonode.com/api/proxy-lists?limit=500&page=10&sort_by=last_checked&sort_type=desc", # JSON API Page 10
]
PROXY_SOURCES_HTTPS = [
    "https://www.proxy-list.download/https",
    "https://www.sslproxies.org/",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/https.txt",
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=https"
]
PROXY_SOURCES_SOCKS4 = [
    "https://www.proxy-list.download/socks4",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt",
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks4"
]
PROXY_SOURCES_SOCKS5 = [
    "https://www.proxy-list.download/socks5",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5"
]
PROXY_SOURCES_IPV6 = [
    "https://www.proxy-list.download/ipv6",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/ipv6.txt",
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&ipv6=true" # Lưu ý: Một số nguồn có thể liệt kê IPv6 là SOCKS5
]

PROXY_STORAGE_FILE = "proxy_list.json"
PROXY_CHECK_TIMEOUT = 5  # giây cho timeout kiểm tra proxy
PROXY_CHECK_URL = "http://httpbin.org/ip" # URL để kiểm tra proxy hoạt động (HTTP)
PROXY_CHECK_HTTPS_URL = "https://httpbin.org/ip" # URL để kiểm tra proxy HTTPS
PROXY_CHECK_SOCKS_URL = "http://httpbin.org/ip" # URL cho kiểm tra proxy SOCKS - HTTP là đủ để kiểm tra kết nối

# --- Biến toàn cục ---
proxy_list = {
    "http": [],
    "https": [],
    "socks4": [],
    "socks5": [],
    "ipv6": []
}
scraping_in_progress = False
last_scrape_time = None
scrape_interval = 3600  # 1 giờ (giây)

# --- Cấu hình Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Khởi tạo Bot ---
bot = telebot.TeleBot(BOT_TOKEN)

# --- Hàm tiện ích ---

def load_proxies_from_file():
    """Tải proxies từ file lưu trữ."""
    global proxy_list
    try:
        with open(PROXY_STORAGE_FILE, "r") as f:
            proxy_list = json.load(f)
        logger.info(f"Proxies đã tải từ {PROXY_STORAGE_FILE}")
    except FileNotFoundError:
        logger.info(f"File proxy {PROXY_STORAGE_FILE} không tìm thấy. Bắt đầu với danh sách proxy trống.")
        proxy_list = {
            "http": [],
            "https": [],
            "socks4": [],
            "socks5": [],
            "ipv6": []
        }
    except json.JSONDecodeError:
        logger.error(f"Lỗi giải mã JSON từ {PROXY_STORAGE_FILE}. Bắt đầu với danh sách proxy trống.")
        proxy_list = {
            "http": [],
            "https": [],
            "socks4": [],
            "socks5": [],
            "ipv6": []
        }
    return proxy_list

def save_proxies_to_file():
    """Lưu proxies vào file lưu trữ."""
    try:
        with open(PROXY_STORAGE_FILE, "w") as f:
            json.dump(proxy_list, f, indent=4)
        logger.info(f"Proxies đã lưu vào {PROXY_STORAGE_FILE}")
    except Exception as e:
        logger.error(f"Lỗi khi lưu proxies vào {PROXY_STORAGE_FILE}: {e}")

def is_valid_proxy_format(proxy_str):
    """Kiểm tra xem chuỗi proxy có định dạng IP:PORT hợp lệ không."""
    pattern = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+$") # IPv4
    pattern_ipv6 = re.compile(r"^\[[0-9a-fA-F:]+\]:\d+$") # IPv6
    return bool(pattern.match(proxy_str) or pattern_ipv6.match(proxy_str))

async def check_proxy_anonymity(proxy, proxy_type):
    """
    Kiểm tra mức độ ẩn danh của proxy.
    Trả về "elite", "anonymous", "transparent", hoặc None nếu kiểm tra thất bại.
    """
    check_url = PROXY_CHECK_URL
    if proxy_type == "https":
        check_url = PROXY_CHECK_HTTPS_URL
    elif proxy_type in ["socks4", "socks5"]:
        check_url = PROXY_CHECK_SOCKS_URL

    try:
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            async with session.get(check_url, proxy=f"{proxy_type}://{proxy}", timeout=PROXY_CHECK_TIMEOUT) as response:
                elapsed_time = time.time() - start_time
                if response.status == 200:
                    origin_ip = (await response.json()).get('origin', '')
                    if "," in origin_ip:
                        return "anonymous" # Proxy ẩn danh - tiết lộ IP proxy, không phải IP client
                    else:
                        return "elite" # Proxy tinh túy - không tiết lộ IP client hoặc proxy
                else:
                    logger.warning(f"Kiểm tra proxy thất bại với status {response.status} cho {proxy} ({proxy_type})")
                    return None
    except aiohttp.ClientError as e:
        logger.error(f"Lỗi AIOHTTP Client trong quá trình kiểm tra proxy cho {proxy} ({proxy_type}): {e}")
        return None
    except asyncio.TimeoutError:
        logger.error(f"Timeout trong quá trình kiểm tra proxy cho {proxy} ({proxy_type})")
        return None
    except Exception as e:
        logger.error(f"Lỗi không mong muốn trong quá trình kiểm tra proxy cho {proxy} ({proxy_type}): {e}")
        return None


async def is_working_proxy(proxy, proxy_type):
    """Kiểm tra xem proxy có hoạt động không."""
    check_url = PROXY_CHECK_URL
    if proxy_type == "https":
        check_url = PROXY_CHECK_HTTPS_URL
    elif proxy_type in ["socks4", "socks5"]:
        check_url = PROXY_CHECK_SOCKS_URL

    try:
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            async with session.get(check_url, proxy=f"{proxy_type}://{proxy}", timeout=PROXY_CHECK_TIMEOUT) as response:
                elapsed_time = time.time() - start_time
                return response.status == 200
    except Exception as e:
        return False


async def scrape_proxies_from_source(source_url, proxy_type, message):
    """Cào proxies từ một nguồn URL duy nhất."""
    global proxy_list
    new_proxies = []
    logger.info(f"Đang cào proxy {proxy_type.upper()} từ: {source_url}")
    await bot.send_message(message.chat.id, f"Đang cào proxy {proxy_type.upper()} từ: {source_url}")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(source_url, timeout=30) as response:
                if response.status == 200:
                    text = await response.text()

                    if "proxylist.geonode.com" in source_url and "/api/proxy-lists" in source_url: # Xử lý JSON API
                        try:
                            json_data = json.loads(text)
                            for item in json_data.get('data', []):
                                if item.get('protocols') and proxy_type.upper() in [p.upper() for p in item.get('protocols')]:
                                    ip = item.get('ip')
                                    port = item.get('port')
                                    if ip and port:
                                        proxy_str = f"{ip}:{port}"
                                        if is_valid_proxy_format(proxy_str):
                                            new_proxies.append(proxy_str)
                        except json.JSONDecodeError:
                            logger.error(f"Lỗi giải mã JSON từ {source_url}")

                    elif "api.proxyscrape.com" in source_url: # Plain text API
                        proxies = text.strip().splitlines()
                        for proxy_str in proxies:
                            if is_valid_proxy_format(proxy_str.strip()):
                                new_proxies.append(proxy_str.strip())

                    elif "raw.githubusercontent.com" in source_url: # Danh sách văn bản thô
                        proxies = text.strip().splitlines()
                        for proxy_str in proxies:
                            if is_valid_proxy_format(proxy_str.strip()):
                                new_proxies.append(proxy_str.strip())

                    else: # Cào HTML cho các trang web khác
                        soup = BeautifulSoup(text, "html.parser")
                        if "proxy-list.download" in source_url:
                            table = soup.find("table", class_="table-striped")
                            if table:
                                rows = table.find_all("tr")[1:] # Bỏ qua hàng tiêu đề
                                for row in rows:
                                    cols = row.find_all("td")
                                    if len(cols) >= 2:
                                        ip = cols[0].text.strip()
                                        port = cols[1].text.strip()
                                        proxy_str = f"{ip}:{port}"
                                        if is_valid_proxy_format(proxy_str):
                                            new_proxies.append(proxy_str)
                        elif "free-proxy-list.net" in source_url or "sslproxies.org" in source_url:
                            table = soup.find("table", id="proxylisttable")
                            if table:
                                rows = table.find_all("tr")[1:]
                                for row in rows:
                                    cols = row.find_all("td")
                                    if len(cols) >= 2:
                                        ip = cols[0].text.strip()
                                        port = cols[1].text.strip()
                                        proxy_str = f"{ip}:{port}"
                                        if is_valid_proxy_format(proxy_str):
                                            new_proxies.append(proxy_str)

                else:
                    logger.warning(f"Không thể truy xuất proxy {proxy_type} từ {source_url}. Mã trạng thái: {response.status}")
                    await bot.send_message(message.chat.id, f"Không thể truy xuất proxy {proxy_type} từ {source_url}. Mã trạng thái: {response.status}")

    except aiohttp.ClientError as e:
        logger.error(f"Lỗi AIOHTTP Client trong quá trình cào từ {source_url}: {e}")
        await bot.send_message(message.chat.id, f"Lỗi khi cào từ {source_url}: {e}")
    except asyncio.TimeoutError:
        logger.error(f"Timeout khi cào từ {source_url}")
        await bot.send_message(message.chat.id, f"Timeout khi cào từ {source_url}")
    except Exception as e:
        logger.error(f"Lỗi không mong muốn trong quá trình cào từ {source_url}: {e}")
        await bot.send_message(message.chat.id, f"Lỗi không mong muốn trong quá trình cào từ {source_url}: {e}")

    valid_proxies = []
    for proxy in new_proxies:
        if proxy not in proxy_list[proxy_type]: # Tránh trùng lặp trong cùng một lần cào
            valid_proxies.append(proxy)

    proxy_list[proxy_type].extend(valid_proxies) # Thêm proxies mới

    logger.info(f"Tìm thấy {len(valid_proxies)} proxy {proxy_type.upper()} mới từ {source_url}")
    await bot.send_message(message.chat.id, f"Tìm thấy {len(valid_proxies)} proxy {proxy_type.upper()} mới từ {source_url}")
    return valid_proxies


async def scrape_all_proxies_async(message):
    """Cào proxy từ tất cả các nguồn cấu hình (hàm async)."""
    global scraping_in_progress, last_scrape_time, proxy_list

    if scraping_in_progress:
        await bot.send_message(message.chat.id, "Quá trình cào proxy đang diễn ra. Vui lòng đợi.")
        return

    if last_scrape_time and time.time() - last_scrape_time < scrape_interval:
        time_since_last_scrape = time.time() - last_scrape_time
        remaining_time = scrape_interval - time_since_last_scrape
        await bot.send_message(message.chat.id, f"Vui lòng đợi {int(remaining_time/60)} phút trước khi cào lại.")
        return

    scraping_in_progress = True
    last_scrape_time = time.time()
    await bot.send_message(message.chat.id, "Bắt đầu cào proxy từ tất cả các nguồn...")

    proxy_counts_before = {k: len(v) for k, v in proxy_list.items()}

    scrape_tasks = []
    scrape_tasks.append(scrape_proxies_from_source(PROXY_SOURCES_HTTP, "http", message))
    scrape_tasks.append(scrape_proxies_from_source(PROXY_SOURCES_HTTPS, "https", message))
    scrape_tasks.append(scrape_proxies_from_source(PROXY_SOURCES_SOCKS4, "socks4", message))
    scrape_tasks.append(scrape_proxies_from_source(PROXY_SOURCES_SOCKS5, "socks5", message))
    scrape_tasks.append(scrape_proxies_from_source(PROXY_SOURCES_IPV6, "ipv6", message))

    await asyncio.gather(*scrape_tasks) # Chạy tất cả các task cào đồng thời

    save_proxies_to_file() # Lưu ngay sau khi cào

    proxy_counts_after = {k: len(v) for k, v in proxy_list.items()}
    newly_added_counts = {k: proxy_counts_after[k] - proxy_counts_before[k] for k in proxy_counts_before}

    summary_message = "Hoàn tất cào proxy!\n"
    summary_message += f"Proxy HTTP thêm vào: {newly_added_counts['http']}\n"
    summary_message += f"Proxy HTTPS thêm vào: {newly_added_counts['https']}\n"
    summary_message += f"Proxy SOCKS4 thêm vào: {newly_added_counts['socks4']}\n"
    summary_message += f"Proxy SOCKS5 thêm vào: {newly_added_counts['socks5']}\n"
    summary_message += f"Proxy IPv6 thêm vào: {newly_added_counts['ipv6']}\n"
    summary_message += f"\nTổng Proxy HTTP: {proxy_counts_after['http']}\n"
    summary_message += f"Tổng Proxy HTTPS: {proxy_counts_after['https']}\n"
    summary_message += f"Tổng Proxy SOCKS4: {proxy_counts_after['socks4']}\n"
    summary_message += f"Tổng Proxy SOCKS5: {proxy_counts_after['socks5']}\n"
    summary_message += f"Tổng Proxy IPv6: {proxy_counts_after['ipv6']}\n"

    await bot.send_message(message.chat.id, summary_message)

    # Gửi file proxy
    for proxy_type in proxy_list:
        if proxy_list[proxy_type]:
            file_path = f"{proxy_type}_proxies.txt"
            with open(file_path, "w") as f:
                f.write("\n".join(proxy_list[proxy_type]))
            with open(file_path, "rb") as f:
                await bot.send_document(message.chat.id, f, caption=f"Danh sách proxy {proxy_type.upper()}")
            os.remove(file_path) # Xóa file sau khi gửi

    scraping_in_progress = False


def scrape_all_proxies(message):
    """Xử lý lệnh cào proxy, yêu cầu chat riêng nếu ở group."""
    if message.chat.type == 'group' or message.chat.type == 'supergroup':
        bot.reply_to(message, "Lệnh /scrape chỉ hoạt động trong chat riêng với bot. Vui lòng bắt đầu chat riêng và sử dụng lệnh ở đó.")
    else:
        asyncio.run(scrape_all_proxies_async(message)) # Chạy hàm async trong thread chính


@bot.message_handler(commands=['proxy'])
def get_proxy(message):
    """Gửi một proxy theo yêu cầu."""
    args = message.text.split()[1:]
    if not args:
        bot.reply_to(message, "Vui lòng chỉ định loại proxy: http, https, socks4, socks5 hoặc ipv6. Ví dụ: /proxy http")
        return

    proxy_type = args[0].lower()
    if proxy_type not in proxy_list:
        bot.reply_to(message, "Loại proxy không hợp lệ. Vui lòng chọn từ: http, https, socks4, socks5, ipv6.")
        return

    if not proxy_list[proxy_type]:
        bot.reply_to(message, f"Không có proxy {proxy_type.upper()} nào khả dụng. Vui lòng cào proxy trước bằng lệnh /scrape.")
        return

    proxy = random.choice(proxy_list[proxy_type])
    bot.reply_to(message, f"Đây là proxy {proxy_type.upper()} của bạn: `{proxy}`", parse_mode="Markdown")


@bot.message_handler(commands=['proxylist'])
def get_proxy_list(message):
    """Gửi danh sách proxy theo yêu cầu."""
    args = message.text.split()[1:]
    if not args:
        bot.reply_to(message, "Vui lòng chỉ định loại proxy: http, https, socks4, socks5 hoặc ipv6. Ví dụ: /proxylist http")
        return

    proxy_type = args[0].lower()
    if proxy_type not in proxy_list:
        bot.reply_to(message, "Loại proxy không hợp lệ. Vui lòng chọn từ: http, https, socks4, socks5, ipv6.")
        return

    if not proxy_list[proxy_type]:
        bot.reply_to(message, f"Không có proxy {proxy_type.upper()} nào khả dụng. Vui lòng cào proxy trước bằng lệnh /scrape.")
        return

    proxy_str_list = "\n".join(proxy_list[proxy_type])
    if len(proxy_str_list) > 3000: # Giới hạn tin nhắn Telegram
        parts = [proxy_str_list[i:i+3000] for i in range(0, len(proxy_str_list), 3000)]
        for i, part in enumerate(parts):
            bot.send_message(message.chat.id, f"Danh sách proxy {proxy_type.upper()} (phần {i+1}):\n`{part}`", parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, f"Danh sách proxy {proxy_type.upper()}:\n`{proxy_str_list}`", parse_mode="Markdown")


async def check_proxies_async(message):
    """Kiểm tra trạng thái hoạt động của proxy và loại bỏ proxy không hoạt động (hàm async)."""
    global proxy_list
    await bot.send_message(message.chat.id, "Bắt đầu kiểm tra proxy. Quá trình này có thể mất một lúc...")

    for proxy_type in list(proxy_list.keys()): # Lặp trên bản sao để có thể sửa đổi
        working_proxies = []
        proxies_to_check = proxy_list[proxy_type][:] # Tạo bản sao để tránh sửa đổi trong quá trình lặp
        total_proxies = len(proxies_to_check)
        checked_count = 0

        for proxy in proxies_to_check:
            if await is_working_proxy(proxy, proxy_type):
                working_proxies.append(proxy)
            checked_count += 1
            if checked_count % 50 == 0: # Gửi cập nhật trạng thái sau mỗi 50 lần kiểm tra
                await bot.send_message(message.chat.id, f"Đã kiểm tra {checked_count}/{total_proxies} proxy {proxy_type.upper()}...")

        proxy_list[proxy_type] = working_proxies
        await bot.send_message(message.chat.id, f"Kiểm tra proxy {proxy_type.upper()} hoàn tất. Tìm thấy {len(working_proxies)} proxy hoạt động trong tổng số {total_proxies}.")

    save_proxies_to_file()
    await bot.send_message(message.chat.id, "Kiểm tra proxy hoàn tất cho tất cả các loại. Đã loại bỏ proxy không hoạt động.")


@bot.message_handler(commands=['check'])
def check_proxies(message):
    """Xử lý lệnh kiểm tra proxy."""
    asyncio.run(check_proxies_async(message))


@bot.message_handler(commands=['stats'])
def get_proxy_stats(message):
    """Cung cấp thống kê về danh sách proxy hiện tại."""
    stats_message = "Thống kê Proxy Hiện Tại:\n"
    total_proxies = 0
    for proxy_type, proxies in proxy_list.items():
        count = len(proxies)
        stats_message += f"- Proxy {proxy_type.upper()}: {count}\n"
        total_proxies += count
    stats_message += f"\nTổng Proxy: {total_proxies}"
    bot.reply_to(message, stats_message)


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    """Gửi tin nhắn chào mừng và hướng dẫn."""
    help_text = """
Chào mừng bạn đến với Bot Đào Proxy!

Các lệnh khả dụng:

/start - Bắt đầu bot và hiển thị tin nhắn chào mừng.
/help - Hiển thị tin nhắn trợ giúp này.
/scrape - Bắt đầu cào proxy từ tất cả các nguồn cấu hình (chỉ hoạt động trong chat riêng).
/proxy <loại> - Lấy một proxy đơn lẻ theo loại được chỉ định (http, https, socks4, socks5, ipv6). Ví dụ: /proxy http
/proxylist <loại> - Lấy danh sách proxy theo loại được chỉ định. Ví dụ: /proxylist socks5
/check - Kiểm tra trạng thái hoạt động của tất cả proxy và loại bỏ proxy không hoạt động.
/stats - Hiển thị thống kê về danh sách proxy hiện tại.
    """
    bot.reply_to(message, help_text)


if __name__ == '__main__':
    load_proxies_from_file() # Tải proxy khi khởi động
    bot.infinity_polling()