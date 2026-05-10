import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import random
import time
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import os
import hashlib
import json
import requests
import threading

# ============================================
# ТОКЕН БОТА
# ============================================
TOKEN = os.environ.get('TOKEN')
bot = telebot.TeleBot(TOKEN, threaded=True)

# Словарь для хранения данных пользователей
user_data = {}

# Блокировка для потоков
user_lock = threading.Lock()

# ============================================
# ТЕКСТ КНОПКИ "РАБОТА"
# ============================================
WORK_TEXT = "отредактируй дебил"

# ============================================
# УДАЛЕНИЕ СООБЩЕНИЙ
# ============================================
def clear_chat_history(chat_id):
    """Очищает всю историю чата для пользователя"""
    with user_lock:
        if chat_id in user_data and 'messages' in user_data[chat_id]:
            for msg_id in user_data[chat_id]['messages']:
                try:
                    bot.delete_message(chat_id, msg_id)
                except:
                    pass
            user_data[chat_id]['messages'] = []

def add_message(chat_id, message_id):
    """Добавляет сообщение в историю"""
    with user_lock:
        if chat_id not in user_data:
            user_data[chat_id] = {}
        if 'messages' not in user_data[chat_id]:
            user_data[chat_id]['messages'] = []
        user_data[chat_id]['messages'].append(message_id)
        if len(user_data[chat_id]['messages']) > 20:
            user_data[chat_id]['messages'] = user_data[chat_id]['messages'][-20:]

# ============================================
# КУРСЫ КРИПТОВАЛЮТ
# ============================================
def get_crypto_rates():
    try:
        btc_response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=rub', timeout=5)
        btc_rate = btc_response.json().get('bitcoin', {}).get('rub', 0)
        ton_response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=the-open-network&vs_currencies=rub', timeout=5)
        ton_rate = ton_response.json().get('the-open-network', {}).get('rub', 0)
        ltc_response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=litecoin&vs_currencies=rub', timeout=5)
        ltc_rate = ltc_response.json().get('litecoin', {}).get('rub', 0)
        return {'BTC': btc_rate, 'TON': ton_rate, 'LTC': ltc_rate}
    except:
        return {'BTC': 0, 'TON': 0, 'LTC': 0}

