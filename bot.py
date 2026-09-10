import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timezone, timedelta
import json
import os

TOKEN = "8842143426:AAEt-8OhhfrpmDeN1ibXyn3DYYGb2tCqTvs"
ADMIN_ID = 8832347891
CHANNEL_USERNAME = "@TURSE_INFO"

bot = telebot.TeleBot(TOKEN)
DATA_FILE = "bot_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {
        "points": {},
        "last_bonus": {},
        "last_free": {},
        "used_codes": {},
        "invited": {},
        "vip": {}
    }

def save_data():
    data = {
        "points": user_points,
        "last_bonus": last_bonus_date,
        "last_free": last_free_date,
        "used_codes": used_codes_data,
        "invited": invited_counts,
        "vip": vip_users
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

db = load_data()
user_points = {int(k): v for k, v in db.get("points", {}).items()}
last_bonus_date = {int(k): v for k, v in db.get("last_bonus", {}).items()}
last_free_date = {int(k): v for k, v in db.get("last_free", {}).items()}
used_codes_data = {int(k): v for k, v in db.get("used_codes", {}).items()}
invited_counts = {int(k): v for k, v in db.get("invited", {}).items()}
vip_users = {int(k): v for k, v in db.get("vip", {}).items()}

user_states = {}
user_temp_data = {}
iraq_tz = timezone(timedelta(hours=3))

def check_user_membership(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
    except:
        return True  
    return False

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    
    if not check_user_membership(user_id):
        show_force_sub_message(message.chat.id)
        return

    if user_id not in user_points:
        user_points[user_id] = 1000
        save_data()
        
    user_states[user_id] = None
    show_main_menu(message.chat.id, message.message_id if hasattr(message, 'message_id') else None, is_new=True)

def show_force_sub_message(chat_id):
    text = (
        "⚠️ **بۆ بەکارئینانا بۆتی، پێدڤیە بەری هەر شتەکی جۆینێ کەناڵا مە ببی!**\n\n"
        "👇 تکایە سەرەتا جۆینێ کەناڵی بکە، پاشان دوگمەیا (پشکنینا جۆینبوونێ) کلیک بکە:"
    )
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("JOIN 🌐", url="https://t.me/TURSE_INFO"))
    markup.add(InlineKeyboardButton("✅ پشکنینا جۆینبوونێ (Check)", callback_data="check_membership"))
    bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")

def show_main_menu(chat_id, message_id=None, is_new=False):
    user_id = chat_id
    points = user_points.get(user_id, 1000)
    
    text = (
        "💎 - بەخێرهاتن بۆ بۆتا دەنگدانا کوردی\n"
        f"💰 - پۆینتێن تە: {points}\n\n"
        "- تکایە یەکێ ژ وان یێن خوارێ هەڵبژێرە:"
    )
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🎁 بەشێ فەیک", callback_data="menu_fake"))
    markup.add(InlineKeyboardButton("⭐ ڤەکرنا بەشێ VIP", callback_data="vip"))
    markup.add(InlineKeyboardButton("🌟 تورسی تایبەت", callback_data="special_tursi"))
    markup.add(InlineKeyboardButton("🎟 بکارئینانا کۆدێ دیاری", callback_data="code"))
    markup.add(InlineKeyboardButton("🎁 دیاریا ڕۆژانە (+10 پۆینت)", callback_data="daily_bonus"))
    markup.add(InlineKeyboardButton("🌐 لینکێ ئینڤایتێ (Ref)", callback_data="ref_link"))
    
    if is_new:
        bot.send_message(chat_id, text, reply_markup=markup)
    else:
        try:
            bot.edit_message_text(text, chat_id, message_id, reply_markup=markup)
        except:
            bot.send_message(chat_id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id

    if call.data == "check_membership":
        if check_user_membership(user_id):
            bot.answer_callback_query(call.id, "✅ سوپاس، تە جۆین کر!", show_alert=True)
            if user_id not in user_points:
                user_points[user_id] = 1000
                save_data()
            show_main_menu(call.message.chat.id, call.message.message_id, is_new=False)
        else:
            bot.answer_callback_query(call.id, "❌ هێشتا تە جۆین نەکریە!", show_alert=True)
        return

    if not check_user_membership(user_id):
        bot.answer_callback_query(call.id, "⚠️ پێدڤیە سەرەتا جۆینێ کەناڵی ببی!", show_alert=True)
        return

    if user_id not in user_points:
        user_points[user_id] = 1000
        save_data()

    if call.data == "menu_fake":
        text = "🎁 **بەشێ فەیک**\nفەرموو بەشەک هەڵبژێرە:"
        markup = InlineKeyboardMarkup()
        row1 = [
            InlineKeyboardButton("TELEGRAM", callback_data="fake_telegram"),
            InlineKeyboardButton("TIKTOK", callback_data="fake_tiktok")
        ]
        row2 = [
            InlineKeyboardButton("INSTGRAM", callback_data="fake_instagram"),
            InlineKeyboardButton("چاڤەرێبن", callback_data="fake_wait")
        ]
        row3 = [
            InlineKeyboardButton("🎁 FREE (100 مێمبەر)", callback_data="free_telegram_100")
        ]
        row4 = [
            InlineKeyboardButton("🔙 ڤەگەر", callback_data="back_home")
        ]
        markup.add(*row1)
        markup.add(*row2)
        markup.add(*row3)
        markup.add(*row4)
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "fake_telegram":
        text = "✈️ **بەشێ تەلەگرام (TELEGRAM)**\nخزمەتگوزاریەکێ هەڵبژێرە:"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("👥 مێمبەر (1 = 20 پۆینت)", callback_data="tg_member"))
        markup.add(InlineKeyboardButton("❤️ ڕێەکشن (1 = 10 پۆینت)", callback_data="tg_reaction"))
        markup.add(InlineKeyboardButton("👁 ڤیو (100 = 50 پۆینت)", callback_data="tg_view"))
        markup.add(InlineKeyboardButton("🔙 ڤەگەر", callback_data="menu_fake"))
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "fake_tiktok":
        bot.answer_callback_query(call.id, "⏳ بەشێ TIKTOK هێشتا ئامەدە نەبویە!", show_alert=True)

    elif call.data == "fake_instagram":
        text = "📸 **بەشێ ئینستاگرام (INSTGRAM)**\nخزمەتگوزاریەکێ هەڵبژێرە:"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("❤️ لایک (100 لایک = 200 پۆینت)", callback_data="ig_like"))
        markup.add(InlineKeyboardButton("👁 ڤیو (100 ڤیو = 100 پۆینت)", callback_data="ig_view"))
        markup.add(InlineKeyboardButton("🔙 ڤەگەر", callback_data="menu_fake"))
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data in ["tg_member", "tg_reaction", "tg_view"]:
        names = {
            "tg_member": "مێمبەر (تەلەگرام)",
            "tg_reaction": "رێەکشن (تەلەگرام)",
            "tg_view": "ڤیو (تەلەگرام)"
        }
        s_name = names.get(call.data)
        user_states[user_id] = "WAITING_TG_QUANTITY"
        user_temp_data[user_id] = {'service_key': call.data, 'service_name': s_name}
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, f"🔢 چەند دانە تە دڤێن بۆ ({s_name})؟ ژمارەیەکێ دگەل ok بنڤیسە:")

    elif call.data in ["ig_like", "ig_view"]:
        names = {
            "ig_like": "لایک (ئینستاگرام)",
            "ig_view": "ڤیو (ئینستاگرام)"
        }
        s_name = names.get(call.data)
        user_states[user_id] = "WAITING_IG_QUANTITY"
        user_temp_data[user_id] = {'service_key': call.data, 'service_name': s_name}
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, f"🔢 چەند تە دڤێن بۆ ({s_name})؟ ژمارەیەکێ دگەل ok بنڤیسە:")

    elif call.data == "fake_wait":
        bot.answer_callback_query(call.id, "⏳ ئەڤ بەشە ل داهاتوویێ دێ هێتە زێدەکرن، چاڤەرێ بن!", show_alert=True)

    elif call.data == "free_telegram_100":
        current_time = datetime.now(iraq_tz)
        last_time_str = last_free_date.get(user_id)
        
        if last_time_str:
            last_time = datetime.fromisoformat(last_time_str)
            diff = current_time - last_time
            if diff < timedelta(hours=24):
                remaining = timedelta(hours=24) - diff
                hours = int(remaining.total_seconds() // 3600)
                minutes = int((remaining.total_seconds() % 3600) // 60)
                bot.answer_callback_query(call.id, f"⚠️ تو دشێ ڕوژانە جارەکێ ڤی بەشی بکاربینی!\nمایە: {hours} دەمژمێر و {minutes} خولەک.", show_alert=True)
                return

        user_states[user_id] = "WAITING_FREE_LINK"
        user_temp_data[user_id] = {'service': "تەلەگرام 100 مێمبەر (FREE)"}
        bot.send_message(call.message.chat.id, "🔗 لینکێ کەناڵ یان گروپێ خۆ بنێرە:")
        bot.answer_callback_query(call.id)

    elif call.data == "code":
        user_states[user_id] = "WAITING_GIFT_CODE"
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "🎟 تکایە کۆدێ دیاریێ بنڤیسە:")

    elif call.data == "special_tursi":
        text = "🌟 **بەشێ تورسی تایبەت**\nبەشەک هەڵبژێرە:"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("✈️ تەلەگرام", callback_data="tursi_telegram"))
        markup.add(InlineKeyboardButton("🎵 تیکتۆک", callback_data="tursi_tiktok"))
        markup.add(InlineKeyboardButton("🔙 ڤەگەر", callback_data="back_home"))
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "tursi_telegram":
        text = "✈️ **تەلەگرام - تورسی تایبەت**"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("👥 مێمبەر", callback_data="ts_tg_member"))
        markup.add(InlineKeyboardButton("👁 بینەر", callback_data="ts_tg_view"))
        markup.add(InlineKeyboardButton("🔙 ڤەگەر", callback_data="special_tursi"))
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "tursi_tiktok":
        text = "🎵 **تیکتۆک - تورسی تایبەت**"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("👁 بینەر", callback_data="ts_tt_view"))
        markup.add(InlineKeyboardButton("❤️ دلک", callback_data="ts_tt_like"))
        markup.add(InlineKeyboardButton("🔙 ڤەگەر", callback_data="special_tursi"))
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data in ["ts_tg_member", "ts_tg_view", "ts_tt_view", "ts_tt_like"]:
        service_names = {
            "ts_tg_member": "مێمبەر (تەلەگرام تورسی)",
            "ts_tg_view": "بینەر (تەلەگرام تورسی)",
            "ts_tt_view": "بینەر (تیکتۆک تورسی)",
            "ts_tt_like": "دلک (تیکتۆک تورسی)"
        }
        s_name = service_names.get(call.data)
        user_states[user_id] = "WAITING_TURSI_LINK"
        user_temp_data[user_id] = {'service': s_name}
        bot.send_message(call.message.chat.id, f"🔗 لینکێ خۆ بۆ ({s_name}) بنێرە:")
        bot.answer_callback_query(call.id)

    elif call.data == "back_home":
        user_states[user_id] = None
        show_main_menu(call.message.chat.id, call.message.message_id)

    elif call.data == "daily_bonus":
        current_date = datetime.now(iraq_tz).strftime('%Y-%m-%d')
        if last_bonus_date.get(user_id) == current_date:
            bot.answer_callback_query(call.id, "⚠️ تە دیاریا ئەڤرۆ وەرگرتییە!", show_alert=True)
        else:
            last_bonus_date[user_id] = current_date
            user_points[user_id] = user_points.get(user_id, 1000) + 10
            save_data()
            bot.answer_callback_query(call.id, f"🎉 پیرۆزە! 10 پۆینت زێدەبوون. کۆما پۆینتا: {user_points[user_id]}", show_alert=True)
        show_main_menu(call.message.chat.id, call.message.message_id)

    elif call.data == "ref_link":
        bot_info = bot.get_me()
        ref_url = f"https://t.me/{bot_info.username}?start={user_id}"
        invites_num = invited_counts.get(user_id, 0)
        msg_text = f"🔗 **لینکێ ئینڤایتێ تە:**\n`{ref_url}`\n\n👥 کەسێن هاتینە بانگهێشتکرن: {invites_num}"
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, msg_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.from_user.id
    if not check_user_membership(user_id):
        show_force_sub_message(message.chat.id)
        return

    state = user_states.get(user_id)
    text_input = message.text.strip()

    if state == "WAITING_TG_QUANTITY":
        # لابردنا پەیڤا ok ئەگەر هاتبێت ڤە
        clean_text = text_input.lower().replace("ok", "").strip()
        if not clean_text.isdigit() or int(clean_text) <= 0:
            bot.send_message(message.chat.id, "❌ تکایە ژمارەیەکا دروست دگەل ok بنڤیسە:")
            return

        quantity = int(clean_text)
        temp = user_temp_data.get(user_id, {})
        s_key = temp.get('service_key')

        cost = 0
        if s_key == "tg_member":
            cost = quantity * 20
        elif s_key == "tg_reaction":
            cost = quantity * 10
        elif s_key == "tg_view":
            cost = int((quantity / 100) * 50)

        user_points[user_id] = user_points.get(user_id, 1000)

        if user_points[user_id] < cost:
            bot.send_message(message.chat.id, f"❌ پۆینتێن تە تێرانەکن!\n💰 پۆینتێن تە: {user_points[user_id]}\n🏷 پێدڤی ب: {cost} پۆینتانە.\n👉 پۆینتێن خۆ پڕبکە.")
            user_states[user_id] = None
            return

        temp['quantity'] = quantity
        temp['cost'] = cost
        user_temp_data[user_id] = temp
        user_states[user_id] = "WAITING_TG_LINK"
        bot.send_message(message.chat.id, "🔗 لینکێ کەناڵ یان گروپێ خۆ بنێرە:")

    elif state == "WAITING_TG_LINK":
        link = message.text
        temp = user_temp_data.get(user_id, {})
        s_name = temp.get('service_name', 'تەلەگرام')
        quantity = temp.get('quantity', 0)
        cost = temp.get('cost', 0)

        user_points[user_id] = user_points.get(user_id, 1000) - cost
        save_data()
        user_states[user_id] = None

        bot.send_message(message.chat.id, "پیرۆزە داخازیا تە هاتە بجھ ینان‌‌🚀")

        admin_msg = (
            f"🔔 **[کڕینەکا نووی - تەلەگرام]**\n\n"
            f"👤 ئایدی: `{user_id}`\n"
            f"📌 خزمەتگوزاری: {s_name}\n"
            f"🔢 بڕ: {quantity}\n"
            f"💰 پۆینتێن هاتینە کێمکرن: {cost}\n"
            f"🔗 لینک: {link}"
        )
        try:
            bot.send_message(8832347891, admin_msg, parse_mode="Markdown")
        except:
            pass

    elif state == "WAITING_IG_QUANTITY":
        clean_text = text_input.lower().replace("ok", "").strip()
        if not clean_text.isdigit() or int(clean_text) <= 0:
            bot.send_message(message.chat.id, "❌ تکایە ژمارەیەکا دروست دگەل ok بنڤیسە:")
            return

        quantity = int(clean_text)
        temp = user_temp_data.get(user_id, {})
        s_key = temp.get('service_key')

        cost = 0
        if s_key == "ig_like":
            # 100 like = 200 points => cost = (quantity / 100) * 200
            cost = int((quantity / 100) * 200)
        elif s_key == "ig_view":
            # 100 view = 100 points => cost = (quantity / 100) * 100
            cost = int((quantity / 100) * 100)

        user_points[user_id] = user_points.get(user_id, 1000)

        if user_points[user_id] < cost:
            bot.send_message(message.chat.id, f"❌ پۆینتێن تە تێرانەکن!\n💰 پۆینتێن تە: {user_points[user_id]}\n🏷 پێدڤی ب: {cost} پۆینتانە.\n👉 پۆینتێن خۆ پڕبکە.")
            user_states[user_id] = None
            return

        temp['quantity'] = quantity
        temp['cost'] = cost
        user_temp_data[user_id] = temp
        user_states[user_id] = "WAITING_IG_LINK"
        bot.send_message(message.chat.id, "🔗 لینک ڤیدیو فرێکە:")

    elif state == "WAITING_IG_LINK":
        link = message.text
        temp = user_temp_data.get(user_id, {})
        s_name = temp.get('service_name', 'ئینستاگرام')
        quantity = temp.get('quantity', 0)
        cost = temp.get('cost', 0)

        user_points[user_id] = user_points.get(user_id, 1000) - cost
        save_data()
        user_states[user_id] = None

        bot.send_message(message.chat.id, "پیرۆزە داخازیا تە هاتە بجھ ینان‌‌🚀")

        admin_msg = (
            f"🔔 **[کڕینەکا نووی - ئینستاگرام]**\n\n"
            f"👤 ئایدی: `{user_id}`\n"
            f"📌 خزمەتگوزاری: {s_name}\n"
            f"🔢 بڕ: {quantity}\n"
            f"💰 پۆینتێن هاتینە کێمکرن: {cost}\n"
            f"🔗 لینک: {link}"
        )
        try:
            bot.send_message(8832347891, admin_msg, parse_mode="Markdown")
        except:
            pass

    elif state == "WAITING_GIFT_CODE":
        code = message.text.strip()
        user_states[user_id] = None
        
        if user_id not in used_codes_data:
            used_codes_data[user_id] = []
            
        if code == "turse2027":
            if "turse2027" in used_codes_data[user_id]:
                bot.send_message(message.chat.id, "❌ تە بەری نۆکە ئەڤ کۆدە بکارئینایە!")
            else:
                used_codes_data[user_id].append("turse2027")
                user_points[user_id] = user_points.get(user_id, 1000) + 500
                save_data()
                bot.send_message(message.chat.id, f"🎉 پیرۆزە! 500 پۆینت بۆ کۆما پۆینتێن تە زێدەبوون.\n💰 کۆما نوو: {user_points[user_id]}")
        else:
            bot.send_message(message.chat.id, "❌ کۆدێ دیاریێ هەڵە یە!")

    elif state == "WAITING_FREE_LINK":
        if user_id not in user_temp_data:
            user_temp_data[user_id] = {}
        user_temp_data[user_id]['link'] = message.text
        user_states[user_id] = "WAITING_FREE_NUMBER"
        bot.send_message(message.chat.id, "🔢 تکایە ژمارەیەکێ ژ (1 تا 100) بنڤیسە:")

    elif state == "WAITING_FREE_NUMBER":
        text_val = message.text.strip()
        if not text_val.isdigit() or not (1 <= int(text_val) <= 100):
            bot.send_message(message.chat.id, "❌ تکایە تنێ ژمارەیەکێ د ناڤبەرا 1 بۆ 100 دا بنڤیسە:")
            return

        link = user_temp_data.get(user_id, {}).get('link', 'نەدیار')
        num = text_val
        service = user_temp_data.get(user_id, {}).get('service', 'FREE')
        
        last_free_date[user_id] = datetime.now(iraq_tz).isoformat()
        save_data()
        
        user_states[user_id] = None

        bot.send_message(message.chat.id, "✅ داخوازیا تە هاتە جێبەجێکردن")

        admin_msg = (
            f"🔔 **[ئاگەهداریا نووی - بەشێ فەیری]**\n\n"
            f"👤 ئایدیێ بەکارهێنەری: `{user_id}`\n"
            f"📌 خزمەتگوزاری: {service}\n"
            f"🔗 لینک: {link}\n"
            f"🔢 ژمارە (1-100): {num}"
        )
        try:
            bot.send_message(8832347891, admin_msg, parse_mode="Markdown")
        except:
            pass

    elif state == "WAITING_FAKE_SECTION_LINK":
        link = message.text
        service = user_temp_data.get(user_id, {}).get('service', 'فەیک')
        user_states[user_id] = None

        bot.send_message(message.chat.id, f"✅ داخوازیا تە بۆ ({service}) ب سەرکەفتیانە هاتە وەرگرتن!")

        admin_msg = (
            f"🔔 **[داخوازەکا نووی / کڕین - فەیک]**\n\n"
            f"👤 ئایدیێ بەکارهێنەری: `{user_id}`\n"
            f"📌 خزمەتگوزاری: {service}\n"
            f"🔗 لینک: {link}"
        )
        try:
            bot.send_message(8832347891, admin_msg, parse_mode="Markdown")
        except:
            pass

    elif state == "WAITING_TURSI_LINK":
        link = message.text
        service = user_temp_data.get(user_id, {}).get('service', 'تورسی تایبەت')
        user_states[user_id] = None
        
        bot.send_message(message.chat.id, f"✅ داخوازیا تە بۆ ({service}) ب سەرکەفتیانە هاتە وەرگرتن!")
        
        admin_msg = (
            f"🔔 **[داخوازەکا نووی / تورسی تایبەت]**\n\n"
            f"👤 ئایدیێ بەکارهێنەری: `{user_id}`\n"
            f"📌 خزمەتگوزاری: {service}\n"
            f"🔗 لینک: {link}"
        )
        try:
            bot.send_message(8832347891, admin_msg, parse_mode="Markdown")
        except:
            pass

bot.infinity_polling()
