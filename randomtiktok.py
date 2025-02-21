import telebot
import requests
import os
import json
import random
from time import sleep
from datetime import datetime

# Telegram Bot Token (thay thế bằng token bot của bạn)
BOT_TOKEN = "7903504769:AAEMX3AUeOgGXvHNMQ5x7T7XcewuK90quNQ"  # Thay thế bằng token bot thật của bạn
bot = telebot.TeleBot(BOT_TOKEN)

# Biến toàn cục để lưu trữ dữ liệu người dùng
cookie_nguoi_dung = {}
so_luong_tai_khoan = {}
thoi_gian_tre = {}
anh_dai_dien_nguoi_dung = {}

# Nguồn proxy (thêm nhiều hơn nếu cần)
nguon_proxy = [
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http"
]

def lay_proxy():
    """Lấy danh sách proxy từ các nguồn và trả về một proxy ngẫu nhiên."""
    proxies = []
    for source in nguon_proxy:
        try:
            response = requests.get(source, timeout=5)
            if response.status_code == 200:
                proxies.extend(response.text.strip().split('\n'))
            else:
                print(f"Không thể lấy proxy từ {source}: {response.status_code}")
        except Exception as e:
            print(f"Lỗi khi lấy proxy từ {source}: {e}")

    if proxies:
        proxy_string = random.choice(proxies)  # Chọn ngẫu nhiên một proxy
        return dinh_dang_proxy(proxy_string)
    else:
        return None



def dinh_dang_proxy(proxy_string):
    """Định dạng chuỗi proxy thành dictionary phù hợp cho requests."""
    try:
        if "@" in proxy_string:
            userpass, address = proxy_string.split("@")
            username, password = userpass.split(":")
            ip, port = address.split(":")
            proxy_url = f"http://{username}:{password}@{ip}:{port}"
        else:
            ip, port = proxy_string.split(":")
            proxy_url = f"http://{ip}:{port}"

        return {"http": proxy_url, "https": proxy_url}  # Sử dụng cùng một proxy cho cả http và https

    except ValueError:
        print(f"Định dạng proxy không hợp lệ: {proxy_string}")
        return None


def kiem_tra_cookie(cookie):
    """Kiểm tra xem cookie còn sống hay không."""
    headers_get = {
        'authority': 'www.facebook.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
        'sec-ch-prefers-color-scheme': 'light',
        'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'viewport-width': '1184',
        'cookie': cookie
    }
    uid = cookie.split('c_user=')[1].split(';')[0]
    try:
        url = requests.get(f"https://mbasic.facebook.com/profile.php?id={uid}", headers=headers_get, timeout=10).text
        if 'Đăng nhập Facebook' in url:
            return 'error_ck'
        else:
            return 'valid_ck'  # Chỉ trả về 'valid_ck' nếu cookie hợp lệ
    except requests.exceptions.RequestException as e:
        print(f"Lỗi trong quá trình kiểm tra cookie: {e}")
        return 'error_ck'
    except Exception as e:
        print(f"Một lỗi không mong muốn đã xảy ra: {e}")
        return 'error_ck'



