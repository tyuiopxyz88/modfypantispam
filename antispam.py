import telebot
import re

TOKEN = "8169347469:AAEV-8c_KJJ3LO_7TK126G1aiV4rvK4jUtI"
bot = telebot.TeleBot(TOKEN)

warnings = {}

# Hàm kiểm tra tin nhắn có chứa link hay không
def contains_link(message):
    return bool(re.search(r"(https?://|www\.)\S+", message.text, re.IGNORECASE))

# Hàm kiểm tra user có phải admin không
def is_admin(chat_id, user_id):
    try:
        admins = bot.get_chat_administrators(chat_id)
        return any(admin.user.id == user_id for admin in admins)
    except Exception as e:
        print(f"Admin Error: {e}")
        return False  # Nếu không thể lấy danh sách admin, giả định user không phải admin

# Xử lý tin nhắn
@bot.message_handler(func=lambda message: True, content_types=['text'])
def check_message(message):
    chat_id = message.chat.id

    # Nếu tin nhắn đến từ channel liên kết, bỏ qua
    if message.forward_from_chat:
        return  

    # Kiểm tra nếu user là admin → Không kiểm tra link
    if is_admin(chat_id, message.from_user.id):
        return  

    # Nếu tin nhắn chứa link và user không phải admin
    if contains_link(message):
        bot.delete_message(chat_id, message.message_id)

        user_id = message.from_user.id

        # Cảnh cáo hoặc ban nếu vi phạm nhiều lần
        if user_id in warnings:
            warnings[user_id] += 1
        else:
            warnings[user_id] = 1

        if warnings[user_id] == 1:
            bot.send_message(chat_id, f"⚠️ @{message.from_user.username} You are not allowed to post links to the MODFYP community! This is a warning, next time we will ban you from the Group. Please pay attention!")
        elif warnings[user_id] >= 2:
            bot.kick_chat_member(chat_id, user_id)
            bot.send_message(chat_id, f"🚫 @{message.from_user.username} has been banned for posting links to the group! Please note: do not post links to the group to avoid being banned.")

print("Bot Running...")
bot.polling()