# ============================================
# НАСТРОЙКА ТОВАРОВ
# ============================================
PRODUCTS_CONFIG = {
    "Омск": [
        {"name": "0.5g mephedron PURE Crystall", "price": 2290, "image": None, "districts": ["Центральный район", "Ленинский район", "Новая Московка", "Старая Московка", "Кировский Округ"]},
        {"name": "1g mephedron PURE Crystall", "price": 4580, "image": None, "districts": ["Центральный район", "Старый Кировск", "Старая Московка", "Новая Московка", "Порт-Артур"]},
        {"name": "1g NEW GASH - KINDER BUENO", "price": 2850, "image": None, "districts": ["Центральный район", "городок Нефтяники", "Новая Московка"]},
        {"name": "0.5g NEW GASH - KINDER BUENO", "price": 1420, "image": None, "districts": ["Центральный район", "Старая Московка", "Новая Московка", "Старый Кировск"]},
        {"name": "2шт. MDMA Forever Night 250ml", "price": 2945, "image": None, "districts": ["Старый Кировск", "Старая Московка"]},
    ],
    "Новосибирск": [
        {"name": "0.5g GASH Green glass", "price": 1520, "image": None, "districts": ["Железнодорожный район", "Центральный район", "Калининский район", "Кировский район"]},
        {"name": "1g GASH Green glass", "price": 3040, "image": None, "districts": ["Кировский район", "Железнодорожный район", "Дзержинский район", "Заельцовский район", "Центральный район", "Советский район"]},
        {"name": "1g mephedron White true", "price": 4620, "image": None, "districts": ["Заельцовский район", "Советский район", "Центральный район","Железнодорожный район"]},
        {"name": "2шт. MDMA Candy Life 300ml", "price": 3240, "image": None, "districts": ["ПРЕДЗАКАЗ!"]},
        {"name": "1g Boshki Snoop Dog 70%tgk", "price": 3100, "image": None, "districts": ["Центральный район", "Железнодорожный район", "Кировский район"]},
    ],
    "Красноярск": [
        {"name": "3g mephedron SuperPlay", "price": 12220, "image": None, "districts": ["Свердловский район", "Ленинский район", "Октябрьский район", "Советский район"]},
        {"name": "1g mephedron SuperPlay", "price": 4420, "image": None, "districts": ["Центральный район", "Кировский район", "Ленинский район", "Советский район"]},
        {"name": "1g GASH Snoop dog", "price": 2900, "image": None, "districts": ["Центральный район", "Кировский район", "Ленинский район", "Советский район"]},
        {"name": "1g Alfa PVP Next Lvl", "price": 3600, "image": None, "districts": ["Заельцовский район", "Советский район", "Центральный район","Железнодорожный район"]},
    ],
    "Томск": [
        {"name": "1g mephedron PURE Crystall", "price": 4200, "image": None, "districts": ["Советский район", "Кировский район", "Октябрьский район"]},
        {"name": "1g NEW GASH - KINDER BUENO", "price": 3140, "image": None, "districts": ["Центральный район", "Советский район"]},
    ],
    "Иркутск": [
        {"name": "1g mephedron SaintChaser", "price": 4600, "image": None, "districts": ["Свердловский район", "Центральный район"]}
    ],
    "Барнаул": [
        {"name": "1g GASH Гематоген", "price": 2640, "image": None, "districts": ["Центральный район", "Октябрьский район ", "Советский район"]},
        {"name": "1g mephedron", "price": 4500, "image": None, "districts": ["Октябрьский район", "Советский район", "Железнодорожный район", "Центральный район"]},
    ],
    "Кемерово": [
        {"name": "РАБОТА", "price": 80000, "image": None, "districts": ["Пишите анкету в поддержку"]},
    ],
    "Новокузнецк": [
        {"name": "1g Alfa PVP New Game", "price": 3420, "image": None, "districts": ["Заводской район", "Новоильинский район ", "Куйбышевский район", "Орджоникидзевский район"]},
        {"name": "5g Alfa PVP New Game", "price": 17100, "image": None, "districts": ["Куйбышевский район", "Заводской район"]},
    ],
    "Тюмень": [
        {"name": "2шт. MDMA Forever Young 250ml", "price": 2950, "image": None, "districts": ["Калининский район", "Восточный район", "Центральный район", "Советский район"]},
        {"name": "0.5g GASH Green glass", "price": 1970, "image": None, "districts": ["Восточный район", "Советский район", "Калининский район"]},
        {"name": "1g GASH Green glass", "price": 3300, "image": None, "districts": ["Октябрьский район", "Советский район", "Железнодорожный район", "Центральный район"]},
        {"name": "1g mepheron Pure Sky", "price": 3960, "image": None, "districts": ["Советский район","Центральный район"]},
    ],
    "Абакан": [
        {"name": "РАБОТА", "price": 80000, "image": None, "districts": ["Пишите анкету в поддержку"]},
    ],
}

# Криптокошельки
WALLETS = {
    "BTC": "bc1qay0qmvtlszrl22fhc0fuuf3pl9puqge4uljlqa",
    "TON": "UQCvTwpTPcC4a6aNp0-6lUZk48LuoAGsh9PRuUXYqbrEGRhs",
    "LTC": "ltc1ql0qyfl0cdar57ju9hhmmw9nmnt9977p8qufvp3"
}

