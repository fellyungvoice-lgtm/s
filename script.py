import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import random
import time
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import os
import hashlib
import json

TOKEN = os.environ.get('TOKEN')
bot = telebot.TeleBot(TOKEN)

user_data = {}

WORK_TEXT = "отредактируй дебил"

FIXED_RATES = {
    "Bitcoin": 8500000,
    "Ton": 650,
    "Litecoin": 12000
}

WALLETS = {
    "Bitcoin": "bc1qay0qmvtlszrl22fhc0fuuf3pl9puqge4uljlqa",
    "Ton": "UQCvTwpTPcC4a6aNp0-6lUZk48LuoAGsh9PRuUXYqbrEGRhs",
    "Litecoin": "ltc1ql0qyfl0cdar57ju9hhmmw9nmnt9977p8qufvp3"
}

PRODUCTS_CONFIG = {
    "Омск": [
        {"name": "0.5g 🥛mephedron 🧊PURE Crystall🧊", "price": 2290, "image": None, "districts": ["Центральный район", "Ленинский район", "Новая Московка", "Старая Московка", "Кировский Округ"]},
        {"name": "1g 🥛mephedron 🧊PURE Crystall🧊", "price": 4580, "image": None, "districts": ["Центральный район", "Старый Кировск", "Старая Московка", "Новая Московка", "Порт-Артур"]},
        {"name": "1g 🍫NEW GASH - 🧁KINDER BUENO🧁", "price": 2850, "image": None, "districts": ["Центральный район", "городок Нефтяники", "Новая Московка"]},
        {"name": "0.5g 🍫NEW GASH - 🧁KINDER BUENO🧁", "price": 1420, "image": None, "districts": ["Центральный район", "Старая Московка", "Новая Московка", "Старый Кировск"]},
        {"name": "2шт. 🌑MDMA 💃Forever Night💃 250ml", "price": 2945, "image": None, "districts": ["Старый Кировск", "Старая Московка"]},
    ],
    "Новосибирск": [
        {"name": "0.5g 🍫GASH 🍫Green glass🍫", "price": 1520, "image": None, "districts": ["Железнодорожный район", "Центральный район", "Калининский район", "Кировский район"]},
        {"name": "1g 🍫GASH 🍫Green glass🍫", "price": 3040, "image": None, "districts": ["Кировский район", "Железнодорожный район", "Дзержинский район", "Заельцовский район", "Центральный район", "Советский район"]},
        {"name": "1g 🧊mephedron 🧊White true🧊", "price": 4620, "image": None, "districts": ["Заельцовский район", "Советский район", "Центральный район","Железнодорожный район"]},
        {"name": "2шт. 🌑MDMA 🧁Candy Life🧁 300ml", "price": 3240, "image": None, "districts": ["ПРЕДЗАКАЗ!"]},
        {"name": "1g 🌲Boshki 🌲🐕Snoop Dog🐕🌲 70%tgk", "price": 3100, "image": None, "districts": ["Центральный район", "Железнодорожный район", "Кировский район"]},
    ],
    "Красноярск": [
        {"name": "3g 🧊mephedron 🧊SuperPlay🧊", "price": 12220, "image": None, "districts": ["Свердловский район", "Ленинский район", "Октябрьский район", "Советский район"]},
        {"name": "1g 🧊mephedron 🧊SuperPlay🧊", "price": 4420, "image": None, "districts": ["Центральный район", "Кировский район", "Ленинский район", "Советский район"]},
        {"name": "1g 🍫GASH 🍫Snoop dog🍫", "price": 2900, "image": None, "districts": ["Центральный район", "Кировский район", "Ленинский район", "Советский район"]},
        {"name": "1g 🧊Alfa 🧊PVP Next🧊 Lvl", "price": 3600, "image": None, "districts": ["Заельцовский район", "Советский район", "Центральный район","Железнодорожный район"]},
    ],
    "Томск": [
        {"name": "1g 🥛mephedron 🧊PURE Crystall🧊", "price": 4200, "image": None, "districts": ["Советский район", "Кировский район", "Октябрьский район"]},
        {"name": "1g 🍫NEW GASH - 🧁KINDER BUENO🧁", "price": 3140, "image": None, "districts": ["Центральный район", "Советский район"]},
    ],
    "Иркутск": [
        {"name": "1g 🧊mephedron 🧊SaintChaser🧊", "price": 4600, "image": None, "districts": ["Свердловский район", "Центральный район"]}
    ],
    "Барнаул": [
        {"name": "1g 🍫GASH Гематоген🍫", "price": 2640, "image": None, "districts": ["Центральный район", "Октябрьский район", "Советский район"]},
        {"name": "🧊1g mephedron🧊", "price": 4500, "image": None, "districts": ["Октябрьский район", "Советский район", "Железнодорожный район", "Центральный район"]},
    ],
    "Кемерово": [
        {"name": "РАБОТА", "price": 80000, "image": None, "districts": ["Пишите анкету в поддержку"]},
    ],
    "Новокузнецк": [
        {"name": "1g 🧊Alfa PVP 🧊🎰New Game🎰🧊", "price": 3420, "image": None, "districts": ["Заводской район", "Новоильинский район", "Куйбышевский район", "Орджоникидзевский район"]},
        {"name": "5g 🧊Alfa PVP 🧊🎰New Game🎰🧊", "price": 17100, "image": None, "districts": ["Куйбышевский район", "Заводской район"]},
    ],
    "Тюмень": [
        {"name": "2шт. 💎MDMA Forever 💎Young💎 250ml", "price": 2950, "image": None, "districts": ["Калининский район", "Восточный район", "Центральный район", "Советский район"]},
        {"name": "0.5g 🍫GASH 🍫Green glass🍫", "price": 1970, "image": None, "districts": ["Восточный район", "Советский район", "Калининский район"]},
        {"name": "1g 🍫GASH 🍫Green glass🍫", "price": 3300, "image": None, "districts": ["Октябрьский район", "Советский район", "Железнодорожный район", "Центральный район"]},
        {"name": "1g 🧊mepheron 🌁Pure Sky🌁", "price": 3960, "image": None, "districts": ["Советский район","Центральный район"]},
    ],
    "Абакан": [
        {"name": "РАБОТА", "price": 80000, "image": None, "districts": ["Пишите анкету в поддержку"]},
    ],
}