def dang_ky(cookie, proxy):
    """Đăng ký tài khoản Pro5."""
    ge = requests.get("https://story-shack-cdn-v2.glitch.me/generators/vietnamese-name-generator/male?count=2").json()
    name = ge["data"][0]["name"]
    headers_get = {
        'authority': 'www.facebook.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
        'sec-ch-prefers-color-scheme': 'light',
        'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'viewport-width': '1184',
        'cookie': cookie
    }
    try:
        url_profile = requests.get('https://www.facebook.com/', headers=headers_get, proxies=proxy, timeout=10).url
        get_dulieu_profile = requests.get(url=url_profile, headers=headers_get, proxies=proxy, timeout=10).text
        try:
            uid = cookie.split('c_user=')[1].split(';')[0]
            fb_dtsg = get_dulieu_profile.split('{"name":"fb_dtsg","value":"')[1].split('"},')[0]
            jazoest = get_dulieu_profile.split('{"name":"jazoest","value":"')[1].split('"},')[0]
        except:
            uid = cookie.split('c_user=')[1].split(';')[0]
            fb_dtsg = get_dulieu_profile.split(',"f":"')[1].split('","l":null}')[0]
            jazoest = get_dulieu_profile.split('&jazoest=')[1].split('","e":"')[0]
    except requests.exceptions.RequestException as e:
        print(f"Lỗi trong quá trình đăng ký: {e}")
        return 'error_ck'
    except Exception as e:
        print(f"Một lỗi không mong muốn đã xảy ra: {e}")
        return 'error_ck'
    data_reg = {
        "av": uid,
        "__user": uid,
        "__a": "1",
        "__req": "1q",
        "__hs": "19551.HYP:comet_pkg.2.1..2.1",
        "dpr": "2",
        "__ccg": "EXCELLENT",
        "__rev": "1007833183",
        "__s": "o7dsck:w3oksn:4lt5bc",
        "__hsi": "7255348447748397298",
        "__dyn": "7AzHJ16UW5A9Uvxt0mUyEqxd4WobVo66u2i5U4e2C17yUJ3odF8iz8K361twYwJyEiwsobo6u3y4o27wxg3Qwb-q7oc81xoswIK1Rwwwg8a8465o-cw8a1TwgEcEhwGxu782lwj8bU9kbxS210hUb82kwiEjwZx-3m1mzXw8W58jwGzEjzFU5e7oqBwJK2W5olwUwOzEjUlDw-wUwxwhFVovUy2a1ywtUuBwFKq2-azqwqoG3C223908O3216xi4UdUcojxK2B0LwNwJwxyo566k1Fw",
        "__csr": "gugzf2RhWlQIBOPTdilhcj_tOnkttT22dtiaynbb5Tb8gIBdOkNdiJfBsztQDJH8cjH-GulZcDR_mCDmDiBjGmh4hV999aDyFcGrh24VayeJJ25Q9GtpF39d2BHjvCCKmt3GyJqkyQhbZ2emqFqXy9kiBWQmqmAi9xfh9QleiuVUlGQEWbUyjmKbH-HGi4rCyFkdCx2uUhBAgKuq9SjK8KFVGuqEhKmUGi4Fay4qidyoCWAy8y9yoOdxm9AyqAKidyAmq2qfyVFkq9gyl242mcwMQ4fxd0Vz8dRG8xp2WUrAxd7DgrVoiUpxG2erxu2umvy8fFrXwAXKEK4Ey8GaDwDwCK6Q-58kBU4i4Unwno8o1WE34h40cig19U4tnmQRAG09_wi836w1ve1zG8wFCO5K19w0DszBzE9E9UJ9044w0qjE0kvh80UK06580jLwbe2RELDBw8uFx4FpJ90tF6360qq0Kk0YE2iwXF09O0JA8A5yimWbeEgljCN9t09a0cODxi1awl9A0Zo2qwpo29w8C0Se1Gw4Uw864U2QDgG250Pxmbw7OCw5knU2WOw2F80T2ca2",
        "__comet_req": "15",
        "fb_dtsg": fb_dtsg,
        "jazoest": jazoest,
        "lsd": "l8l0qNMKPcF6xiSPGFtn5Y",
        "__spin_r": "1007833183",
        "__spin_b": "trunk",
        "__spin_t": "1689267449",
        "qpl_active_flow_ids": "1056839232",
        "fb_api_caller_class": "RelayModern",
        "fb_api_req_friendly_name": "AdditionalProfilePlusCreationMutation",
        "variables": '{"input":{"bio":"","categories":["183013211744255"],"creation_source":"comet","name":"' + name + '","page_referrer":"launch_point","actor_id":"' + uid + '","client_mutation_id":"2"}}',
        "server_timestamps": "True",
        "doc_id": "5296879960418435",
        "fb_api_analytics_tags": ["qpl_active_flow_ids=1056839232"]
    }
    try:
        hh = requests.post('https://www.facebook.com/api/graphql/', headers=headers_get, data=data_reg, proxies=proxy, timeout=10).json()['data']['additional_profile_plus_create']['additional_profile']['id']
        return hh, name
    except requests.exceptions.RequestException as e:
        print(f"Lỗi trong quá trình đăng ký: {e}")
        return 'error'
    except Exception as e:
        print(f"Một lỗi không mong muốn đã xảy ra: {e}")
        return 'error'