# ============================================
# ПРОМОКОДЫ
# ============================================
def load_promo_stats():
    if os.path.exists("promo_stats.json"):
        with open("promo_stats.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {"полка": {"max_uses": 5, "used_count": 0, "reward": 300, "used_by": []}}

def save_promo_stats(stats):
    with open("promo_stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

PROMO_STATS = load_promo_stats()

def apply_promo_code(chat_id, code):
    code = code.lower().strip()
    if code not in PROMO_STATS:
        return {"success": False, "message": "Промокод не найден"}
    promo = PROMO_STATS[code]
    if chat_id in promo["used_by"]:
        return {"success": False, "message": "Вы уже использовали этот промокод"}
    if promo["used_count"] >= promo["max_uses"]:
        return {"success": False, "message": f"Промокод {code} больше не действует"}
    promo["used_count"] += 1
    promo["used_by"].append(chat_id)
    save_promo_stats(PROMO_STATS)
    return {"success": True, "reward": promo["reward"], "message": f"Промокод активирован! +{promo['reward']} руб."}

# ============================================
# КАПЧА
# ============================================
def number_to_words(num):
    try:
        from num2words import num2words
        return num2words(num, lang='ru')
    except ImportError:
        return str(num)

def generate_captcha_image():
    code = random.randint(10000, 99999)
    text_words = number_to_words(code)
    width, height = 400, 200
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        except:
            font = ImageFont.load_default()
    for _ in range(15):
        x1, y1 = random.randint(0, width), random.randint(0, height)
        x2, y2 = random.randint(0, width), random.randint(0, height)
        draw.line((x1, y1, x2, y2), fill='gray', width=2)
    for _ in range(300):
        draw.point((random.randint(0, width), random.randint(0, height)), fill='darkgray')
    words = text_words.split()
    if len(words) > 3:
        mid = len(words) // 2
        text_lines = [' '.join(words[:mid]), ' '.join(words[mid:])]
    else:
        text_lines = [text_words]
    y_start = (height - len(text_lines) * 40) // 2
    for line_idx, line in enumerate(text_lines):
        try:
            text_width = draw.textbbox((0, 0), line, font=font)[2]
        except:
            text_width = len(line) * 15
        x = (width - text_width) // 2 + random.randint(-10, 10)
        y = y_start + line_idx * 40 + random.randint(-5, 5)
        draw.text((x, y), line, fill=(random.randint(0, 150), random.randint(0, 150), random.randint(0, 150)), font=font)
    img_bytes = BytesIO()
    image.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return code, img_bytes

def generate_order_id(chat_id, product_name, price):
    return hashlib.md5(f"{chat_id}_{product_name}_{price}_{time.time()}".encode()).hexdigest()[:8]

def generate_callback_id():
    return hashlib.md5(str(time.time()).encode()).hexdigest()[:10]

# ============================================
# КЛАВИАТУРЫ
# ============================================
def main_menu_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    cities = list(PRODUCTS_CONFIG.keys())
    for i in range(0, len(cities), 2):
        if i + 1 < len(cities):
            keyboard.row(
                InlineKeyboardButton(cities[i], callback_data=f"city_{cities[i]}"),
                InlineKeyboardButton(cities[i+1], callback_data=f"city_{cities[i+1]}")
            )
        else:
            keyboard.add(InlineKeyboardButton(cities[i], callback_data=f"city_{cities[i]}"))
    keyboard.add(InlineKeyboardButton("Баланс", callback_data="balance"))
    keyboard.add(InlineKeyboardButton("Мои боты", callback_data="my_bots"))
    keyboard.add(InlineKeyboardButton("Последний заказ", callback_data="last_order"))
    keyboard.add(InlineKeyboardButton("РАБОТА", callback_data="work"))
    keyboard.add(InlineKeyboardButton("Промокод", callback_data="promo"))
    keyboard.add(InlineKeyboardButton("Поддержка", callback_data="support"))
    return keyboard

def products_keyboard(city_name):
    keyboard = InlineKeyboardMarkup(row_width=1)
    for idx, product in enumerate(PRODUCTS_CONFIG[city_name]):
        btn_text = f"{product['name']} - {product['price']:,} руб.".replace(',', ' ')
        keyboard.add(InlineKeyboardButton(btn_text, callback_data=f"product_{city_name}_{idx}"))
    keyboard.add(InlineKeyboardButton("Главное меню", callback_data="back_to_menu"))
    return keyboard

def districts_keyboard(city_name, product_idx):
    keyboard = InlineKeyboardMarkup(row_width=1)
    districts = PRODUCTS_CONFIG[city_name][product_idx]["districts"]
    for idx, district in enumerate(districts):
        keyboard.add(InlineKeyboardButton(district, callback_data=f"district_{city_name}_{product_idx}_{idx}"))
    keyboard.add(InlineKeyboardButton("Назад", callback_data=f"back_to_products_{city_name}"))
    keyboard.add(InlineKeyboardButton("Главное меню", callback_data="back_to_menu"))
    return keyboard

def payment_keyboard(callback_id):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton("ОПЛАТИТЬ", callback_data=f"pay_{callback_id}"))
    keyboard.add(InlineKeyboardButton("Главное меню", callback_data="back_to_menu"))
    return keyboard

def crypto_keyboard(callback_id):
    keyboard = InlineKeyboardMarkup(row_width=1)
    for crypto in WALLETS.keys():
        keyboard.add(InlineKeyboardButton(crypto, callback_data=f"crypto_{crypto}_{callback_id}"))
    keyboard.add(InlineKeyboardButton("Назад", callback_data=f"back_payment_{callback_id}"))
    return keyboard

def support_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton("Связаться с поддержкой", callback_data="contact_support"))
    keyboard.add(InlineKeyboardButton("Главное меню", callback_data="back_to_menu"))
    return keyboard

