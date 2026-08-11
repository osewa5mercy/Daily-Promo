import os
import logging
import datetime
import random
from telebot import TeleBot, types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
if not BOT_TOKEN:
    logging.error("TELEGRAM_BOT_TOKEN environment variable not set!")
    exit(1)

bot = TeleBot(BOT_TOKEN)

# Simple in-memory storage (for production, use a database)
user_data = {}  # user_id: {"points": 0, "last_visit": None, "streak": 0, "total_visits": 0}

# Daily promos database
DAILY_PROMOS = [
    {
        "title": "🛍️ Fashion Flash",
        "code": "FASHION20",
        "discount": "20% OFF",
        "store": "StyleHub",
        "description": "Get 20% off on all summer collection"
    },
    {
        "title": "🍕 Pizza Deal",
        "code": "PIZZA25",
        "discount": "25% OFF",
        "store": "PizzaWorld",
        "description": "25% off on large pizzas"
    },
    {
        "title": "📚 Book Bundle",
        "code": "BOOKS15",
        "discount": "15% OFF",
        "store": "ReadMore",
        "description": "15% off on all bestsellers"
    },
    {
        "title": "🎮 Game Discount",
        "code": "GAME10",
        "discount": "10% OFF",
        "store": "GameZone",
        "description": "10% off on all new releases"
    },
    {
        "title": "☕ Coffee Break",
        "code": "COFFEE30",
        "discount": "30% OFF",
        "store": "BrewHouse",
        "description": "30% off on all specialty drinks"
    },
    {
        "title": "💻 Tech Special",
        "code": "TECH15",
        "discount": "15% OFF",
        "store": "TechWorld",
        "description": "15% off on all electronics"
    },
    {
        "title": "🏋️ Fitness Gear",
        "code": "FIT20",
        "discount": "20% OFF",
        "store": "FitLife",
        "description": "20% off on all fitness equipment"
    },
    {
        "title": "🎬 Movie Night",
        "code": "MOVIE25",
        "discount": "25% OFF",
        "store": "CinemaHub",
        "description": "25% off on movie tickets"
    },
    {
        "title": "🛒 Grocery Saver",
        "code": "GROCERY10",
        "discount": "10% OFF",
        "store": "FreshMart",
        "description": "10% off on all groceries"
    },
    {
        "title": "✈️ Travel Deal",
        "code": "TRAVEL15",
        "discount": "15% OFF",
        "store": "Wanderlust",
        "description": "15% off on all bookings"
    }
]

# Categories with promos
CATEGORIES = {
    "fashion": {
        "emoji": "👗",
        "name": "Fashion",
        "promos": [
            {"title": "Summer Sale", "code": "SUMMER20", "discount": "20% OFF", "store": "StyleHub"},
            {"title": "Shoe Special", "code": "SHOE15", "discount": "15% OFF", "store": "FootLocker"},
            {"title": "Accessories", "code": "ACC10", "discount": "10% OFF", "store": "AccessoryWorld"}
        ]
    },
    "food": {
        "emoji": "🍕",
        "name": "Food & Dining",
        "promos": [
            {"title": "Pizza Deal", "code": "PIZZA25", "discount": "25% OFF", "store": "PizzaWorld"},
            {"title": "Coffee Break", "code": "COFFEE30", "discount": "30% OFF", "store": "BrewHouse"},
            {"title": "Burger Fest", "code": "BURGER20", "discount": "20% OFF", "store": "BurgerKing"}
        ]
    },
    "tech": {
        "emoji": "💻",
        "name": "Technology",
        "promos": [
            {"title": "Laptop Deal", "code": "LAPTOP15", "discount": "15% OFF", "store": "TechWorld"},
            {"title": "Phone Offer", "code": "PHONE10", "discount": "10% OFF", "store": "PhoneHub"},
            {"title": "Gaming Gear", "code": "GAME20", "discount": "20% OFF", "store": "GameZone"}
        ]
    },
    "travel": {
        "emoji": "✈️",
        "name": "Travel",
        "promos": [
            {"title": "Flight Deal", "code": "FLY15", "discount": "15% OFF", "store": "Wanderlust"},
            {"title": "Hotel Special", "code": "HOTEL20", "discount": "20% OFF", "store": "StayInn"},
            {"title": "Tour Package", "code": "TOUR25", "discount": "25% OFF", "store": "ExploreWorld"}
        ]
    }
}

# Streak multipliers (for bonus points)
STREAK_MULTIPLIERS = {
    0: 1.0, 1: 1.0, 2: 1.1, 3: 1.2, 4: 1.3,
    5: 1.5, 7: 2.0, 10: 2.5, 15: 3.0, 30: 5.0
}

