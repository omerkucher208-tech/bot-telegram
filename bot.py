import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timezone, timedelta
import json
import os
import threading
import time

TOKEN = "8664613512:AAFFMntlik-eCWCF-qnUaV32qmwaiPYEBKo"
ADMIN_ID = 8832347891
CHANNELS = ["@TURSE_INFO", "@TORSEII"]
ADMIN_USERNAME = "@T_U_R_S_E"

bot = telebot.TeleBot(TOKEN)
DATA_FILE = "bot_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
        except Exception as e:
            print(f"Error loading data: {e}")
            
    return {
        "points": {},
        "last_bonus": {},
        "last_free": {},
        "used_codes": {},
        "global_used_codes": [],
        "vip": {},
        "vip_expiry": {},
        "bonus_points_earned": {},
        "total_gifts_claimed": {},
        "total_requests": {},
        "sent_points_count": {}
    }

db = load_data()

def save_data_to_file():
    data = {
        "points": {str(k): v for k, v in user_points.items()},
        "last_bonus": {str(k): v for k, v in last_bonus_date.items()},
        "last_free": {str(k): v for k, v in last_free_date.items()},
        "used_codes": {str(k): v for k, v in used_codes_data.items()},
        "global_used_codes": global_used_codes,
        "vip": {str(k): v for k, v in vip_users.items()},
        "vip_expiry": {str(k): v for k, v in vip_expiry_date.items()},
        "bonus_points_earned": {str(k): v for k, v in bonus_points_earned.items()},
        "total_gifts_claimed": {str(k): v for k, v in total_gifts_claimed.items()},
        "total_requests": {str(k): v for k, v in total_requests.items()},
        "sent_points_count": {str(k): v for k, v in sent_points_count.items()}
    }
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error saving data: {e}")

user_points = {int(k): v for k, v in db.get("points", {}).items()}
last_bonus_date = {int(k): v for k, v in db.get("last_bonus", {}).items()}
last_free_date = {int(k): v for k, v in db.get("last_free", {}).items()}
used_codes_data = {int(k): v for k, v in db.get("used_codes", {}).items()}
global_used_codes = db.get("global_used_codes", [])
vip_users = {int(k): v for k, v in db.get("vip", {}).items()}
vip_expiry_date = {int(k): v for k, v in db.get("vip_expiry", {}).items()}
bonus_points_earned = {int(k): v for k, v in db.get("bonus_points_earned", {}).items()}
total_gifts_claimed = {int(k): v for k, v in db.get("total_gifts_claimed", {}).items()}
total_requests = {int(k): v for k, v in db.get("total_requests", {}).items()}
sent_points_count = {int(k): v for k, v in db.get("sent_points_count", {}).items()}

user_states = {}
user_temp_data = {}
iraq_tz = timezone(timedelta(hours=3))

def check_user_membership(user_id):
    for channel in CHANNELS:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                return False
        except:
            return False  
    return True

def show_force_sub_message(chat_id):
    text = (
        "⚠️ **بۆ بەکارئینانا بۆتی، پێدڤیە بەری هەر شتەکی جۆینێ هەردوو کەناڵێن مە ببی!**\n\n"
        "👇 تکایە سەرەتا جۆینێ کەناڵان بکە، پاشان دوگمەیا (پشکنینا جۆینبوونێ) کلیک بکە:"
    )
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("JOIN 🌐 (TURSE_INFO)", url="https://t.me/TURSE_INFO"))
    markup.add(InlineKeyboardButton("JOIN 🌐 (TORSEII)", url="https://t.me/TORSEII"))
    markup.add(InlineKeyboardButton("✅ پشکنینا جۆینبوونێ (Check)", callback_data="check_membership"))
    try:
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")
    except:
        pass

def background_vip_checker():
    while True:
        try:
            now = datetime.now(iraq_tz)
            for uid, is_vip in list(vip_users.items()):
                if is_vip:
                    exp_str = vip_expiry_date.get(uid)
                    if exp_str:
                        exp_time = datetime.fromisoformat(exp_str)
                        if now >= exp_time:
                            vip_users[uid] = False
                            vip_expiry_date.pop(uid, None)
                            save_data_to_file()
                            try:
                                bot.send_message(uid, "⚠️ **تێبینییا VIP:**\nماوەیا VIP یا حەفتییا تە تەواو بوو.")
                            except:
                                pass
        except Exception as e:
            print(f"Error in background checker: {e}")
        time.sleep(3600)

threading.Thread(target=background_vip_checker, daemon=True).start()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    
    if not check_user_membership(user_id):
        show_force_sub_message(message.chat.id)
        return

    if user_id not in user_points:
        user_points[user_id] = 0
        save_data_to_file()
        
    user_states[user_id] = None
    show_main_menu(message.chat.id, message.message_id if hasattr(message, 'message_id') else None, is_new=True)