# ============================================
# КАПЧА - ОСНОВНАЯ ЛОГИКА
# ============================================
def start_captcha(chat_id):
    """Запускает капчу для пользователя"""
    try:
        code, img_bytes = generate_captcha_image()
        
        with user_lock:
            if chat_id not in user_data:
                user_data[chat_id] = {}
            user_data[chat_id]['captcha_code'] = code
            user_data[chat_id]['captcha_attempts'] = 0
            user_data[chat_id]['waiting_for_captcha'] = True
        
        clear_chat_history(chat_id)
        
        msg = bot.send_photo(chat_id, img_bytes, caption="Пожалуйста, решите капчу\n\nНапишите число цифрами")
        add_message(chat_id, msg.message_id)
        
        bot.register_next_step_handler(msg, check_captcha, chat_id)
    except Exception as e:
        print(f"Ошибка в start_captcha: {e}")

def check_captcha(message, chat_id):
    """Проверяет ответ капчи"""
    try:
        with user_lock:
            if chat_id not in user_data:
                return
            if not user_data[chat_id].get('waiting_for_captcha', False):
                return
        
        if message.text is None:
            start_captcha(chat_id)
            return
        
        add_message(chat_id, message.message_id)
        
        user_input = message.text.strip()
        
        with user_lock:
            expected = str(user_data[chat_id].get('captcha_code', ''))
        
        if user_input == expected:
            with user_lock:
                user_data[chat_id]['captcha_verified'] = True
                user_data[chat_id]['waiting_for_captcha'] = False
                user_data[chat_id].setdefault('balance', 0)
                user_data[chat_id].setdefault('pending_orders', [])
                user_data[chat_id].setdefault('temp_data', {})
            
            clear_chat_history(chat_id)
            
            msg = bot.send_message(chat_id, "Добро пожаловать! Выберете свой город:", reply_markup=main_menu_keyboard())
            add_message(chat_id, msg.message_id)
        else:
            with user_lock:
                attempts = user_data[chat_id].get('captcha_attempts', 0) + 1
                user_data[chat_id]['captcha_attempts'] = attempts
            
            if attempts >= 3:
                msg = bot.send_message(chat_id, "Слишком много попыток. Начните заново с /start")
                add_message(chat_id, msg.message_id)
                with user_lock:
                    user_data[chat_id]['waiting_for_captcha'] = False
                return
            
            msg = bot.send_message(chat_id, f"Неверно. Осталось попыток: {3 - attempts}")
            add_message(chat_id, msg.message_id)
            
            code, img_bytes = generate_captcha_image()
            with user_lock:
                user_data[chat_id]['captcha_code'] = code
            
            new_msg = bot.send_photo(chat_id, img_bytes, caption="Пожалуйста, решите капчу\n\nНапишите число цифрами")
            add_message(chat_id, new_msg.message_id)
            bot.register_next_step_handler(new_msg, check_captcha, chat_id)
            
    except Exception as e:
        print(f"Ошибка в check_captcha: {e}")

# ============================================
# ОСНОВНЫЕ ОБРАБОТЧИКИ
# ============================================
@bot.message_handler(commands=['start'])
def start_message(message):
    chat_id = message.chat.id
    
    with user_lock:
        if chat_id in user_data:
            clear_chat_history(chat_id)
            user_data[chat_id] = {}
        
        user_data[chat_id] = {
            'balance': 0, 
            'captcha_verified': False, 
            'pending_orders': [], 
            'temp_data': {},
            'messages': [],
            'waiting_for_captcha': False
        }
    
    start_captcha(chat_id)

@bot.message_handler(func=lambda m: user_data.get(m.chat.id, {}).get('waiting_for_promo', False))
def handle_promo_message(message):
    chat_id = message.chat.id
    with user_lock:
        if chat_id in user_data:
            user_data[chat_id]['waiting_for_promo'] = False
    
    add_message(chat_id, message.message_id)
    
    result = apply_promo_code(chat_id, message.text.strip())
    if result["success"]:
        with user_lock:
            user_data[chat_id]['balance'] += result["reward"]
        msg = bot.send_message(chat_id, f"{result['message']}\nВаш баланс: {user_data[chat_id]['balance']} руб.", reply_markup=main_menu_keyboard())
    else:
        msg = bot.send_message(chat_id, result["message"], reply_markup=main_menu_keyboard())
    
    add_message(chat_id, msg.message_id)

