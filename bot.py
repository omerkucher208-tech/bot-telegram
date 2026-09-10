pyTelegramBotAPI
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timezone, timedelta

TOKEN = "8842143426:AAEt-8OhhfrpmDeN1ibXyn3DYYGb2tCqTvs"
ADMIN_ID = 8832347891
CHANNEL_USERNAME = "@TURSE_INFO"

bot = telebot.TeleBot(TOKEN)

user_points = {}
last_bonus_date = {}
user_states = {}
user_temp_data = {}
invited_counts = {}
vip_users = {}

iraq_tz = timezone(timedelta(hours=3))

def check_user_membership(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
    except Exception as e:
        print(f"Error checking membership: {e}")
        return True  
    return False

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    
    if not check_user_membership(user_id):
        show_force_sub_message(message.chat.id)
        return

    args = message.text.split()
    if len(args) > 1 and args[1].isdigit():
        ref_id = int(args[1])
        if ref_id != user_id and user_id not in user_points:
            user_points[ref_id] = user_points.get(ref_id, 1487) + 100
            invited_counts[ref_id] = invited_counts.get(ref_id, 0) + 1

    if user_id not in user_points:
        user_points[user_id] = 1487
        
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
    points = user_points.get(user_id, 1487)
    
    text = (
        "💎 - بەخێرهاتن بۆ بۆتا دەنگدانا کوردی\n"
        f"💰 - پۆینتێن تە: {points}\n\n"
        "- تکایە یەکێ ژ وان یێن خوارێ هەڵبژێرە:"
    )
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🎁 بەشێ فەیک", callback_data="menu_fake"))
    markup.add(InlineKeyboardButton("⭐ ڤەکرنا بەشێ VIP", callback_data="vip"))
    markup.add(InlineKeyboardButton("🌟 تورسی تایبەت (دەرەوەی VIP)", callback_data="special_tursi"))
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
            bot.answer_callback_query(call.id, "✅ سوپاس، تە جۆین کر! بۆت بۆ تە ڤەبوو.", show_alert=True)
            if user_id not in user_points:
                user_points[user_id] = 1487
            show_main_menu(call.message.chat.id, call.message.message_id, is_new=False)
        else:
            bot.answer_callback_query(call.id, "❌ هێشتا تە جۆین نەکریە! تکایە سەرەتا جۆین کە.", show_alert=True)
        return

    if not check_user_membership(user_id):
        bot.answer_callback_query(call.id, "⚠️ پێدڤیە سەرەتا جۆینێ کەناڵی ببی!", show_alert=True)
        return

    if user_id not in user_points:
        user_points[user_id] = 1487

    if call.data == "daily_bonus":
        current_date = datetime.now(iraq_tz).strftime('%Y-%m-%d')
        
        if last_bonus_date.get(user_id) == current_date:
            bot.answer_callback_query(
                call.id, 
                "⚠️ تە دیاریا ئەڤرۆ وەرگرتییە! تکایە سبەهی پاش سەعات ١٢ی شەڤێ سەرەدانا مە بکە.", 
                show_alert=True
            )
        else:
            last_bonus_date[user_id] = current_date
            user_points[user_id] += 10
            current_points = user_points[user_id]
            bot.answer_callback_query(
                call.id, 
                f"🎉 پیرۆزە! 10 پۆینتێن دیاریا ڕۆژانە بۆ تە زێدەبوون.\n💰 کۆما پۆینتێن تە: {current_points}", 
                show_alert=True
            )
        show_main_menu(call.message.chat.id, call.message.message_id)
        
    elif call.data == "ref_link":
        bot_info = bot.get_me()
        ref_url = f"https://t.me/{bot_info.username}?start={user_id}"
        invites_num = invited_counts.get(user_id, 0)
        
        msg_text = (
            f"🔗 **لینکێ ئینڤایتێ (Invite) یێ تە:**\n"
            f"`{ref_url}`\n\n"
            f"👥 **چەند کەس ئیناینە؟** {invites_num} کەس\n"
            f"💰 **پاداشت:** بۆ هەر کەسەکی 100 پۆینت!\n\n"
            "*(تکایە لینکێ خۆ کۆپی بکە و بۆ هەڤالێن خۆ بنێرە)*"
        )
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, msg_text, parse_mode="Markdown")

    elif call.data == "special_tursi":
        text = (
            "🌟 **بەخێرهاتن بۆ بەشی تورسی تایبەت!**\n\n"
            "ئەم بەشە تایبەتە ب خزمەتگوزاری و نووترین ئەپدەیتێن تورسی. یەکەک لە بژاردەکانی خوارەوە هەڵبژێرە:"
        )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📢 کەناڵێ ڕەسمی تورسی", url="https://t.me/TURSE_INFO"))
        markup.add(InlineKeyboardButton("🔙 ڤەگەر بۆ مێنویێ سەرەکی", callback_data="back_home"))
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
        
    elif call.data == "menu_fake":
        user_states[user_id] = None
        text = "🎁 - فەرموو بەشێ فەیک هەڵبژێرە:"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("✈️ تەلەگرام", callback_data="fake_telegram"))
        markup.add(InlineKeyboardButton("🎵 تیکتۆک", callback_data="fake_tiktok"))
        markup.add(InlineKeyboardButton("📸 ئینستگرام", callback_data="fake_instagram"))
        markup.add(InlineKeyboardButton("👻 سناپچات", callback_data="fake_snapchat"))
        markup.add(InlineKeyboardButton("🔙 ڤەگەر", callback_data="back_home"))
        
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)
        
    elif call.data == "fake_telegram":
        user_states[user_id] = None
        text = "✈️ - بەشێ تەلەگرام هاتە هەڵبژاردن، خزمەتگوزاریا خۆ دیار بکە:"
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("👍 ڕیاکشن", callback_data="tg_reaction"),
            InlineKeyboardButton("❤️ دلک", callback_data="tg_heart")
        )
        markup.add(
            InlineKeyboardButton("👥 مێمبەر", callback_data="tg_member"),
            InlineKeyboardButton("👁 بینەر", callback_data="tg_view")
        )
        markup.add(InlineKeyboardButton("🔙 ڤەگەر", callback_data="menu_fake"))
        
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)
        
    elif call.data in ["tg_reaction", "tg_heart"]:
        user_states[user_id] = "WAITING_FOR_REACTION_LINK"
        service_name = "ڕیاکشن/دلک" if call.data == "tg_reaction" else "دلک"
        user_temp_data[user_id] = {'service': service_name}
        bot.send_message(call.message.chat.id, "بەرێز زەحمەت نەبیت لینکێ پۆستێ خۆ فرێکە (1 ڕیاکشن = 5 پۆینت):")
        bot.answer_callback_query(call.id)
        
    elif call.data == "tg_member":
        user_states[user_id] = "WAITING_FOR_MEMBER_LINK"
        user_temp_data[user_id] = {'service': "مێمبەر"}
        bot.send_message(call.message.chat.id, "لینکێ کەناڵ یان گروپێ خۆ بدە (1 مێمبەر = 15 پۆینت):")
        bot.answer_callback_query(call.id)

    elif call.data == "tg_view":
        user_states[user_id] = "WAITING_FOR_VIEW_LINK"
        user_temp_data[user_id] = {'service': "بینەر"}
        bot.send_message(call.message.chat.id, "لینکێ پۆستێ خۆ فرێکە (1 بینەر = 3 پۆینت):")
        bot.answer_callback_query(call.id)
        
    elif call.data == "back_home":
        user_states[user_id] = None
        show_main_menu(call.message.chat.id, call.message.message_id)
        
    elif call.data == "vip":
        if vip_users.get(user_id, False):
            show_vip_menu(call.message.chat.id, call.message.message_id)
        else:
            text = (
                "⭐ **کرنا بەشێ VIP**\n\n"
                "💎 بۆ ڤەکرنا بەشێ VIP پێدڤیە **1000 پۆینت** ژ ئەکاونتێ تە بهێنە خار.\n"
                "ئایا دخوازەی ڤی بەشی بکڕی؟"
            )
            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton("✅ YES (کڕین)", callback_data="vip_buy_yes"),
                InlineKeyboardButton("❌ NO (پاشڤە هاتن)", callback_data="vip_buy_no")
            )
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
            
    elif call.data == "vip_buy_yes":
        user_balance = user_points.get(user_id, 1487)
        if user_balance >= 1000:
            user_points[user_id] -= 1000
            vip_users[user_id] = True
            bot.answer_callback_query(call.id, "🎉 پیرۆزە! بەشێ VIP بۆ تە هاتە ڤەکرن.", show_alert=True)
            show_vip_menu(call.message.chat.id, call.message.message_id)
        else:
            bot.answer_callback_query(call.id, f"❌ پۆینتێن تە بەش ناکەن! پێتڤی: 1000 پۆینت، یێن تە: {user_balance}", show_alert=True)
            show_main_menu(call.message.chat.id, call.message.message_id)
            
    elif call.data == "vip_buy_no":
        bot.answer_callback_query(call.id, "❌ کرینا VIP هاتە هەڵوەشاندن.", show_alert=False)
        show_main_menu(call.message.chat.id, call.message.message_id)
        
    elif call.data == "vip_telegram":
        text = "✈️ **بەشێ VIP - تەلەگرام**\nخزمەتگوزاریا خۆ هەڵبژێرە:"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("👥 مێمبەرێت زەمان 60 ڕۆژ", callback_data="vip_tg_member_60"))
        markup.add(InlineKeyboardButton("❤️ دلک/دەنگ (ئینگلیزی 🇺🇸)", callback_data="vip_tg_vote_en"))
        markup.add(InlineKeyboardButton("🔙 ڤەگەر بۆ VIP", callback_data="vip"))
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
        
    elif call.data == "vip_instagram":
        bot.answer_callback_query(call.id, "📸 بەشێ VIP - ئینستگرام بزوی زێدە دبت.", show_alert=True)

    elif call.data == "vip_special_tursi":
        text = "🌟 **بەشێ VIP - تورسی تایبەت**\nخزمەتگوزاریا خۆ هەڵبژێرە:"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("⚽ COIN PES", callback_data="vip_coin_pes"))
        markup.add(InlineKeyboardButton("🎮 UC PUBG", callback_data="vip_uc_pubg"))
        markup.add(InlineKeyboardButton("🔙 ڤەگەر بۆ VIP", callback_data="vip"))
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "vip_coin_pes":
        user_states[user_id] = "WAITING_VIP_COIN_PES"
        user_temp_data[user_id] = {'service': "COIN PES (VIP)"}
        bot.send_message(call.message.chat.id, "⚽ ئایدی یان زانیاریێن خۆ بۆ وەرگرتنا **COIN PES** بنێرە:")
        bot.answer_callback_query(call.id)

    elif call.data == "vip_uc_pubg":
        user_states[user_id] = "WAITING_VIP_UC_PUBG"
        user_temp_data[user_id] = {'service': "UC PUBG (VIP)"}
        bot.send_message(call.message.chat.id, "🎮 ئایدی (ID) یان ناڤێ خۆ بۆ وەرگرتنا **UC PUBG** بنێرە:")
        bot.answer_callback_query(call.id)
        
    elif call.data == "vip_tg_member_60":
        user_states[user_id] = "WAITING_VIP_TG_MEMBER_LINK"
        user_temp_data[user_id] = {'service': "مێمبەر 60 ڕۆژ (VIP)"}
        bot.send_message(call.message.chat.id, "🔗 لینکێ کەناڵ یان گروپێ خۆ بۆ مێمبەرێن زەمان 60 ڕۆژ بنێرە:")
        bot.answer_callback_query(call.id)
        
    elif call.data == "vip_tg_vote_en":
        user_states[user_id] = "WAITING_VIP_VOTE_EN_LINK"
        user_temp_data[user_id] = {'service': "دلک/دەنگ ئینگلیزی (VIP)"}
        bot.send_message(call.message.chat.id, "🔗 لینکێ پۆستێ خۆ بۆ دلک/دەنگی ئینگلیزی (🇺🇸) بنێرە:\n*(نرخ: هەر دلکەک = 30 پۆینت)*")
        bot.answer_callback_query(call.id)

    elif call.data.startswith("tg_"):
        sub_type = call.data.split("_")[1]
        bot.answer_callback_query(call.id, f"خزمەتگوزاریا تەلەگرام ({sub_type}) هاتە هەڵبژاردن.", show_alert=False)
        
    elif call.data.startswith("fake_"):
        platform = call.data.split("_")[1]
        bot.answer_callback_query(call.id, f"بەشێ فەیکیێ {platform} هاتە هەڵبژاردن.", show_alert=False)
        
    elif call.data == "code":
        bot.answer_callback_query(call.id, "🎟 فەرموو کۆدێ دیاریا خۆ بنڤیسە.", show_alert=False)