def tai_anh_dai_dien(cookie, id_page, proxy, image_path):
    """Tải ảnh đại diện cho tài khoản Pro5."""
    cookie += f";i_user={id_page}"
    headers = {
        'authority': 'www.facebook.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
        'cookie': cookie,
        'origin': 'https://www.facebook.com',
        'referer': f'https://www.facebook.com/profile.php?id={id_page}',
        'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        'sec-ch-ua-full-version-list': '"Not.A/Brand";v="8.0.0.0", "Chromium";v="114.0.5735.134", "Google Chrome";v="114.0.5735.134"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-ch-ua-platform-version': '"15.0.0"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    }
    try:
        url_profile = requests.get('https://www.facebook.com/me', headers=headers, proxies=proxy, timeout=10).url
        profile = requests.get(url_profile, headers=headers, proxies=proxy, timeout=10).text
        try:
            fb_dtsg = profile.split('{"name":"fb_dtsg","value":"')[1].split('"},')[0]
        except:
            fb_dtsg = profile.split(',"f":"')[1].split('","l":null}')[0]
        params = {
            "profile_id": id_page,
            "photo_source": "57",
            "av": id_page,
            "__user": id_page,
            "__a": "1",
            "__req": "t",
            "__hs": "19524.HYP:comet_pkg.2.1..2.1",
            "dpr": "1",
            "__ccg": "GOOD",
            "__rev": "1007693839",
            "__comet_req": "15",
            "fb_dtsg": fb_dtsg,
            "__spin_r": "1007693839",
            "__spin_b": "trunk",
            "__spin_t": "1686891592"
        }

        jpg = open(image_path, "rb").read()  # Đọc ảnh từ đường dẫn đã lưu
        files = {'file': open(image_path, 'rb')}
        values = {"Content-Disposition": "form-data", "name": "file", "filename": image_path, # Use the path
                  "Content-Type": "image/jpeg"}
        headers['content-length'] = str(len(jpg))
        response = requests.post('https://www.facebook.com/profile/picture/upload/',
                                 params=params, headers=headers, data=values, files=files, proxies=proxy, timeout=10)
        json_response = json.loads(response.text.split('for (;;);')[1])
        id_avt = json_response['payload']['fbid']
        data = {
            'av': id_page,
            '__user': id_page,
            '__a': '1',
            '__req': '33',
            '__hs': '19524.HYP:comet_pkg.2.1..2.1',
            'dpr': '1',
            '__ccg': 'EXCELLENT',
            '__rev': '1007693839',
            '__comet_req': '15',
            'fb_dtsg': fb_dtsg,
            'jazoest': '25391',
            '__spin_r': '1007693839',
            '__spin_b': 'trunk',
            '__spin_t': '1686897074',
            'fb_api_caller_class': 'RelayModern',
            'fb_api_req_friendly_name': 'ProfileCometProfilePictureSetMutation',
            'variables': '{"input":{"attribution_id_v2":"ProfileCometTimelineListViewRoot.react,comet.profile.timeline.list,tap_bookmark,1686897073710,35114,' + id_page + '","caption":"","existing_photo_id":"' + id_avt + '","expiration_time":null,"profile_id":"' + id_page + '","profile_pic_method":"EXISTING","profile_pic_source":"TIMELINE","scaled_crop_rect":{"height":0.99999,"width":0.6686,"x":0.1657,"y":0},"skip_cropping":true,"actor_id":"' + id_page + '","client_mutation_id":"1"},"isPage":false,"isProfile":true,"sectionToken":"UNKNOWN","collectionToken":"UNKNOWN","scale":1}',
            'server_timestamps': 'true',
            'doc_id': '9390972637642235',
        }
        up = requests.post('https://www.facebook.com/api/graphql/', headers=headers, data=data, proxies=proxy, timeout=10)
        with open('uid_pro5.txt', 'a+') as save:
            save.write(f"{id_page}\n")
        return "success"
    except requests.exceptions.RequestException as e:
        print(f"Lỗi trong quá trình tải ảnh đại diện: {e}")
        return "error_avt"
    except Exception as e:
        print(f"Một lỗi không mong muốn đã xảy ra: {e}")
        return "error_avt"