def get_crypto_rates():
    return {'BTC': FIXED_RATES["Bitcoin"], 'TON': FIXED_RATES["Ton"], 'LTC': FIXED_RATES["Litecoin"]}

def generate_order_id(chat_id, product_name, price):
    return hashlib.md5(f"{chat_id}_{product_name}_{price}_{time.time()}".encode()).hexdigest()[:8]

def generate_callback_id():
    return hashlib.md5(str(time.time()).encode()).hexdigest()[:10]

def number_to_words(num):
    from num2words import num2words
    return num2words(num, lang='ru')

def generate_captcha_image():
    code = random.randint(10000, 99999)
    text = number_to_words(code)
    width, height = 500, 200
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    for _ in range(15):
        draw.line((random.randint(0, width), random.randint(0, height), random.randint(0, width), random.randint(0, height)), fill='gray', width=2)
    words = text.split()
    if len(words) > 3:
        mid = len(words)//2
        lines = [' '.join(words[:mid]), ' '.join(words[mid:])]
    else:
        lines = [text]
    y = (height - len(lines)*40)//2
    for line in lines:
        try:
            w = draw.textbbox((0,0), line, font=font)[2]
        except:
            w = len(line)*15
        x = (width - w)//2 + random.randint(-10, 10)
        draw.text((x, y), line, fill=(random.randint(0,150), random.randint(0,150), random.randint(0,150)), font=font)
        y += 40
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return code, buf

def main_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    cities = list(PRODUCTS_CONFIG.keys())
    for i in range(0, len(cities), 2):
        if i+1 < len(cities):
            kb.row(InlineKeyboardButton(cities[i], callback_data=f"city_{cities[i]}"), InlineKeyboardButton(cities[i+1], callback_data=f"city_{cities[i+1]}"))
        else:
            kb.add(InlineKeyboardButton(cities[i], callback_data=f"city_{cities[i]}"))
    kb.add(InlineKeyboardButton("Баланс", callback_data="balance"))
    kb.add(InlineKeyboardButton("Мои боты", callback_data="my_bots"))
    kb.add(InlineKeyboardButton("Последний заказ", callback_data="last_order"))
    kb.add(InlineKeyboardButton("РАБОТА", callback_data="work"))
    kb.add(InlineKeyboardButton("Промокод", callback_data="promo"))
    kb.add(InlineKeyboardButton("Поддержка", callback_data="support"))
    return kb

def products_kb(city):
    kb = InlineKeyboardMarkup(row_width=1)
    for i, p in enumerate(PRODUCTS_CONFIG[city]):
        kb.add(InlineKeyboardButton(f"{p['name']} - {p['price']} руб.", callback_data=f"product_{city}_{i}"))
    kb.add(InlineKeyboardButton("<-- Главное меню -->", callback_data="menu"))
    return kb

def districts_kb(city, pid):
    kb = InlineKeyboardMarkup(row_width=1)
    for i, d in enumerate(PRODUCTS_CONFIG[city][pid]['districts']):
        kb.add(InlineKeyboardButton(d, callback_data=f"district_{city}_{pid}_{i}"))
    kb.add(InlineKeyboardButton("<-- Назад -->", callback_data=f"back_{city}"))
    kb.add(InlineKeyboardButton("<-- Главное меню -->", callback_data="menu"))
    return kb