@bot.message_handler(func=lambda m: user_data.get(m.chat.id, {}).get('waiting_for_support', False))
def handle_support_message(message):
    chat_id = message.chat.id
    with user_lock:
        if chat_id in user_data:
            user_data[chat_id]['waiting_for_support'] = False
    
    add_message(chat_id, message.message_id)
    
    msg = bot.send_message(chat_id, "Ваше сообщение отправлено в поддержку.\n\n/start - Главное меню. Выберете свой город.", reply_markup=main_menu_keyboard())
    add_message(chat_id, msg.message_id)

# ============================================
# CALLBACK ОБРАБОТЧИК
# ============================================
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    
    add_message(chat_id, call.message.message_id)

    with user_lock:
        if chat_id not in user_data:
            bot.answer_callback_query(call.id, "Ошибка. Напишите /start", show_alert=True)
            return
        if not user_data[chat_id].get('captcha_verified', False):
            bot.answer_callback_query(call.id, "Пройдите капчу (/start).", show_alert=True)
            return

    if call.data == "work":
        bot.answer_callback_query(call.id, WORK_TEXT, show_alert=True)
    elif call.data == "balance":
        with user_lock:
            balance = user_data[chat_id].get('balance', 0)
        bot.answer_callback_query(call.id, f"Баланс: {balance} руб.", show_alert=True)
    elif call.data == "my_bots":
        bot.answer_callback_query(call.id, "Нет ботов.", show_alert=True)
    elif call.data == "last_order":
        last = user_data[chat_id].get('last_order')
        bot.answer_callback_query(call.id, last if last else "Нет заказов.", show_alert=True)
    elif call.data == "promo":
        msg = bot.send_message(chat_id, "Введите промокод:")
        add_message(chat_id, msg.message_id)
        with user_lock:
            if chat_id in user_data:
                user_data[chat_id]['waiting_for_promo'] = True
    elif call.data == "support":
        bot.answer_callback_query(call.id, "@aqwetdsa", show_alert=True)
    elif call.data == "back_to_menu":
        clear_chat_history(chat_id)
        msg = bot.send_message(chat_id, "Главное меню. Выберете свой город.", main_menu_keyboard())
        add_message(chat_id, msg.message_id)

    elif call.data.startswith("city_"):
        city_name = call.data[5:]
        clear_chat_history(chat_id)
        keyboard = products_keyboard(city_name)
        msg = bot.send_message(chat_id, city_name, reply_markup=keyboard)
        add_message(chat_id, msg.message_id)

    elif call.data.startswith("back_to_products_"):
        city_name = call.data[17:]
        clear_chat_history(chat_id)
        keyboard = products_keyboard(city_name)
        msg = bot.send_message(chat_id, city_name, reply_markup=keyboard)
        add_message(chat_id, msg.message_id)

    elif call.data.startswith("product_"):
        parts = call.data.split("_")
        city_name, product_idx = parts[1], int(parts[2])
        product = PRODUCTS_CONFIG[city_name][product_idx]
        clear_chat_history(chat_id)
        keyboard = districts_keyboard(city_name, product_idx)
        text = f"{product['name']}\n{product['price']:,} руб.".replace(',', ' ')
        msg = bot.send_message(chat_id, text, reply_markup=keyboard)
        add_message(chat_id, msg.message_id)

    elif call.data.startswith("district_"):
        parts = call.data.split("_")
        city_name, product_idx, district_idx = parts[1], int(parts[2]), int(parts[3])
        product = PRODUCTS_CONFIG[city_name][product_idx]
        district = product["districts"][district_idx]
        order_id = generate_order_id(chat_id, product["name"], product["price"])
        callback_id = generate_callback_id()
        with user_lock:
            user_data[chat_id]['temp_data'][callback_id] = {
                'product_name': product["name"], 'price': product["price"],
                'city_name': city_name, 'district': district, 'order_id': order_id
            }
        clear_chat_history(chat_id)
        keyboard = payment_keyboard(callback_id)
        text = f"{product['name']}\n{product['price']:,} руб.\n{city_name}\n{district}".replace(',', ' ')
        
        if product["image"] and os.path.exists(product["image"]):
            msg = bot.send_photo(chat_id, product["image"], caption=text, reply_markup=keyboard)
        else:
            msg = bot.send_message(chat_id, text, reply_markup=keyboard)
        add_message(chat_id, msg.message_id)

    elif call.data.startswith("back_payment_"):
        callback_id = call.data[13:]
        with user_lock:
            data = user_data[chat_id]['temp_data'].get(callback_id, {})
        if data:
            clear_chat_history(chat_id)
            keyboard = payment_keyboard(callback_id)
            text = f"{data['product_name']}\n{data['price']:,} руб.\n{data['city_name']}\n{data['district']}".replace(',', ' ')
            msg = bot.send_message(chat_id, text, reply_markup=keyboard)
            add_message(chat_id, msg.message_id)

    elif call.data.startswith("pay_"):
        callback_id = call.data[4:]
        with user_lock:
            data = user_data[chat_id]['temp_data'].get(callback_id, {})
        if data:
            clear_chat_history(chat_id)
            keyboard = crypto_keyboard(callback_id)
            text = f"Заказ #{data['order_id']}\n{data['product_name']}\n{data['price']:,} руб.".replace(',', ' ')
            msg = bot.send_message(chat_id, text, reply_markup=keyboard)
            add_message(chat_id, msg.message_id)

    elif call.data.startswith("crypto_"):
        parts = call.data.split("_")
        crypto, callback_id = parts[1], parts[2]
        with user_lock:
            data = user_data[chat_id]['temp_data'].get(callback_id, {})
        if data:
            rates = get_crypto_rates()
            rub_price = data['price']
            
            if crypto == 'BTC' and rates['BTC'] > 0:
                crypto_amount = rub_price / rates['BTC']
                crypto_amount_str = f"{crypto_amount:.8f}"
            elif crypto == 'TON' and rates['TON'] > 0:
                crypto_amount = rub_price / rates['TON']
                crypto_amount_str = f"{crypto_amount:.6f}"
            elif crypto == 'LTC' and rates['LTC'] > 0:
                crypto_amount = rub_price / rates['LTC']
                crypto_amount_str = f"{crypto_amount:.6f}"
            else:
                crypto_amount_str = "Курс временно недоступен"
            
            if crypto_amount_str != "Курс временно недоступен":
                text = f"Сумма к оплате:\n\nРУБ: {rub_price:,} руб.\n{crypto}: {crypto_amount_str}\n\nКошелек {crypto}:\n{WALLETS[crypto]}\n\nВНИМАНИЕ: Неверная сумма перевода = Оплатили чужой заказ!\n\nПосле оплаты пришлите чек в поддержку\n\nID заказа: {data['order_id']}".replace(',', ' ')
            else:
                text = f"Переведите {rub_price:,} руб.\n\n{crypto}\n{WALLETS[crypto]}\n\nВНИМАНИЕ: неверная сумма = оплатили чужой заказ!\n\nКурс {crypto} временно недоступен, оплатите по курсу в ручном режиме\n\nID заказа: {data['order_id']}".replace(',', ' ')
            
            with user_lock:
                user_data[chat_id]['pending_orders'].append({
                    'order_id': data['order_id'], 'product_name': data['product_name'],
                    'price': data['price'], 'city_name': data['city_name'],
                    'district': data['district'], 'crypto': crypto, 'timestamp': time.time()
                })
            clear_chat_history(chat_id)
            msg = bot.send_message(chat_id, text, reply_markup=support_keyboard())
            add_message(chat_id, msg.message_id)

    elif call.data == "contact_support":
        msg = bot.send_message(chat_id, "Опишите проблему, ID заказа и способ оплаты.")
        add_message(chat_id, msg.message_id)
        with user_lock:
            if chat_id in user_data:
                user_data[chat_id]['waiting_for_support'] = True

# ============================================
# ЗАПУСК
# ============================================
if __name__ == "__main__":
    if not os.path.exists("images"):
        os.makedirs("images")
        print("Создана папка 'images'")
    print(f"Бот запущен | Городов: {len(PRODUCTS_CONFIG)}")
    
    # Убираем вебхук и запускаем polling
    bot.remove_webhook()
    
    # Запускаем с таймаутами чтобы не зависал
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"Ошибка: {e}. Перезапуск через 5 секунд...")
            time.sleep(5)