# Telegram Bot Handlers
@bot.message_handler(commands=['start'])
def gui_loi_chao(message):
    """Gửi lời chào khi người dùng bắt đầu trò chuyện với bot."""
    bot.reply_to(message, "Chào mừng bạn! Sử dụng /regpg để bắt đầu quá trình đăng ký Pro5.")


@bot.message_handler(commands=['regpg'])
def lenh_regpg(message):
    """Xử lý lệnh /regpg để bắt đầu quá trình đăng ký."""
    chat_id = message.chat.id
    cookie_nguoi_dung[chat_id] = None  # Reset cookie
    so_luong_tai_khoan[chat_id] = None # Reset số lượng tài khoản
    thoi_gian_tre[chat_id] = None # Reset thời gian trễ
    anh_dai_dien_nguoi_dung[chat_id] = None # Reset ảnh đại diện

    bot.send_message(chat_id, "Vui lòng nhập cookie của bạn:")
    bot.register_next_step_handler(message, nhap_cookie)


def nhap_cookie(message):
    """Nhận cookie từ người dùng."""
    chat_id = message.chat.id
    cookie = message.text.strip()
    # Kiểm tra cookie trước khi lưu
    kiem_tra = kiem_tra_cookie(cookie)
    if kiem_tra == 'valid_ck':
        cookie_nguoi_dung[chat_id] = cookie
        bot.send_message(chat_id, "Cookie hợp lệ. Bây giờ hãy gửi ảnh đại diện cho các tài khoản Pro5 (gửi ảnh dưới dạng file):")
        bot.register_next_step_handler(message, nhap_anh_dai_dien)
    else:
        bot.send_message(chat_id, "Cookie không hợp lệ. Vui lòng nhập lại:")
        bot.register_next_step_handler(message, nhap_cookie) #Yêu cầu nhập lại cookie



def nhap_anh_dai_dien(message):
    """Nhận ảnh đại diện từ người dùng."""
    chat_id = message.chat.id
    if message.document:
        try:
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            duong_dan_anh = f"avt_{chat_id}.jpg" #Tạo tên file duy nhất cho mỗi user
            with open(duong_dan_anh, 'wb') as new_file:
                new_file.write(downloaded_file)
            anh_dai_dien_nguoi_dung[chat_id] = duong_dan_anh # Lưu đường dẫn ảnh
            bot.send_message(chat_id, "Đã nhận được ảnh đại diện. Vui lòng nhập số lượng tài khoản Pro5 bạn muốn tạo:")
            bot.register_next_step_handler(message, nhap_so_luong)

        except Exception as e:
            bot.send_message(chat_id, f"Lỗi khi tải ảnh đại diện: {e}")
            return
    else:
        bot.send_message(chat_id, "Vui lòng gửi ảnh dưới dạng file (document), không phải ảnh thông thường.")
        bot.register_next_step_handler(message, nhap_anh_dai_dien) #Yêu cầu gửi lại ảnh


def nhap_so_luong(message):
    """Nhận số lượng tài khoản từ người dùng."""
    chat_id = message.chat.id
    try:
        so_luong = int(message.text.strip())
        if so_luong > 0:
            so_luong_tai_khoan[chat_id] = so_luong
            bot.send_message(chat_id, "Vui lòng nhập thời gian trễ (delay) giữa mỗi lần tạo tài khoản (ví dụ: 10 cho 10 giây):")
            bot.register_next_step_handler(message, nhap_thoi_gian_tre)
        else:
            bot.send_message(chat_id, "Số lượng tài khoản phải lớn hơn 0. Vui lòng nhập lại:")
            bot.register_next_step_handler(message, nhap_so_luong)
    except ValueError:
        bot.send_message(chat_id, "Số lượng tài khoản không hợp lệ. Vui lòng nhập lại:")
        bot.register_next_step_handler(message, nhap_so_luong)


