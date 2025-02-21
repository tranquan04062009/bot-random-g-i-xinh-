import requests, random, os
import datetime

# Kiểm tra ngày hết hạn
ngay_hien_tai = datetime.date.today()
ngay_muc_tieu = datetime.date(2025, 12, 25)
if ngay_hien_tai >= ngay_muc_tieu:
    exit("Dừng hoạt động")
else:
    print("Đang chạy...")

import threading
from threading import active_count
import urllib
import time
import telebot
from telebot import types

# Token cố định
TOKEN = "7903504769:AAEMX3AUeOgGXvHNMQ5x7T7XcewuK90quNQ"
bot = telebot.TeleBot(TOKEN)

so_luong_luong = 400  
luong_dang_chay = []
danh_sach_link = []
so_luot_thanh_cong = 0
so_luot_that_bai = 0
dang_chay = False
so_luong_link = 0
so_luot_muc_tieu = 0  

def tao_ban_phim():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('Gửi liên kết')
    btn2 = types.KeyboardButton('Bắt đầu tăng view')
    btn3 = types.KeyboardButton('Dừng tăng view')
    btn4 = types.KeyboardButton('Xem lượt view thành công')
    btn5 = types.KeyboardButton('Chạy lại')
    markup.add(btn1, btn2, btn3, btn4, btn5)
    return markup

@bot.message_handler(commands=['start'])
def bat_dau_tin_nhan(message):
    global danh_sach_link, so_luong_link, dang_chay, so_luot_thanh_cong, so_luot_that_bai
    danh_sach_link = []  
    so_luong_link = 0  
    so_luot_thanh_cong = 0
    so_luot_that_bai = 0
    dang_chay = False  
    bot.send_message(message.chat.id, "Chào mừng bạn đến với bot tăng view Telegram! 🧚‍♀️", reply_markup=tao_ban_phim())

@bot.message_handler(func=lambda message: message.text == 'Gửi liên kết')
def gui_lien_ket(message):
    global so_luong_link, dang_chay
    if dang_chay:
        dang_chay = False  
        bot.reply_to(message, "Đã dừng tăng view để nhận liên kết mới.")  
    bot.reply_to(message, "Vui lòng gửi liên kết.")
    bot.register_next_step_handler(message, luu_link)

def luu_link(message):
    global danh_sach_link, so_luong_link
    link = message.text
    danh_sach_link = [link] * 6  
    so_luong_link = 6
    bot.reply_to(message, "Liên kết đã được lưu, nhấn 'Bắt đầu tăng view' để tiếp tục.")

@bot.message_handler(func=lambda message: message.text == 'Bắt đầu tăng view')
def bat_dau_view(message):
    global dang_chay, so_luot_muc_tieu
    if not dang_chay:
        if len(danh_sach_link) == 6:
            bot.reply_to(message, "Bạn muốn tăng bao nhiêu lượt xem?")
            bot.register_next_step_handler(message, thiet_lap_muc_tieu)
        else:
            bot.reply_to(message, "Bạn cần gửi liên kết trước!")
    else:
        bot.reply_to(message, "Tăng view đang chạy.")

def thiet_lap_muc_tieu(message):
    global so_luot_muc_tieu, dang_chay
    try:
        so_luot_muc_tieu = int(message.text)
        dang_chay = True
        bot.reply_to(message, f"Bắt đầu tăng {so_luot_muc_tieu} lượt xem...")
        bat_dau()
    except ValueError:
        bot.reply_to(message, "Vui lòng nhập số hợp lệ.")

@bot.message_handler(func=lambda message: message.text == 'Dừng tăng view')
def dung_view(message):
    global dang_chay
    if dang_chay:
        dang_chay = False
        bot.reply_to(message, "Đã dừng tăng view.")
    else:
        bot.reply_to(message, "Hiện tại không có tiến trình nào đang chạy.")

@bot.message_handler(func=lambda message: message.text == 'Xem lượt view thành công')
def xem_thong_ke(message):
    bot.reply_to(message, f"Lượt xem thành công: {so_luot_thanh_cong}\nLượt xem thất bại: {so_luot_that_bai}")

@bot.message_handler(func=lambda message: message.text == 'Chạy lại')
def chay_lai(message):
    global danh_sach_link, so_luong_link, dang_chay, so_luot_thanh_cong, so_luot_that_bai
    danh_sach_link = []  
    so_luong_link = 0  
    so_luot_thanh_cong = 0
    so_luot_that_bai = 0
    dang_chay = False  
    bot.reply_to(message, "Gửi liên kết mới để tiếp tục.")

def tang_view(proxy):
    global so_luot_thanh_cong, so_luot_that_bai, dang_chay, so_luot_muc_tieu
    for link in danh_sach_link:
        if not dang_chay:
            break
        kenh = link.split('/')[3]
        id_tin_nhan = link.split('/')[4]
        if gui_luot_xem(kenh, id_tin_nhan, proxy):
            so_luot_thanh_cong += 1
            if so_luot_thanh_cong >= so_luot_muc_tieu:
                dang_chay = False
                bot.send_message(message.chat.id, f"Đã hoàn thành {so_luot_muc_tieu} lượt xem.", reply_markup=tao_ban_phim())
                break
        else:
            so_luot_that_bai += 1

def gui_luot_xem(kenh, id_tin_nhan, proxy):
    s = requests.Session()
    proxies = {'http': proxy, 'https': proxy}    
    try:
        a = s.get(f"https://t.me/{kenh}/{id_tin_nhan}", timeout=10, proxies=proxies)
        cookie = a.headers['set-cookie'].split(';')[0]
    except:
        return False

    try:
        i = s.get(f'https://t.me/v/?views={cookie}', timeout=10, proxies=proxies)
        if i.text == "true":
            return True
    except:
        return False

def lay_proxy():
    try:
        https = requests.get("https://api.proxyscrape.com/?request=displayproxies&proxytype=https&timeout=0").text
        http = requests.get("https://api.proxyscrape.com/?request=displayproxies&proxytype=http&timeout=0").text
        socks = requests.get("https://api.proxyscrape.com/?request=displayproxies&proxytype=socks5&timeout=0").text
    except Exception as e:
        print(e)
        return False    
    with open("proxies.txt", "w") as f:
        f.write(https + "\n" + http)    
    with open("socks.txt", "w") as f:
        f.write(socks)

def kiem_tra_proxy(proxy):
    try:
        tang_view(proxy)
    except:
        return False

def bat_dau():
    s = lay_proxy()
    if s == False:
        return    
    with open('proxies.txt', 'r') as f:
        proxies = f.readlines()
    for proxy in proxies:
        p = proxy.strip()
        if not p:
            continue
        while active_count() > so_luong_luong:
            pass
        thread = threading.Thread(target=kiem_tra_proxy, args=(p,))
        luong_dang_chay.append(thread)
        thread.start()    
    with open('socks.txt', 'r') as f:
        proxies = f.readlines()    
    for proxy in proxies:
        p = proxy.strip()
        if not p:
            continue
        while active_count() > so_luong_luong:
            pass
        pr = "socks5://" + p
        thread = threading.Thread(target=kiem_tra_proxy, args=(pr,))
        luong_dang_chay.append(thread)
        thread.start()

bot.polling()