# --- Helper Functions ---

def get_streak_multiplier(streak):
    """Get multiplier based on streak length"""
    if streak >= 30:
        return STREAK_MULTIPLIERS[30]
    elif streak >= 15:
        return STREAK_MULTIPLIERS[15]
    elif streak >= 10:
        return STREAK_MULTIPLIERS[10]
    elif streak >= 7:
        return STREAK_MULTIPLIERS[7]
    elif streak >= 5:
        return STREAK_MULTIPLIERS[5]
    elif streak >= 3:
        return STREAK_MULTIPLIERS[3]
    elif streak >= 2:
        return STREAK_MULTIPLIERS[2]
    else:
        return STREAK_MULTIPLIERS[0]

def get_daily_promo():
    """Get random daily promo"""
    return random.choice(DAILY_PROMOS)

def get_category_promos(category):
    """Get promos for specific category"""
    if category in CATEGORIES:
        return CATEGORIES[category]["promos"]
    return []

def can_visit(user_id):
    """Check if user can visit today"""
    if user_id not in user_data:
        return True, None
    
    last_visit = user_data[user_id].get("last_visit")
    if not last_visit:
        return True, None
    
    today = datetime.datetime.now().date()
    last_date = datetime.datetime.fromisoformat(last_visit).date()
    
    if today > last_date:
        return True, None
    elif today == last_date:
        return False, "✅ You already claimed today's promo!"
    else:
        return True, None

def calculate_points(user_id):
    """Calculate points with streak multiplier"""
    base_points = random.randint(5, 15)
    streak = user_data.get(user_id, {}).get("streak", 0)
    multiplier = get_streak_multiplier(streak)
    points = int(base_points * multiplier)
    
    # Random bonus (10% chance)
    if random.random() < 0.10:
        points = points * 2
        return points, "🎉 DOUBLE POINTS!"
    
    return points, ""

def format_promo_message(user_id, promo, points, points_type):
    """Format daily promo message"""
    user_name = user_data[user_id].get("name", "User")
    total_points = user_data[user_id]["points"]
    streak = user_data[user_id]["streak"]
    
    message = (
        f"🎯 **Daily Promo**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 **User:** {user_name}\n"
        f"📅 **Day:** {streak}\n\n"
        f"**{promo['title']}**\n"
        f"🏷️ **Code:** `{promo['code']}`\n"
        f"💰 **Discount:** {promo['discount']}\n"
        f"🏪 **Store:** {promo['store']}\n"
        f"📝 **Details:** {promo['description']}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⭐ **Points:** +{points}\n"
        f"{points_type}\n"
        f"📊 **Total:** {total_points} points\n"
        f"🔥 **Streak:** {streak} days\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
    )
    
    # Motivational messages
    if streak >= 30:
        message += "\n🏆 **PROMO LEGEND!** 30-day streak!"
    elif streak >= 15:
        message += "\n🌟 **AMAZING!** 15 days of deals!"
    elif streak >= 7:
        message += "\n⭐ **GREAT!** One week of savings!"
    elif streak >= 3:
        message += "\n💪 **Keep saving!**"
    elif streak == 1:
        message += "\n🎯 **Day 1!** Come back for more deals!"
    
    return message

def get_leaderboard():
    """Get top 10 users by points"""
    sorted_users = sorted(user_data.items(), key=lambda x: x[1]["points"], reverse=True)
    return sorted_users[:10]

# --- Command Handlers ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Welcome message"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    if user_id not in user_data:
        user_data[user_id] = {
            "points": 0,
            "last_visit": None,
            "streak": 0,
            "total_visits": 0,
            "name": user_name
        }
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🎯 Daily Promo", callback_data="daily_promo"),
        InlineKeyboardButton("📂 Categories", callback_data="categories")
    )
    markup.add(
        InlineKeyboardButton("📊 My Stats", callback_data="my_stats"),
        InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard")
    )
    markup.add(
        InlineKeyboardButton("ℹ️ About", callback_data="about")
    )
    
    welcome_text = (
        f"👋 Welcome, {user_name}!\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 **Daily Promo Bot**\n\n"
        f"Discover the best daily deals!\n"
        f"• 🎯 Daily promo codes\n"
        f"• 📂 Category deals\n"
        f"• ⭐ Earn points\n"
        f"• 🔥 Build streaks\n"
        f"• 🏆 Compete on leaderboard\n\n"
        f"**Start saving now:**"
    )
    
    bot.send_message(
        message.chat.id,
        welcome_text,
        parse_mode='Markdown',
        reply_markup=markup
    )