def show_main_menu(chat_id, message_id=None, is_new=False):
    user_id = chat_id
    points = user_points.get(user_id, 0)
    
    text = (
        "💎 - بەخێرهاتن بۆ بۆتا دەنگدانا کوردی\n"
        f"💰 - پۆینتێن تە: {points}\n\n"
        "- تکایە یەکێ ژ وان یێن خوارێ هەڵبژێرە:"
    )
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🎁 بەشێ فەیک", callback_data="menu_fake"))
    markup.add(InlineKeyboardButton("⭐ کڕینا بەشێ VIP (1200 پۆینت / 1 حەفتە)", callback_data="buy_vip_menu"))
    markup.add(InlineKeyboardButton("بەشێ vip", callback_data="vip"))
    markup.add(InlineKeyboardButton("🧠🫂 کۆمکرنا پوینتان", callback_data="collect_points_menu"))
    markup.add(InlineKeyboardButton("💾 زانیاری دەربارەی ئەکاونت", callback_data="account_info"))
    markup.add(InlineKeyboardButton("🛒 کڕینا پۆینتان", callback_data="buy_points"))
    
    if is_new:
        try:
            bot.send_message(chat_id, text, reply_markup=markup)
        except:
            pass
    else:
        try:
            bot.edit_message_text(text, chat_id, message_id, reply_markup=markup)
        except:
            try:
                bot.send_message(chat_id, text, reply_markup=markup)
            except:
                pass

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id

    if call.data == "check_membership":
        if check_user_membership(user_id):
            bot.answer_callback_query(call.id, "✅ سوپاس، تە جۆینێ هەردوو کەناڵان کر!", show_alert=True)
            if user_id not in user_points:
                user_points[user_id] = 0
                save_data_to_file()
            show_main_menu(call.message.chat.id, call.message.message_id, is_new=False)
        else:
            bot.answer_callback_query(call.id, "❌ هێشتا تە جۆینێ هەردوو کەناڵان نەکریە!", show_alert=True)
        return

    if not check_user_membership(user_id):
        bot.answer_callback_query(call.id, "⚠️ پێدڤیە سەرەتا جۆینێ هەردوو کەناڵان ببی!", show_alert=True)
        show_force_sub_message(call.message.chat.id)
        return

    if user_id not in user_points:
        user_points[user_id] = 0
        save_data_to_file()

    if call.data == "buy_vip_menu":
        is_vip = vip_users.get(user_id, False)
        if is_vip:
            bot.answer_callback_query(call.id, "⭐ تو نوکە ئەندامێ VIP یی و ئەکاونتێ تە فعالە!", show_alert=True)
            return
            
        text = "⭐ **پشتڕاستکرنا کڕینا VIP**\n\nئایا تو دخوازی **1200 پۆینت** بڕی و بووە خاوەن VIP بۆ ماوەیا 1 حەفتێ؟"
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("✅ Yes (بەڵێ)", callback_data="confirm_buy_vip"),
            InlineKeyboardButton("❌ No (نەخێر)", callback_data="back_home")
        )
        try:
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
        except:
            pass
        return

    elif call.data == "confirm_buy_vip":
        is_vip = vip_users.get(user_id, False)
        if is_vip:
            bot.answer_callback_query(call.id, "⭐ تو نوکە ئەندامێ VIP یی!", show_alert=True)
            return

        current_points = user_points.get(user_id, 0)
        if current_points >= 1200:
            user_points[user_id] = current_points - 1200
            vip_users[user_id] = True
            vip_expiry_date[user_id] = (datetime.now(iraq_tz) + timedelta(days=7)).isoformat()
            save_data_to_file()
            bot.answer_callback_query(call.id, "🎉 پیرۆزە! 1200 پۆینت هاتە بڕین و تو بۆ ماوەیا 1 حەفتی بوویە خاوەن VIP ⭐", show_alert=True)
            show_main_menu(call.message.chat.id, call.message.message_id, is_new=False)
        else:
            bot.answer_callback_query(call.id, f"❌ پۆینتێن تە تێرانەکن! (پێدڤی ب 1200 پۆینتانییە، پۆینتێن تە: {current_points})", show_alert=True)
            show_main_menu(call.message.chat.id, call.message.message_id, is_new=False)
        return

    elif call.data == "vip":
        is_vip = vip_users.get(user_id, False)
        if not is_vip:
            bot.answer_callback_query(call.id, "❌ تو ئەندامێ VIP نینی! تکایە سەرەتا بەشێ کڕینا VIP هەڵبژێرە.", show_alert=True)
            return

        text = "⭐ **بەشێ vip**\nفەرموو بەشەک هەڵبژێرە:"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("✈️ تەلەگرام (VIP)", callback_data="vip_telegram"))
        markup.add(InlineKeyboardButton("🎵 تیکتۆک (VIP)", callback_data="vip_tiktok"))
        markup.add(InlineKeyboardButton("📸 ئینستاگرام (VIP)", callback_data="vip_instagram"))
        markup.add(InlineKeyboardButton("🔙 ڤەگەر", callback_data="back_home"))
        try:
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
        except:
            pass

    elif call.data == "vip_telegram":
        text = "✈️ **تەلەگرام - VIP**\nخزمەتگوزاریەکێ هەڵبژێرە:"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("❤️ دلک / دەنگ (1 = 40 پۆینت)", callback_data="vip_tg_vote"))
        markup.add(InlineKeyboardButton("👥 مێمبەر 60 رۆژ زەمان (1 = 80 پۆینت)", callback_data="vip_tg_member"))
        markup.add(InlineKeyboardButton("🔙 ڤەگەر", callback_data="vip"))
        try:
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
        except:
            pass

    elif call.data in ["vip_tg_vote", "vip_tg_member"]:
        names = {
            "vip_tg_vote": "دەنگ / دلک (تەلەگرام VIP)",
            "vip_tg_member": "مێمبەر 60 رۆژ زەمان (تەلەگرام VIP)"
        }
        s_name = names.get(call.data)
        user_states[user_id] = "WAITING_VIP_TG_QUANTITY"
        user_temp_data[user_id] = {'service_key': call.data, 'service_name': s_name}
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, f"🔢 چەند تەدڤێن بۆ ({s_name})؟ ژمارەیەکێ دگەل ok بنڤیسە:")

    elif call.data == "vip_tiktok":
        text = "🎵 **تیکتۆک - VIP**\nخزمەتگوزاریەکێ هەڵبژێرە:"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("💾 Saved (100 = 300 پۆینت)", callback_data="vip_tt_saved"))
        markup.add(InlineKeyboardButton("❤️ Like Live (100 = 300 پۆینت)", callback_data="vip_tt_like_live"))
        markup.add(InlineKeyboardButton("↗️ Share (100 = 300 پۆینت)", callback_data="vip_tt_share"))
        markup.add(InlineKeyboardButton("🔙 ڤەگەر", callback_data="vip"))
        try:
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
        except:
            pass

    elif call.data in ["vip_tt_saved", "vip_tt_like_live", "vip_tt_share"]:
        names = {
            "vip_tt_saved": "Saved (تیکتۆک VIP)",
            "vip_tt_like_live": "Like Live (تیکتۆک VIP)",
            "vip_tt_share": "Share (تیکتۆک VIP)"
        }
        s_name = names.get(call.data)
        user_states[user_id] = "WAITING_VIP_TT_QUANTITY"
        user_temp_data[user_id] = {'service_key': call.data, 'service_name': s_name}
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, f"🔢 چەند تە دڤێن؟ (100-100) بنڤیسە (بۆ نموونە 100):")

    elif call.data == "vip_instagram":
        text = "📸 **ئینستاگرام - VIP**\nفەرموو خزمەتگوزارییا خۆ هەڵبژێرە:"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("👁 بینەرێن ستوری (100 = 300 پۆینت)", callback_data="vip_ig_story_views"))
        markup.add(InlineKeyboardButton("❤️ لایکێن رێلز (100 = 300 پۆینت)", callback_data="vip_ig_reel_likes"))
        markup.add(InlineKeyboardButton("👁 بینەرێن رێلز (500 = 300 پۆینت)", callback_data="vip_ig_reel_views"))
        markup.add(InlineKeyboardButton("🚀 اکسپلور (100 = 100 پۆینت)", callback_data="vip_ig_explore"))
        markup.add(InlineKeyboardButton("🔙 ڤەگەر", callback_data="vip"))
        try:
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
        except:
            pass

    elif call.data in ["vip_ig_story_views", "vip_ig_reel_likes", "vip_ig_reel_views", "vip_ig_explore"]:
        names = {
            "vip_ig_story_views": "بینەرێن ستوری (ئینستاگرام VIP)",
            "vip_ig_reel_likes": "لایکێن رێلز (ئینستاگرام VIP)",
            "vip_ig_reel_views": "بینەرێن رێلز (ئینستاگرام VIP)",
            "vip_ig_explore": "اکسپلور (ئینستاگرام VIP)"
        }
        s_name = names.get(call.data)
        user_states[user_id] = "WAITING_VIP_IG_QUANTITY"
        user_temp_data[user_id] = {'service_key': call.data, 'service_name': s_name}
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, f"🔢 چەند تەدڤێن بۆ ({s_name})؟ ژمارەیەکێ دگەل ok بنڤیسە:")

    elif call.data == "collect_points_menu":
        text = (
            "🧠🫂 **بەشێ کۆمکرنا پۆینتان**\n\n"
            "فەرموو ڕێگایەکێ هەڵبژێرە بۆ زێدەکرنا پۆینتێن خۆ:"
        )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🎁 دیاریا ڕۆژانە (+10 پۆینت)", callback_data="daily_bonus"))
        markup.add(InlineKeyboardButton("🎟 بکارئینانا کۆدێ دیاری", callback_data="code"))
        markup.add(InlineKeyboardButton("🔙 ڤەگەر", callback_data="back_home"))
        try:
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
        except:
            pass

    elif call.data == "account_info":
        points = user_points.get(user_id, 0)
        is_vip = vip_users.get(user_id, False)
        vip_status = "VIP ⭐" if is_vip else "FREE 👤"
        gifts_claimed = total_gifts_claimed.get(user_id, 0)
        bonus_earned = bonus_points_earned.get(user_id, 0)
        requests_count = total_requests.get(user_id, 0)
        sent_points = sent_points_count.get(user_id, 0)

        text = (
            f"💾 **زانیاری دەربارەی ئەکاونت:**\n\n"
            f"• [❇️] پۆینتت : `{points}`\n"
            f"• [👤] you VIP - FREE؟ : `{vip_status}`\n\n"
            f"• [🎁] ژمارەی ئەو دیارییانەی وەرتگرتوە : `{gifts_claimed}`\n"
            f"• [❇️] ژمارەی ئەو پۆینتانەی لە دیاری ڕۆژانە وەرتگرتوە : `{bonus_earned}`\n"
            f"• [📮] ژمارەی داواکارییەکانت لە بۆت : `{requests_count}`\n"
            f"• [♻️] ژمارەی ئەو کەسانەی کە پۆینتت بۆی ناردوە : `{sent_points}`\n"
        )

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 ڤەگەر", callback_data="back_home"))

        try:
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
        except:
            pass

    elif call.data == "buy_points":
        text = (
            "🛒 **بەشێ کڕینا پۆینتان**\n\n"
            "💵 نرخ: **2000 پۆینت = 1000 دینار**\n\n"
            "💳 رێگایێن پارەدانا بەردەست:\n"
            "• **FIB**\n"
            "• **FastPay**\n"
            "• **کۆڕەک (Korek)**\n\n"
            "👇 بۆ کڕینا پۆینتان، دوگمەیا خوارێ کلیک بکە:"
        )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📩 داخوازی کڕینێ (رەوانەکرنا وەسڵ/ژمارە)", callback_data="request_buy_points"))
        markup.add(InlineKeyboardButton("🔙 ڤەگەر", callback_data="back_home"))
        try:
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
        except:
            pass

    elif call.data == "request_buy_points":
        user_states[user_id] = "WAITING_BUY_RECEIPT"
        bot.answer_callback_query(call.id)
        try:
            bot.send_message(
                call.message.chat.id, 
                f"📥 وێنەیێ وەسڵێ خۆ یان ژمارە و ناوەندا پارەدانێ (FIB, FastPay, Korek) بۆ مە بنێرە:\n\n"
                f"⚠️ **تێبینی:** پشتی هناردنێ، لای خۆ ڤە نامەیەکێ بڕێڤەبەری ژی ڕوانە بکە: {ADMIN_USERNAME}"
            )
        except:
            pass

    elif call.data == "menu_fake":
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
            InlineKeyboardButton("🔙 ڤەگەر", callback_data="back_home")
        ]
        markup.add(*row1)
        markup.add(*row2)
        markup.add(*row3)
        try:
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
        except:
            pass

    elif call.data == "fake_telegram":
        text = "✈️ **بەشێ تەلەگرام (TELEGRAM)**\nخزمەتگوزاریەکێ هەڵبژێرە:"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("👥 مێمبەر (1 = 20 پۆینت)", callback_data="tg_member"))
        markup.add(InlineKeyboardButton("❤️ ڕێەکشن (1 = 10 پۆینت)", callback_data="tg_reaction"))
        markup.add(InlineKeyboardButton("👁 ڤیو (100 = 50 پۆینت)", callback_data="tg_view"))
        markup.add(InlineKeyboardButton("🔙 ڤەگەر", callback_data="menu_fake"))
        try:
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
        except:
            pass

    elif call.data == "fake_tiktok":
        bot.answer_callback_query(call.id, "⏳ بەشێ TIKTOK هێشتا ئامەدە نەبویە!", show_alert=True)

    elif call.data == "fake_instagram":
        text = "📸 **بەشێ ئینستاگرام (INSTGRAM)**\nخزمەتگوزاریەکێ هەڵبژێرە:"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("❤️ لایک (100 لایک = 200 پۆینت)", callback_data="ig_like"))
        markup.add(InlineKeyboardButton("👁 ڤیو (100 ڤیو = 100 پۆینت)", callback_data="ig_view"))
        markup.add(InlineKeyboardButton("🔙 ڤەگەر", callback_data="menu_fake"))
        try:
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
        except:
            pass

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
        try:
            bot.send_message(call.message.chat.id, f"🔢 چەند دانە تە دڤێن بۆ ({s_name})؟ ژمارەیەکێ دگەل ok بنڤیسە:")
        except:
            pass

    elif call.data in ["ig_like", "ig_view"]:
        names = {
            "ig_like": "لایک (ئینستاگرام)",
            "ig_view": "ڤیو (ئینستاگرام)"
        }
        s_name = names.get(call.data)
        user_states[user_id] = "WAITING_IG_QUANTITY"
        user_temp_data[user_id] = {'service_key': call.data, 'service_name': s_name}
        bot.answer_callback_query(call.id)
        try:
            bot.send_message(call.message.chat.id, f"🔢 چەند تە دڤێن بۆ ({s_name})؟ ژمارەیەکێ دگەل ok بنڤیسە:")
        except:
            pass

    elif call.data == "fake_wait":
        bot.answer_callback_query(call.id, "⏳ ئەڤ بەشە ل داهاتوویێ دێ هێتە زێدەکرن، چاڤەرێ بن!", show_alert=True)

    elif call.data == "code":
        user_states[user_id] = "WAITING_GIFT_CODE"
        bot.answer_callback_query(call.id)
        try:
            bot.send_message(call.message.chat.id, "🎟 تکایە کۆدێ دیاریێ بنڤیسە:")
        except:
            pass

    elif call.data == "back_home":
        user_states[user_id] = None
        show_main_menu(call.message.chat.id, call.message.message_id)

    elif call.data == "daily_bonus":
        current_date = datetime.now(iraq_tz).strftime('%Y-%m-%d')
        if last_bonus_date.get(user_id) == current_date:
            bot.answer_callback_query(call.id, "⚠️ تە دیاریا ئەڤرۆ وەرگرتییە!", show_alert=True)
        else:
            last_bonus_date[user_id] = current_date
            user_points[user_id] = user_points.get(user_id, 0) + 10
            
            bonus_points_earned[user_id] = bonus_points_earned.get(user_id, 0) + 10
            total_gifts_claimed[user_id] = total_gifts_claimed.get(user_id, 0) + 1
            save_data_to_file()
            
            bot.answer_callback_query(call.id, f"🎉 پیرۆزە! 10 پۆینت زێدەبوون. کۆما پۆینتا: {user_points[user_id]}", show_alert=True)
        
        text = (
            "🧠🫂 **بەشێ کۆمکرنا پۆینتان**\n\n"
            "فەرموو ڕێگایەکێ هەڵبژێرە بۆ زێدەکرنا پۆینتێن خۆ:"
        )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🎁 دیاریا ڕۆژانە (+10 پۆینت)", callback_data="daily_bonus"))
        markup.add(InlineKeyboardButton("🎟 بکارئینانا کۆدێ دیاری", callback_data="code"))
        markup.add(InlineKeyboardButton("🔙 ڤەگەر", callback_data="back_home"))
        try:
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
        except:
            pass