def nhap_thoi_gian_tre(message):
    """Nhận thời gian trễ từ người dùng."""
    chat_id = message.chat.id
    try:
        delay = int(message.text.strip())
        if delay >= 0:
            thoi_gian_tre[chat_id] = delay
            bot.send_message(chat_id, f"Đã đặt thời gian trễ là {delay} giây.")
            thuc_hien_dang_ky(chat_id) # Bắt đầu quá trình đăng ký
        else:
            bot.send_message(chat_id, "Thời gian trễ phải là một số không âm. Vui lòng nhập lại:")
            bot.register_next_step_handler(message, nhap_thoi_gian_tre)
    except ValueError:
        bot.send_message(chat_id, "Thời gian trễ không hợp lệ. Vui lòng nhập lại:")
        bot.register_next_step_handler(message, nhap_thoi_gian_tre)



def thuc_hien_dang_ky(chat_id):
    """Thực hiện quá trình đăng ký Pro5."""
    cookie = cookie_nguoi_dung.get(chat_id)
    so_luong = so_luong_tai_khoan.get(chat_id)
    delay = thoi_gian_tre.get(chat_id)
    image_path = anh_dai_dien_nguoi_dung.get(chat_id)

    if not cookie:
        bot.send_message(chat_id, "Cookie chưa được cung cấp. Vui lòng sử dụng /regpg lại.")
        return
    if not so_luong:
        bot.send_message(chat_id, "Số lượng tài khoản chưa được cung cấp. Vui lòng sử dụng /regpg lại.")
        return
    if not delay:
        bot.send_message(chat_id, "Thời gian trễ chưa được cung cấp. Vui lòng sử dụng /regpg lại.")
        return

    if not image_path:
        bot.send_message(chat_id, "Ảnh đại diện chưa được cung cấp. Vui lòng sử dụng /regpg lại.")
        return


    dem = 0
    for i in range(so_luong):
        proxy = lay_proxy() # Lấy proxy mới cho mỗi lần đăng ký
        if proxy:
          print(f"Sử dụng proxy: {proxy}")
        else:
          print("Không tìm thấy proxy hợp lệ. Tiếp tục không có proxy.")
          bot.send_message(chat_id, "Không tìm thấy proxy hợp lệ. Tiếp tục không có proxy.")

        uid_pro5 = dang_ky(cookie, proxy)
        if uid_pro5 == 'error_ck':
            bot.send_message(chat_id, "Cookie không hợp lệ.")
            break

        dem += 1
        if uid_pro5 == 'error':
            bot.send_message(chat_id, "Không thể đăng ký Pro5. Có thể bị giới hạn.")
            break

        UID = uid_pro5[0]
        ten = uid_pro5[1]
        bot.send_message(chat_id, f"[{dem}/{so_luong}] - Uid_Pro5: {UID}|{ten} - [{i+1}/{so_luong}]")
        ket_qua_tai_anh = tai_anh_dai_dien(cookie, UID, proxy, image_path)
        if ket_qua_tai_anh == 'error_avt':
            bot.send_message(chat_id, "Lỗi khi tải ảnh đại diện.")
            break

        bot.send_message(chat_id, f"Đã đăng ký tài khoản Pro5 thứ {dem}/{so_luong} thành công. Chờ {delay} giây...")
        sleep(delay) # Delay

    bot.send_message(chat_id, "Quá trình đăng ký Pro5 đã hoàn tất.")
    # Xóa ảnh sau khi dùng xong
    try:
        os.remove(image_path)
        print(f"Đã xóa file ảnh: {image_path}")
    except Exception as e:
        print(f"Lỗi khi xóa file ảnh: {e}")



# Khởi chạy bot
if __name__ == '__main__':
    print("Bot đã khởi động. Đang chờ lệnh...")
    bot.infinity_polling()