@bot.message_handler(commands=['promo'])
def daily_promo_command(message):
    """Get daily promo via command"""
    handle_daily_promo(message.chat.id, message.from_user.id)

@bot.message_handler(commands=['categories'])
def categories_command(message):
    """Show categories via command"""
    handle_categories(message.chat.id)

@bot.message_handler(commands=['stats'])
def stats_command(message):
    """Show stats via command"""
    handle_stats(message.chat.id, message.from_user.id)

@bot.message_handler(commands=['leaderboard'])
def leaderboard_command(message):
    """Show leaderboard via command"""
    handle_leaderboard(message.chat.id)

@bot.message_handler(commands=['help'])
def send_help(message):
    """Help command"""
    help_text = (
        "📖 **Commands**\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "• `/start` - Main menu\n"
        "• `/promo` - Get daily promo\n"
        "• `/categories` - Browse categories\n"
        "• `/stats` - Your stats\n"
        "• `/leaderboard` - Top users\n"
        "• `/help` - This message\n\n"
        "🎯 **How it works:**\n"
        "Get daily promo codes\n"
        "Browse deals by category\n"
        "Earn points for visits\n"
        "Build streaks\n"
        "Compete with others\n\n"
        "📌 **Free deals & discounts!**"
    )
    bot.reply_to(message, help_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_other_messages(message):
    """Handle any other messages"""
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📂 Menu", callback_data="start"))
    
    response = (
        "💡 **Use commands or buttons:**\n\n"
        "• `/start` - Main menu\n"
        "• `/promo` - Daily promo\n"
        "• `/categories` - Browse deals\n"
        "• `/stats` - Your stats\n"
        "• `/leaderboard` - Top users"
    )
    bot.reply_to(message, response, parse_mode='Markdown', reply_markup=markup)

# --- Handler Functions ---

def handle_daily_promo(chat_id, user_id):
    """Handle daily promo"""
    if user_id not in user_data:
        bot.send_message(chat_id, "⚠️ Use /start first!", parse_mode='Markdown')
        return
    
    can_visit_now, message = can_visit(user_id)
    if not can_visit_now:
        last_visit = user_data[user_id]["last_visit"]
        last_date = datetime.datetime.fromisoformat(last_visit).date()
        next_date = last_date + datetime.timedelta(days=1)
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📊 My Stats", callback_data="my_stats"))
        
        bot.send_message(
            chat_id,
            f"⏰ {message}\n"
            f"📅 **Next promo available:** {next_date.strftime('%B %d, %Y')}",
            parse_mode='Markdown',
            reply_markup=markup
        )
        return
    
    # Get daily promo
    promo = get_daily_promo()
    points, points_type = calculate_points(user_id)
    
    # Update user data
    user_data[user_id]["points"] += points
    user_data[user_id]["total_visits"] += 1
    user_data[user_id]["last_visit"] = datetime.datetime.now().isoformat()
    user_data[user_id]["streak"] += 1
    user_data[user_id]["name"] = user_data[user_id].get("name", "User")
    
    result_message = format_promo_message(user_id, promo, points, points_type)
    
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("📂 Categories", callback_data="categories"),
        InlineKeyboardButton("📊 My Stats", callback_data="my_stats")
    )
    markup.add(InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard"))
    markup.add(InlineKeyboardButton("🔄 Tomorrow's Promo", callback_data="daily_promo"))
    
    bot.send_message(
        chat_id,
        result_message,
        parse_mode='Markdown',
        reply_markup=markup
    )

def handle_categories(chat_id):
    """Show promo categories"""
    markup = InlineKeyboardMarkup(row_width=2)
    for key, value in CATEGORIES.items():
        markup.add(InlineKeyboardButton(f"{value['emoji']} {value['name']}", callback_data=f"cat_{key}"))
    markup.add(InlineKeyboardButton("🔙 Menu", callback_data="start"))
    
    bot.send_message(
        chat_id,
        "📂 **Choose a Category:**\n"
        "Find deals in your favorite category!",
        parse_mode='Markdown',
        reply_markup=markup
    )

def handle_category_promos(chat_id, category):
    """Show promos for specific category"""
    if category not in CATEGORIES:
        return
    
    cat_data = CATEGORIES[category]
    promos = cat_data["promos"]
    
    text = f"{cat_data['emoji']} **{cat_data['name']} Deals**\n"
    text += "━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for promo in promos:
        text += f"**{promo['title']}**\n"
        text += f"🏷️ Code: `{promo['code']}`\n"
        text += f"💰 {promo['discount']} at {promo['store']}\n\n"
    
    text += "━━━━━━━━━━━━━━━━━━━━"
    text += "\n💡 **Use these codes to save!**"
    
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("📂 More Categories", callback_data="categories"),
        InlineKeyboardButton("🎯 Daily Promo", callback_data="daily_promo")
    )
    markup.add(InlineKeyboardButton("🔙 Menu", callback_data="start"))
    
    bot.send_message(chat_id, text, parse_mode='Markdown', reply_markup=markup)