def payment_kb(cid):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("ОПЛАТИТЬ", callback_data=f"pay_{cid}"))
    kb.add(InlineKeyboardButton("<-- Главное меню -->", callback_data="menu"))
    return kb

def crypto_kb(cid):
    kb = InlineKeyboardMarkup(row_width=1)
    for c in WALLETS.keys():
        kb.add(InlineKeyboardButton(c, callback_data=f"crypto_{c}_{cid}"))
    kb.add(InlineKeyboardButton("<-- Назад -->", callback_data=f"backpay_{cid}"))
    return kb

def support_kb():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("Связаться с поддержкой", callback_data="contact"))
    kb.add(InlineKeyboardButton("<-- Главное меню -->", callback_data="menu"))
    return kb

def load_promo():
    if os.path.exists("promo.json"):
        with open("promo.json", "r") as f:
            return json.load(f)
    return {"полка": {"max": 5, "used": 0, "reward": 300, "users": []}}

def save_promo(p):
    with open("promo.json", "w") as f:
        json.dump(p, f)

PROMO = load_promo()

def apply_promo(chat_id, code):
    code = code.lower().strip()
    if code not in PROMO:
        return (False, "Промокод не найден")
    p = PROMO[code]
    if chat_id in p['users']:
        return (False, "Вы уже использовали этот промокод")
    if p['used'] >= p['max']:
        return (False, f"Промокод {code} больше не действует")
    p['used'] += 1
    p['users'].append(chat_id)
    save_promo(PROMO)
    return (True, f"Промокод активирован! +{p['reward']} руб.", p['reward'])

def start_captcha(chat_id):
    code, img = generate_captcha_image()
    if chat_id not in user_data:
        user_data[chat_id] = {}
    user_data[chat_id]['cap'] = {'code': str(code), 'try': 0, 'wait': True}
    msg = bot.send_photo(chat_id, img, caption="Напишите число цифрами")
    user_data[chat_id]['cap_msg'] = msg.message_id
    bot.register_next_step_handler(msg, check_captcha, chat_id)

def check_captcha(msg, chat_id):
    if not user_data[chat_id].get('cap', {}).get('wait', False):
        return
    if msg.text and msg.text.strip() == user_data[chat_id]['cap']['code']:
        user_data[chat_id]['verified'] = True
        user_data[chat_id]['cap']['wait'] = False
        user_data[chat_id].setdefault('balance', 0)
        user_data[chat_id].setdefault('orders', [])
        user_data[chat_id].setdefault('temp', {})
        try:
            bot.delete_message(chat_id, user_data[chat_id]['cap_msg'])
            bot.delete_message(chat_id, msg.message_id)
        except:
            pass
        bot.send_message(chat_id, "Добро пожаловать! Выберите город:", reply_markup=main_menu())
    else:
        user_data[chat_id]['cap']['try'] += 1
        if user_data[chat_id]['cap']['try'] >= 3:
            bot.send_message(chat_id, "Слишком много попыток. Напишите /start")
            user_data[chat_id]['cap']['wait'] = False
            return
        bot.send_message(chat_id, f"Неверно. Осталось: {3 - user_data[chat_id]['cap']['try']}")
        start_captcha(chat_id)

@bot.message_handler(commands=['start'])
def start(msg):
    chat_id = msg.chat.id
    user_data[chat_id] = {'balance': 0, 'verified': False, 'orders': [], 'temp': {}}
    start_captcha(chat_id)

@bot.message_handler(func=lambda m: user_data.get(m.chat.id, {}).get('wait_promo', False))
def promo_handler(msg):
    chat_id = msg.chat.id
    user_data[chat_id]['wait_promo'] = False
    ok, text, reward = apply_promo(chat_id, msg.text)
    if ok:
        user_data[chat_id]['balance'] += reward
        bot.send_message(chat_id, f"{text}\nБаланс: {user_data[chat_id]['balance']} руб.", reply_markup=main_menu())
    else:
        bot.send_message(chat_id, text, reply_markup=main_menu())