def show_vip_menu(chat_id, message_id):
    text = "⭐ **بەشێ تایبەتێ VIP**\nبەشەک هەڵبژێرە:"
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✈️ تەلەگرام (VIP)", callback_data="vip_telegram"))
    markup.add(InlineKeyboardButton("📸 ئینستگرام (VIP)", callback_data="vip_instagram"))
    markup.add(InlineKeyboardButton("🌟 تورسی تایبەت (VIP)", callback_data="vip_special_tursi"))
    markup.add(InlineKeyboardButton("🔙 ڤەگەر بۆ مێنویێ سەرەکی", callback_data="back_home"))
    try:
        bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")
    except:
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_text_steps(message):
    user_id = message.from_user.id
    
    if not check_user_membership(user_id):
        show_force_sub_message(message.chat.id)
        return

    state = user_states.get(user_id)
    
    if state == "WAITING_FOR_REACTION_LINK":
        if user_id not in user_temp_data:
            user_temp_data[user_id] = {}
        user_temp_data[user_id]['link'] = message.text
        user_states[user_id] = "WAITING_FOR_REACTION_COUNT"
        bot.send_message(message.chat.id, "• باشە، چەند دەنک/ڕیاکشن دڤێن ب ژمارە بنێرە:")
        
    elif state == "WAITING_FOR_REACTION_COUNT":
        try:
            count = int(message.text)
        except ValueError:
            bot.send_message(message.chat.id, "❌ تکایە تنێ ژمارە بنێرە:")
            return
            
        required_points = count * 5
        user_balance = user_points.get(user_id, 0)
        
        if user_balance < required_points:
            bot.send_message(
                message.chat.id, 
                f"❌ پۆینتێن ئەکاونتێ تە بەش ناکەن!\n"
                f"💰 پۆینتێن تە: {user_balance} | پێتڤی: {required_points}\n"
                "بەرێز، پۆینتێن خۆ پڕ بکە..."
            )
            user_states[user_id] = None
        else:
            user_points[user_id] -= required_points
            service_name = user_temp_data.get(user_id, {}).get('service', 'ڕیاکشن')
            link = user_temp_data.get(user_id, {}).get('link', 'نەدیار')
            
            user_states[user_id] = None
            bot.send_message(
                message.chat.id, 
                f"✅ پیرۆزە، داخوازیا تە هاتە بجهئینان!\n"
                f"💰 پۆینتێن مای ل ئەکاونتێ تە: {user_points[user_id]}"
            )
            admin_msg = (
                f"🚨 داخوازەکا نوی هاتە کرن!\n\n"
                f"👤 ئایدیا بکاربەری: `{user_id}`\n"
                f"📌 جۆرێ خزمەتگوزاریێ: {service_name}\n"
                f"🔗 لینک: {link}\n"
                f"🔢 ژمارە: {count}\n"
                f"💎 پۆینتێن هاتینە خار: {required_points}"
            )
            bot.send_message(ADMIN_ID, admin_msg, parse_mode="Markdown")

    elif state == "WAITING_FOR_MEMBER_LINK":
        if user_id not in user_temp_data:
            user_temp_data[user_id] = {}
        user_temp_data[user_id]['link'] = message.text
        user_states[user_id] = "WAITING_FOR_MEMBER_COUNT"
        bot.send_message(message.chat.id, "چەند مێمبەر دڤێن ب ژمارە بنێرە:")
        
    elif state == "WAITING_FOR_MEMBER_COUNT":
        try:
            count = int(message.text)
        except ValueError:
            bot.send_message(message.chat.id, "❌ تکایە تنێ ژمارە بنێرە:")
            return
            
        required_points = count * 15
        user_balance = user_points.get(user_id, 0)
        
        if user_balance < required_points:
            bot.send_message(
                message.chat.id, 
                f"❌ پۆینتێن ئەکاونتێ تە بەش ناکەن!\n"
                f"💰 پۆینتێن تە: {user_balance} | پێتڤی: {required_points}\n"
                "بەرێز، پۆینتێن خۆ پڕ بکە..."
            )
            user_states[user_id] = None
        else:
            user_points[user_id] -= required_points
            service_name = user_temp_data.get(user_id, {}).get('service', 'مێمبەر')
            link = user_temp_data.get(user_id, {}).get('link', 'نەدیار')
            
            user_states[user_id] = None
            bot.send_message(
                message.chat.id, 
                f"✅ پیرۆزە، داخوازیا تە هاتە بجهئینان!\n"
                f"💰 پۆینتێن مای ل ئەکاونتێ تە: {user_points[user_id]}"
            )
            admin_msg = (
                f"🚨 داخوازەکا نوی هاتە کرن!\n\n"
                f"👤 ئایدیا بکاربەری: `{user_id}`\n"
                f"📌 جۆرێ خزمەتگوزاریێ: {service_name}\n"
                f"🔗 لینک: {link}\n"
                f"🔢 ژمارە: {count}\n"
                f"💎 پۆینتێن هاتینە خار: {required_points}"
            )
            bot.send_message(ADMIN_ID, admin_msg, parse_mode="Markdown")

    elif state == "WAITING_FOR_VIEW_LINK":
        if user_id not in user_temp_data:
            user_temp_data[user_id] = {}
        user_temp_data[user_id]['link'] = message.text
        user_states[user_id] = "WAITING_FOR_VIEW_COUNT"
        bot.send_message(message.chat.id, "چەند بینەر دڤێن ب ژمارە بنێرە:")
        
    elif state == "WAITING_FOR_VIEW_COUNT":
        try:
            count = int(message.text)
        except ValueError:
            bot.send_message(message.chat.id, "❌ تکایە تنێ ژمارە بنێرە:")
            return
            
        required_points = count * 3
        user_balance = user_points.get(user_id, 0)
        
        if user_balance < required_points:
            bot.send_message(
                message.chat.id, 
                f"❌ پۆینتێن ئەکاونتێ تە بەش ناکەن!\n"
                f"💰 پۆینتێن تە: {user_balance} | پێتڤی: {required_points}\n"
                "بەرێز، پۆینتێن خۆ پڕ بکە..."
            )
            user_states[user_id] = None
        else:
            user_points[user_id] -= required_points
            service_name = user_temp_data.get(user_id, {}).get('service', 'بینەر')
            link = user_temp_data.get(user_id, {}).get('link', 'نەدیار')
            
            user_states[user_id] = None
            bot.send_message(
                message.chat.id, 
                f"✅ پیرۆزە، داخوازیا تە هاتە بجهئینان!\n"
                f"💰 پۆینتێن مای ل ئەکاونتێ تە: {user_points[user_id]}"
            )
            admin_msg = (
                f"🚨 داخوازەکا نوی هاتە کرن!\n\n"
                f"👤 ئایدیا بکاربەری: `{user_id}`\n"
                f"📌 جۆرێ خزمەتگوزاریێ: {service_name}\n"
                f"🔗 لینک: {link}\n"
                f"🔢 ژمارە: {count}\n"
                f"💎 پۆینتێن هاتینە خار: {required_points}"
            )
            bot.send_message(ADMIN_ID, admin_msg, parse_mode="Markdown")

    elif state == "WAITING_VIP_TG_MEMBER_LINK":
        if user_id not in user_temp_data:
            user_temp_data[user_id] = {}
        user_temp_data[user_id]['link'] = message.text
        user_states[user_id] = "WAITING_VIP_TG_MEMBER_COUNT"
        bot.send_message(message.chat.id, "• چەند مێمبەرێن زەمان 60 ڕۆژ دڤێن؟ ب ژمارە بنێرە:")

    elif state == "WAITING_VIP_TG_MEMBER_COUNT":
        try:
            count = int(message.text)
        except ValueError:
            bot.send_message(message.chat.id, "❌ تکایە تنێ ژمارە بنێرە:")
            return
            
        required_points = count * 20
        user_balance = user_points.get(user_id, 0)
        
        if user_balance < required_points:
            bot.send_message(
                message.chat.id, 
                f"❌ پۆینتێن تە بەش ناکەن!\n"
                f"💰 پۆینتێن تە: {user_balance} | پێتڤی: {required_points}"
            )
            user_states[user_id] = None
        else:
            user_points[user_id] -= required_points
            link = user_temp_data.get(user_id, {}).get('link', 'نەدیار')
            user_states[user_id] = None
            bot.send_message(
                message.chat.id, 
                f"✅ داخوازیا مێمبەرێن زەمان 60 ڕۆژ هاتە وەرگرتن!\n"
                f"💰 پۆینتێن مای: {user_points[user_id]}"
            )
            admin_msg = (
                f"⭐ **داخوازەکا VIP (مێمبەر 60 ڕۆژ)**\n\n"
                f"👤 ئایدی: `{user_id}`\n"
                f"🔗 لینک: {link}\n"
                f"🔢 ژمارە: {count}\n"
                f"💎 پۆینتێن هاتینە خار: {required_points}"
            )
            bot.send_message(ADMIN_ID, admin_msg, parse_mode="Markdown")

    elif state == "WAITING_VIP_VOTE_EN_LINK":
        if user_id not in user_temp_data:
            user_temp_data[user_id] = {}
        user_temp_data[user_id]['link'] = message.text
        user_states[user_id] = "WAITING_VIP_VOTE_EN_COUNT"
        bot.send_message(message.chat.id, "• چەند دلک/دەنگێن ئینگلیزی (🇺🇸) دڤێن؟ (هەر یەک = 30 پۆینت):")

    elif state == "WAITING_VIP_VOTE_EN_COUNT":
        try:
            count = int(message.text)
        except ValueError:
            bot.send_message(message.chat.id, "❌ تکایە تنێ ژمارە بنێرە:")
            return
            
        required_points = count * 30
        user_balance = user_points.get(user_id, 0)
        
        if user_balance < required_points:
            bot.send_message(
                message.chat.id, 
                f"❌ پۆینتێن ئەکاونتێ تە بەش ناکەن!\n"
                f"💰 پۆینتێن تە: {user_balance} | پێتڤی: {required_points}\n"
                "بەرێز، پۆینتێن خۆ پڕ بکە..."
            )
            user_states[user_id] = None
        else:
            user_points[user_id] -= required_points
            link = user_temp_data.get(user_id, {}).get('link', 'نەدیار')
            
            user_states[user_id] = None
            bot.send_message(
                message.chat.id, 
                f"✅ پیرۆزە، داخوازیا دلکێن ئینگلیزی هاتە بجهئینان!\n"
                f"💰 پۆینتێن مای ل ئەکاونتێ تە: {user_points[user_id]}"
            )
            admin_msg = (
                f"⭐ **داخوازەکا VIP (دلک/دەنگ ئینگلیزی 🇺🇸)**\n\n"
                f"👤 ئاییدیا بکاربەری: `{user_id}`\n"
                f"🔗 لینک: {link}\n"
                f"🔢 ژمارە: {count}\n"
                f"💎 پۆینتێن هاتینە خار: {required_points} (هەر یەک 30 پۆینت)"
            )
            bot.send_message(ADMIN_ID, admin_msg, parse_mode="Markdown")

    elif state in ["WAITING_VIP_COIN_PES", "WAITING_VIP_UC_PUBG"]:
        info_text = message.text
        service_name = user_temp_data.get(user_id, {}).get('service', 'تورسی تایبەت')
        user_states[user_id] = None
        
        bot.send_message(
            message.chat.id, 
            f"✅ زانیاریێن تە بۆ ({service_name}) ب سەرکەفتیانە هاتنە وەرگرتن!\n"
            "ئەدمین دێ زوو لێ هۆشدار بیت."
        )
        
        admin_msg = (
            f"🌟 **داخوازەکا نووی (تورسی تایبەت - VIP)**\n\n"
            f"👤 ئایدییا بکاربەری: `{user_id}`\n"
            f"📌 خزمەتگوزاری: {service_name}\n"
            f"📝 زانیاری / ئایدی: {info_text}"
        )
        bot.send_message(ADMIN_ID, admin_msg, parse_mode="Markdown")
            
    else:
        pass

bot.infinity_polling()