def handle_stats(chat_id, user_id):
    """Show user stats"""
    if user_id not in user_data:
        bot.send_message(chat_id, "⚠️ Use /start first!", parse_mode='Markdown')
        return
    
    data = user_data[user_id]
    streak = data["streak"]
    total_points = data["points"]
    total_visits = data["total_visits"]
    multiplier = get_streak_multiplier(streak)
    
    sorted_users = sorted(user_data.items(), key=lambda x: x[1]["points"], reverse=True)
    rank = next((i+1 for i, (uid, _) in enumerate(sorted_users) if uid == user_id), "N/A")
    
    stats_text = (
        f"📊 **Your Stats**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 **User:** {data['name']}\n"
        f"⭐ **Points:** {total_points}\n"
        f"📈 **Total Visits:** {total_visits}\n"
        f"🔥 **Streak:** {streak} days\n"
        f"📈 **Multiplier:** {multiplier}x\n"
        f"🏆 **Rank:** #{rank} of {len(user_data)}\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )
    
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("🎯 Daily Promo", callback_data="daily_promo"),
        InlineKeyboardButton("📂 Categories", callback_data="categories")
    )
    markup.add(InlineKeyboardButton("🔙 Menu", callback_data="start"))
    
    bot.send_message(chat_id, stats_text, parse_mode='Markdown', reply_markup=markup)

def handle_leaderboard(chat_id):
    """Show leaderboard"""
    top_users = get_leaderboard()
    
    if not top_users:
        leaderboard_text = "🏆 **Leaderboard**\n━━━━━━━━━━━━━━━━━━━━\n\nNo users yet. Be the first!"
    else:
        leaderboard_text = "🏆 **Leaderboard**\n━━━━━━━━━━━━━━━━━━━━\n\n"
        for i, (user_id, data) in enumerate(top_users, 1):
            medal = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else f"{i}."
            name = data.get("name", "User")
            points = data["points"]
            streak = data.get("streak", 0)
            leaderboard_text += f"{medal} **{name}** - {points} pts (🔥{streak}d)\n"
    
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("🎯 Daily Promo", callback_data="daily_promo"),
        InlineKeyboardButton("📊 My Stats", callback_data="my_stats")
    )
    markup.add(InlineKeyboardButton("🔙 Menu", callback_data="start"))
    
    bot.send_message(chat_id, leaderboard_text, parse_mode='Markdown', reply_markup=markup)

# --- Callback Handlers ---

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    """Handle button clicks"""
    try:
        if call.data == "start":
            send_welcome(call.message)
            bot.answer_callback_query(call.id)
            
        elif call.data == "daily_promo":
            handle_daily_promo(call.message.chat.id, call.from_user.id)
            bot.answer_callback_query(call.id)
            
        elif call.data == "categories":
            handle_categories(call.message.chat.id)
            bot.answer_callback_query(call.id)
            
        elif call.data.startswith("cat_"):
            category = call.data.replace("cat_", "")
            handle_category_promos(call.message.chat.id, category)
            bot.answer_callback_query(call.id)
            
        elif call.data == "my_stats":
            handle_stats(call.message.chat.id, call.from_user.id)
            bot.answer_callback_query(call.id)
            
        elif call.data == "leaderboard":
            handle_leaderboard(call.message.chat.id)
            bot.answer_callback_query(call.id)
            
        elif call.data == "about":
            about_text = (
                "🤖 **About Daily Promo**\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                "Find the best daily deals!\n\n"
                "✅ Daily promo codes\n"
                "✅ Category deals\n"
                "✅ Earn points\n"
                "✅ Build streaks\n"
                "✅ Compete on leaderboard\n\n"
                "📌 **Free deals & discounts**\n"
                "🛍️ **Save money daily!**\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"👥 {len(user_data)} users"
            )
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🔙 Menu", callback_data="start"))
            
            bot.edit_message_text(
                about_text,
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=markup
            )
            bot.answer_callback_query(call.id)
            
    except Exception as e:
        logging.error(f"Callback error: {e}")
        bot.answer_callback_query(call.id, text="❌ Error", show_alert=True)

# --- Main Execution ---

if __name__ == '__main__':
    logging.info("🚀 Daily Promo Bot is starting...")
    logging.info(f"✅ Bot online! Users: {len(user_data)}")
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        logging.error(f"Bot polling failed: {e}")