@bot.message_handler(content_types=['text', 'photo', 'document'], func=lambda message: True)
def handle_text(message):
    user_id = message.from_user.id
    if not check_user_membership(user_id):
        show_force_sub_message(message.chat.id)
        return

    state = user_states.get(user_id)
    text_input = message.text.strip() if message.text else ""

    if state == "WAITING_BUY_RECEIPT":
        user_states[user_id] = None
        total_requests[user_id] = total_requests.get(user_id, 0) + 1
        save_data_to_file()
        
        try:
            bot.send_message(
                message.chat.id, 
                f"✅ وەسڵ / داخوازییا تە گەهشتە رێڤەبەری.\n"
                f"👇 تکایە نامەیەکێ بڕێڤەبەری ژی بکە و ئاگادار بکە: {ADMIN_USERNAME}"
            )
        except:
            pass
        
        now_iraq = datetime.now(iraq_tz)
        time_str = now_iraq.strftime('%H:%M:%S')
        date_str = now_iraq.strftime('%Y-%m-%d')
        
        admin_msg = (
            f"🛒 **[داخوازەکا نووی بۆ کڕینا پۆینتان]**\n\n"
            f"👤 ئایدی: `{user_id}`\n"
            f"👤 ناڤ: {message.from_user.first_name}\n"
            f"🔗 یوزرنەیم: @{message.from_user.username if message.from_user.username else 'نەدیار'}\n"
            f"📅 رۆژ: {date_str} | ⏰ دەم: {time_str}"
        )
        try:
            bot.send_message(8832347891, admin_msg, parse_mode="Markdown")
            if message.photo:
                bot.send_photo(8832347891, message.photo[-1].file_id, caption=f"وەسڵێ ئایدی: {user_id}")
            elif message.document:
                bot.send_document(8832347891, message.document.file_id, caption=f"وەسڵێ ئایدی: {user_id}")
            elif message.text:
                bot.send_message(8832347891, f"دەقێ وەسڵێ/ژمارەیێ: {message.text}")
        except:
            pass
        return

    if not message.text:
        return

    if state == "WAITING_VIP_TG_QUANTITY":
        clean_text = text_input.lower().replace("ok", "").strip()
        if not clean_text.isdigit() or int(clean_text) <= 0:
            try:
                bot.send_message(message.chat.id, "❌ تکایە ژمارەیەکا دروست دگەل ok بنڤیسە:")
            except:
                pass
            return

        quantity = int(clean_text)
        temp = user_temp_data.get(user_id, {})
        s_key = temp.get('service_key')

        cost = 0
        if s_key == "vip_tg_vote":
            cost = quantity * 40
        elif s_key == "vip_tg_member":
            cost = quantity * 80

        temp['quantity'] = quantity
        temp['cost'] = cost
        user_temp_data[user_id] = temp
        user_states[user_id] = "WAITING_VIP_TG_LINK"
        try:
            bot.send_message(message.chat.id, "🔗 لینکێ خۆ فرێکە:")
        except:
            pass

    elif state == "WAITING_VIP_TG_LINK":
        link = message.text
        temp = user_temp_data.get(user_id, {})
        s_name = temp.get('service_name', 'VIP')
        quantity = temp.get('quantity', 0)
        cost = temp.get('cost', 0)

        current_points = user_points.get(user_id, 0)
        if current_points < cost:
            try:
                bot.send_message(message.chat.id, f"❌ پۆینتێن تە تێرانەکن!\n💰 پۆینتێن تە: {current_points}\n🏷 پێدڤی ب: {cost} پۆینتانە.")
            except:
                pass
            user_states[user_id] = None
            return

        user_points[user_id] = current_points - cost
        total_requests[user_id] = total_requests.get(user_id, 0) + 1
        save_data_to_file()
        user_states[user_id] = None

        final_bal = user_points[user_id]
        success_msg = (
            f"سوپاس بۆ داواکارییەکەت! داواکارییەکەت بۆ زیادکردنی ئەندام ({s_name}) سەرکەوتوو بوو و جێبەجێ دەکرێت.\n\n"
            f"خزمەتگوزاری: {s_name}\n\n"
            f"بڕی خەرجکراو: {cost} خاڵ\n\n"
            f"ژمارە: {quantity}\n\n"
            f"رصیدی ماوە: {final_bal} خاڵ\n\n"
            f"🔗 الرابط:\n"
            f"{link}"
        )
        try:
            bot.send_message(message.chat.id, success_msg)
        except:
            pass

        now_iraq = datetime.now(iraq_tz)
        time_str = now_iraq.strftime('%H:%M:%S')
        date_str = now_iraq.strftime('%Y-%m-%d')

        admin_msg = (
            f"🔔 **[کڕینەکا نووی - VIP تەلەگرام]**\n\n"
            f"👤 ئایدی: `{user_id}`\n"
            f"📌 خزمەتگوزاری: {s_name}\n"
            f"🔢 بڕ: {quantity}\n"
            f"💰 پۆینت: {cost}\n"
            f"🔗 لینک: {link}\n"
            f"📅 رۆژ: {date_str}\n"
            f"⏰ دەم: {time_str}"
        )
        try:
            bot.send_message(8832347891, admin_msg, parse_mode="Markdown")
        except:
            pass

    elif state == "WAITING_VIP_TT_QUANTITY":
        clean_text = text_input.replace("-100", "").replace("100-", "").strip()
        if not clean_text.isdigit() or int(clean_text) <= 0:
            try:
                bot.send_message(message.chat.id, "❌ تکایە ژمارەیەکێ دروست بنڤیسە (بۆ نموونە 100):")
            except:
                pass
            return

        quantity = int(clean_text)
        temp = user_temp_data.get(user_id, {})
        cost = int((quantity / 100) * 300)

        temp['quantity'] = quantity
        temp['cost'] = cost
        user_temp_data[user_id] = temp
        user_states[user_id] = "WAITING_VIP_TT_LINK"
        try:
            bot.send_message(message.chat.id, "🔗 لینکێ پوستێ خو فرێکە:")
        except:
            pass

    elif state == "WAITING_VIP_TT_LINK":
        link = message.text
        temp = user_temp_data.get(user_id, {})
        s_name = temp.get('service_name', 'تیکتۆک VIP')
        quantity = temp.get('quantity', 0)
        cost = temp.get('cost', 0)

        current_points = user_points.get(user_id, 0)
        if current_points < cost:
            try:
                bot.send_message(message.chat.id, f"❌ پۆینتێن تە تێرانەکن!\n💰 پۆینتێن تە: {current_points}\n🏷 پێدڤی ب: {cost} پۆینتانە.")
            except:
                pass
            user_states[user_id] = None
            return

        user_points[user_id] = current_points - cost
        total_requests[user_id] = total_requests.get(user_id, 0) + 1
        save_data_to_file()
        user_states[user_id] = None

        final_bal = user_points[user_id]
        success_msg = (
            f"سوپاس بۆ داواکارییەکەت! داواکارییەکەت بۆ ({s_name}) سەرکەوتوو بوو و جێبەجێ دەکرێت.\n\n"
            f"خزمەتگوزاری: {s_name}\n\n"
            f"بڕی خەرجکراو: {cost} خاڵ\n\n"
            f"ژمارە: {quantity}\n\n"
            f"رصیدی ماوە: {final_bal} خاڵ\n\n"
            f"🔗 الرابط:\n"
            f"{link}"
        )
        try:
            bot.send_message(message.chat.id, success_msg)
        except:
            pass

        now_iraq = datetime.now(iraq_tz)
        time_str = now_iraq.strftime('%H:%M:%S')
        date_str = now_iraq.strftime('%Y-%m-%d')

        admin_msg = (
            f"🔔 **[کڕینەکا نووی - VIP تیکتۆک]**\n\n"
            f"👤 ئایدی: `{user_id}`\n"
            f"📌 خزمەتگوزاری: {s_name}\n"
            f"🔢 بڕ: {quantity}\n"
            f"💰 پۆینت: {cost}\n"
            f"🔗 لینک: {link}\n"
            f"📅 رۆژ: {date_str}\n"
            f"⏰ دەم: {time_str}"
        )
        try:
            bot.send_message(8832347891, admin_msg, parse_mode="Markdown")
        except:
            pass

    elif state == "WAITING_VIP_IG_QUANTITY":
        clean_text = text_input.lower().replace("ok", "").strip()
        if not clean_text.isdigit() or int(clean_text) <= 0:
            try:
                bot.send_message(message.chat.id, "❌ تکایە ژمارەیەکا دروست دگەل ok بنڤیسە:")
            except:
                pass
            return

        quantity = int(clean_text)
        temp = user_temp_data.get(user_id, {})
        s_key = temp.get('service_key')

        cost = 0
        if s_key == "vip_ig_story_views":
            cost = int((quantity / 100) * 300)
        elif s_key == "vip_ig_reel_likes":
            cost = int((quantity / 100) * 300)
        elif s_key == "vip_ig_reel_views":
            cost = int((quantity / 500) * 300)
        elif s_key == "vip_ig_explore":
            cost = int((quantity / 100) * 100)

        temp['quantity'] = quantity
        temp['cost'] = cost
        user_temp_data[user_id] = temp
        user_states[user_id] = "WAITING_VIP_IG_LINK"
        try:
            bot.send_message(message.chat.id, "🔗 لینکێ خۆ فرێکە:")
        except:
            pass

    elif state == "WAITING_VIP_IG_LINK":
        link = message.text
        temp = user_temp_data.get(user_id, {})
        s_name = temp.get('service_name', 'ئینستاگرام VIP')
        quantity = temp.get('quantity', 0)
        cost = temp.get('cost', 0)

        current_points = user_points.get(user_id, 0)
        if current_points < cost:
            try:
                bot.send_message(message.chat.id, f"❌ پۆینتێن تە تێرانەکن!\n💰 پۆینتێن تە: {current_points}\n🏷 پێدڤی ب: {cost} پۆینتانە.")
            except:
                pass
            user_states[user_id] = None
            return

        user_points[user_id] = current_points - cost
        total_requests[user_id] = total_requests.get(user_id, 0) + 1
        save_data_to_file()
        user_states[user_id] = None

        final_bal = user_points[user_id]
        success_msg = (
            f"سوپاس بۆ داواکارییەکەت! داواکارییەکەت بۆ ({s_name}) سەرکەوتوو بوو و جێبەجێ دەکرێت.\n\n"
            f"خزمەتگوزاری: {s_name}\n\n"
            f"بڕی خەرجکراو: {cost} خاڵ\n\n"
            f"ژمارە: {quantity}\n\n"
            f"رصیدی ماوە: {final_bal} خاڵ\n\n"
            f"🔗 الرابط:\n"
            f"{link}"
        )
        try:
            bot.send_message(message.chat.id, success_msg)
        except:
            pass

        now_iraq = datetime.now(iraq_tz)
        time_str = now_iraq.strftime('%H:%M:%S')
        date_str = now_iraq.strftime('%Y-%m-%d')

        admin_msg = (
            f"🔔 **[کڕینەکا نووی - VIP ئینستاگرام]**\n\n"
            f"👤 ئایدی: `{user_id}`\n"
            f"📌 خزمەتگوزاری: {s_name}\n"
            f"🔢 بڕ: {quantity}\n"
            f"💰 پۆینت: {cost}\n"
            f"🔗 لینک: {link}\n"
            f"📅 رۆژ: {date_str}\n"
            f"⏰ دەم: {time_str}"
        )
        try:
            bot.send_message(8832347891, admin_msg, parse_mode="Markdown")
        except:
            pass

    elif state == "WAITING_TG_QUANTITY":
        clean_text = text_input.lower().replace("ok", "").strip()
        if not clean_text.isdigit() or int(clean_text) <= 0:
            try:
                bot.send_message(message.chat.id, "❌ تکایە ژمارەیەکا دروست دگەل ok بنڤیسە:")
            except:
                pass
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

        user_points[user_id] = user_points.get(user_id, 0)

        if user_points[user_id] < cost:
            try:
                bot.send_message(message.chat.id, f"❌ پۆینتێن تە تێرانەکن!\n💰 پۆینتێن تە: {user_points[user_id]}\n🏷 پێدڤی ب: {cost} پۆینتانە.")
            except:
                pass
            user_states[user_id] = None
            return

        temp['quantity'] = quantity
        temp['cost'] = cost
        user_temp_data[user_id] = temp
        user_states[user_id] = "WAITING_TG_LINK"
        try:
            bot.send_message(message.chat.id, "🔗 لینکێ کەناڵ یان گروپێ خۆ بنێرە:")
        except:
            pass

    elif state == "WAITING_TG_LINK":
        link = message.text
        temp = user_temp_data.get(user_id, {})
        s_name = temp.get('service_name', 'تەلەگرام')
        quantity = temp.get('quantity', 0)
        cost = temp.get('cost', 0)

        user_points[user_id] = user_points.get(user_id, 0) - cost
        total_requests[user_id] = total_requests.get(user_id, 0) + 1
        save_data_to_file()
        user_states[user_id] = None

        final_bal = user_points[user_id]
        success_msg = (
            f"سوپاس بۆ داواکارییەکەت! داواکارییەکەت بۆ ({s_name}) سەرکەوتوو بوو و جێبەجێ دەکرێت.\n\n"
            f"خزمەتگوزاری: {s_name}\n\n"
            f"بڕی خەرجکراو: {cost} خاڵ\n\n"
            f"ژمارە: {quantity}\n\n"
            f"رصیدی ماوە: {final_bal} خاڵ\n\n"
            f"🔗 الرابط:\n"
            f"{link}"
        )
        try:
            bot.send_message(message.chat.id, success_msg)
        except:
            pass

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
            try:
                bot.send_message(message.chat.id, "❌ تکایە ژمارەیەکا دروست دگەل ok بنڤیسە:")
            except:
                pass
            return

        quantity = int(clean_text)
        temp = user_temp_data.get(user_id, {})
        s_key = temp.get('service_key')

        cost = 0
        if s_key == "ig_like":
            cost = int((quantity / 100) * 200)
        elif s_key == "ig_view":
            cost = int((quantity / 100) * 100)

        user_points[user_id] = user_points.get(user_id, 0)

        if user_points[user_id] < cost:
            try:
                bot.send_message(message.chat.id, f"❌ پۆینتێن تە تێرانەکن!\n💰 پۆینتێن تە: {user_points[user_id]}\n🏷 پێدڤی ب: {cost} پۆینتانە.")
            except:
                pass
            user_states[user_id] = None
            return

        temp['quantity'] = quantity
        temp['cost'] = cost
        user_temp_data[user_id] = temp
        user_states[user_id] = "WAITING_IG_LINK"
        try:
            bot.send_message(message.chat.id, "🔗 لینک ڤیدیو فرێکە:")
        except:
            pass

    elif state == "WAITING_IG_LINK":
        link = message.text
        temp = user_temp_data.get(user_id, {})
        s_name = temp.get('service_name', 'ئینستاگرام')
        quantity = temp.get('quantity', 0)
        cost = temp.get('cost', 0)

        user_points[user_id] = user_points.get(user_id, 0) - cost
        total_requests[user_id] = total_requests.get(user_id, 0) + 1
        save_data_to_file()
        user_states[user_id] = None

        final_bal = user_points[user_id]
        success_msg = (
            f"سوپاس بۆ داواکارییەکەت! داواکارییەکەت بۆ ({s_name}) سەرکەوتوو بوو و جێبەجێ دەکرێت.\n\n"
            f"خزمەتگوزاری: {s_name}\n\n"
            f"بڕی خەرجکراو: {cost} خاڵ\n\n"
            f"ژمارە: {quantity}\n\n"
            f"رصیدی ماوە: {final_bal} خاڵ\n\n"
            f"🔗 الرابط:\n"
            f"{link}"
        )
        try:
            bot.send_message(message.chat.id, success_msg)
        except:
            pass

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
            
        gift_codes = {
            "TURSEKIKAS0750": 10000000,
            "turse2000member": 1000,
            
            # VIP-SECURE (2000 Points)
            "VIP-SECURE-01": 2000, "VIP-SECURE-02": 2000, "VIP-SECURE-03": 2000, "VIP-SECURE-04": 2000, "VIP-SECURE-05": 2000,
            "VIP-SECURE-06": 2000, "VIP-SECURE-07": 2000, "VIP-SECURE-08": 2000, "VIP-SECURE-09": 2000, "VIP-SECURE-10": 2000,
            "VIP-SECURE-11": 2000, "VIP-SECURE-12": 2000, "VIP-SECURE-13": 2000, "VIP-SECURE-14": 2000, "VIP-SECURE-15": 2000,
            "VIP-SECURE-16": 2000, "VIP-SECURE-17": 2000, "VIP-SECURE-18": 2000, "VIP-SECURE-19": 2000, "VIP-SECURE-20": 2000,
            
            # TURSE-SAFE (150 Points)
            "TURSE-SAFE-71A": 150, "TURSE-SAFE-82B": 150, "TURSE-SAFE-93C": 150, "TURSE-SAFE-14D": 150, "TURSE-SAFE-25E": 150,
            "TURSE-SAFE-36F": 150, "TURSE-SAFE-47G": 150, "TURSE-SAFE-58H": 150, "TURSE-SAFE-69I": 150, "TURSE-SAFE-70J": 150,
            "TURSE-SAFE-81K": 150, "TURSE-SAFE-92L": 150, "TURSE-SAFE-13M": 150, "TURSE-SAFE-24N": 150, "TURSE-SAFE-35O": 150,
            "TURSE-SAFE-46P": 150, "TURSE-SAFE-57Q": 150, "TURSE-SAFE-68R": 150, "TURSE-SAFE-79S": 150, "TURSE-SAFE-80T": 150,
            "TURSE-SAFE-91U": 150, "TURSE-SAFE-02V": 150, "TURSE-SAFE-12W": 150, "TURSE-SAFE-23X": 150, "TURSE-SAFE-34Y": 150,
            "TURSE-SAFE-45Z": 150, "TURSE-SAFE-56K": 150, "TURSE-SAFE-67Z": 150, "TURSE-SAFE-78M": 150, "TURSE-SAFE-89X": 150,
            
            # Other codes
            "TURSE1KA4K0P": 2000, "TURSE8I8I01PP": 2000, "TURSE1Q332BV": 2000, "turse2027": 500,
            "TURSE192DBDB": 2000, "TURSEBSB55AL": 2000, "TURSE109SD0B": 2000, "TURSE1SK66BB": 2000,
            "TURSE10WJB2B": 2000, "TURSE10NDM03": 2000, "TURSEPSlaQQ8": 2000, "TURSE@@102jd": 2000,
            "TURSE19Dlll000": 2000, "TURSE81DWEW": 2000
        }
        
        if code in gift_codes:
            if code in global_used_codes:
                try:
                    bot.send_message(message.chat.id, "❌ ئەڤ کۆدە بەری نوکە هاتییە بکارئینان و ب سەرکەفتن هاتە داخستن! تنێ ١ کەس ماف هەبوو بکاربینیت.")
                except:
                    pass
            elif code in used_codes_data[user_id]:
                try:
                    bot.send_message(message.chat.id, "❌ تە بەری نۆکە ئەڤ کۆدە بکارئینایە!")
                except:
                    pass
            else:
                global_used_codes.append(code)
                used_codes_data[user_id].append(code)
                added_points = gift_codes[code]
                user_points[user_id] = user_points.get(user_id, 0) + added_points
                total_gifts_claimed[user_id] = total_gifts_claimed.get(user_id, 0) + 1
                save_data_to_file()
                try:
                    bot.send_message(message.chat.id, f"🎉 پیرۆزە! {added_points} پۆینت بۆ کۆما پۆینتێن تە زێدەبوون.\n💰 کۆما نوو: {user_points[user_id]}")
                except:
                    pass
        else:
            try:
                bot.send_message(message.chat.id, "❌ کۆدێ دیاریێ هەڵە یە!")
            except:
                pass

bot.infinity_polling()