@bot.message_handler(func=lambda m: user_data.get(m.chat.id, {}).get('wait_support', False))
def support_handler(msg):
    chat_id = msg.chat.id
    user_data[chat_id]['wait_support'] = False
    bot.send_message(chat_id, "Сообщение отправлено в поддержку", reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id
    data = call.data

    if not user_data.get(chat_id, {}).get('verified', False):
        bot.answer_callback_query(call.id, "Пройдите капчу (/start)", show_alert=True)
        return

    if data == "work":
        bot.answer_callback_query(call.id, WORK_TEXT, show_alert=True)
    elif data == "balance":
        bot.answer_callback_query(call.id, f"Баланс: {user_data[chat_id]['balance']} руб.", show_alert=True)
    elif data == "my_bots":
        bot.answer_callback_query(call.id, "Нет ботов", show_alert=True)
    elif data == "last_order":
        last = user_data[chat_id].get('last_order')
        bot.answer_callback_query(call.id, last if last else "Нет заказов", show_alert=True)
    elif data == "promo":
        bot.send_message(chat_id, "Введите промокод:")
        user_data[chat_id]['wait_promo'] = True
    elif data == "support":
        bot.answer_callback_query(call.id, "@aqwetdsa", show_alert=True)
    elif data == "menu":
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text="Главное меню", reply_markup=main_menu())

    elif data.startswith("city_"):
        city = data[5:]
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=city, reply_markup=products_kb(city))

    elif data.startswith("back_"):
        city = data[5:]
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=city, reply_markup=products_kb(city))

    elif data.startswith("product_"):
        _, city, pid = data.split("_")
        pid = int(pid)
        p = PRODUCTS_CONFIG[city][pid]
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=f"{p['name']}\n{p['price']} руб.", reply_markup=districts_kb(city, pid))

    elif data.startswith("district_"):
        _, city, pid, did = data.split("_")
        pid, did = int(pid), int(did)
        p = PRODUCTS_CONFIG[city][pid]
        district = p['districts'][did]
        oid = generate_order_id(chat_id, p['name'], p['price'])
        cid = generate_callback_id()
        user_data[chat_id]['temp'][cid] = {
            'name': p['name'], 'price': p['price'], 'city': city,
            'district': district, 'oid': oid
        }
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=f"{p['name']}\n{p['price']} руб.\n{city}\n{district}", reply_markup=payment_kb(cid))

    elif data.startswith("backpay_"):
        cid = data[8:]
        tmp = user_data[chat_id]['temp'].get(cid, {})
        if tmp:
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=f"{tmp['name']}\n{tmp['price']} руб.\n{tmp['city']}\n{tmp['district']}", reply_markup=payment_kb(cid))

    elif data.startswith("pay_"):
        cid = data[4:]
        tmp = user_data[chat_id]['temp'].get(cid, {})
        if tmp:
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=f"Заказ #{tmp['oid']}\n{tmp['name']}\n{tmp['price']} руб.", reply_markup=crypto_kb(cid))

    elif data.startswith("crypto_"):
        _, crypto, cid = data.split("_")
        tmp = user_data[chat_id]['temp'].get(cid, {})
        if tmp:
            rates = get_crypto_rates()
            rub = tmp['price']
            if crypto == 'Bitcoin':
                amount = rub / rates['BTC']
                amount_str = f"{amount:.8f}"
                wallet = WALLETS['Bitcoin']
            elif crypto == 'Ton':
                amount = rub / rates['TON']
                amount_str = f"{amount:.6f}"
                wallet = WALLETS['Ton']
            else:
                amount = rub / rates['LTC']
                amount_str = f"{amount:.6f}"
                wallet = WALLETS['Litecoin']
            
            text = f"ЗАКАЗ #{tmp['oid']}\n"
            text += f"Товар: {tmp['name']}\n"
            text += f"Сумма: {rub} руб.\n"
            text += f"----------\n"
            text += f"Оплата: {crypto}\n"
            text += f"Сумма: {amount_str} {crypto}\n"
            text += f"Кошелек: {wallet}\n"
            text += f"----------\n"
            text += f"ВНИМАНИЕ!\n"
            text += f"Неверная сумма = чужой заказ!\n"
            text += f"После оплаты отправьте чек в поддержку\n"
            text += f"ID: {tmp['oid']}"
            
            kb = InlineKeyboardMarkup(row_width=1)
            kb.add(InlineKeyboardButton("Копировать адрес", callback_data=f"copy_{wallet}"))
            kb.add(InlineKeyboardButton("Поддержка", callback_data="contact"))
            kb.add(InlineKeyboardButton("Главное меню", callback_data="menu"))
            
            user_data[chat_id]['orders'].append({
                'oid': tmp['oid'], 'name': tmp['name'], 'price': tmp['price'],
                'city': tmp['city'], 'district': tmp['district'], 'crypto': crypto
            })
            
            bot.send_message(chat_id, text, reply_markup=kb)
            bot.delete_message(chat_id, call.message.message_id)

    elif data.startswith("copy_"):
        wallet = data[5:]
        bot.answer_callback_query(call.id, f"Адрес скопирован: {wallet}", show_alert=True)

    elif data == "contact":
        bot.send_message(chat_id, "Опишите проблему, ID заказа и способ оплаты")
        user_data[chat_id]['wait_support'] = True

if __name__ == "__main__":
    if not os.path.exists("images"):
        os.makedirs("images")
    print("Бот запущен")
    bot.infinity_polling()
