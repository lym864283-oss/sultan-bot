import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests

TOKEN = os.getenv("BOT_TOKEN")
API_KEY = os.getenv("API_KEY")
SMM_API_URL = "https://smm-provider-api.com/api/v2" 

if not TOKEN:
    raise ValueError("BOT_TOKEN is not set in environment variables.")

bot = telebot.TeleBot(TOKEN)

def main_menu_keyboard():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("الخدمات", callback_data="services"),
        InlineKeyboardButton("طلباتي", callback_data="orders"),
        InlineKeyboardButton("رصيدي", callback_data="balance"),
        InlineKeyboardButton("المساعدة", callback_data="support"),
        InlineKeyboardButton("لوحة المشرف", callback_data="admin_panel")
    )
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "مرحباً بك في متجر الخدمات الرقمية.\n"
        "اختر من القائمة لعرض الخدمات أو متابعة طلباتك ورصيدك."
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu_keyboard())

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "services":
        try:
            payload = {
                'key': API_KEY,
                'action': 'services'
            }
            response = requests.post(SMM_API_URL, data=payload, timeout=10)
            
            if response.status_code == 401:
                bot.answer_callback_query(call.id, "خطأ 401: مفتاح الربط غير صالح!", show_alert=True)
                
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton("إعادة المحاولة", callback_data="services"))
                markup.add(InlineKeyboardButton("القائمة الرئيسية", callback_data="main_menu"))
                
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text="❌ **تعذر تحميل الخدمات من المزود:** أعاد مزود الخدمة رمز **HTTP 401**.\nتأكد من صحة مفتاح الـ API المضاف في إعدادات المنصة.",
                    reply_markup=markup,
                    parse_mode="Markdown"
                )
                return
            
            elif response.status_code == 200:
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton("القائمة الرئيسية", callback_data="main_menu"))
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text="📋 **قائمة الخدمات المتاحة:**\nتم الاتصال بالمزود بنجاح.",
                    reply_markup=markup,
                    parse_mode="Markdown"
                )
            else:
                bot.answer_callback_query(call.id, f"رمز الاستجابة: {response.status_code}", show_alert=True)
                
        except Exception as e:
            bot.answer_callback_query(call.id, "حدث خطأ في الاتصال بالخدمة.", show_alert=True)

    elif call.data == "support":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("💬 تواصل مع الدعم المباشر", url="https://t.me/YOUR_USERNAME"))
        markup.add(InlineKeyboardButton("القائمة الرئيسية", callback_data="main_menu"))
        bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text="للتواصل مع الإدارة أو الدعم الفني، اضغط على الزر أدناه:",
                    reply_markup=markup
        )

    elif call.data == "main_menu":
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="القائمة الرئيسية:",
            reply_markup=main_menu_keyboard()
        )

if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling()
