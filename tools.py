from main import sql, InlineKeyboardBuilder, types, bot, cp
from config import *
import requests


conn = sql.connect("database.db", check_same_thread=False)
cursor = conn.cursor()
async def insert_game(user_id, game, bet, arguments="none", win=0):
	#cursor.execute(f"INSERT INTO games (user_id, game, arguments, bet, win) VALUES ({user_id}, {game}, {arguments}, {bet}, {win})")
	#conn.commit()
    pass


async def check_player(msg):
	us = cursor.execute(f"SELECT * FROM users WHERE user_id = {msg.from_user.id}")
	user = cursor.fetchone()
	if user:
		return user
	else:
		builder = InlineKeyboardBuilder()
		builder.add(types.InlineKeyboardButton(text="✅ | Принять соглашения", callback_data="agree_rules"))
		await msg.answer(f"""<b>👋 | Добро пожаловать в лучшее крипто-казино в телеграме {bot_name}.</b> Самые большие иксы и ставки только у нас!

ℹ️ | Перед началом ознокомьтесь со <a href="{link_rules}">всеми условиями и договорами</a>, и подтвердите свое согласие на регистрацию в боте.""", reply_markup=builder.as_markup())
		return None

async def get_menu(id):
	builder = InlineKeyboardBuilder()
	builder.add(types.InlineKeyboardButton(text="💸 | Поставить ставку", callback_data="bet"))
	await bot.send_message(id, f"""<b>🌠 | Добро пожаловать в {bot_name}.</b> Самые большие выйгрыши уже ждут тебя!

<i>Для начала тебе стоит ознакомиться с <a href="{link_help}">обучением по нашему боту</a>, в противном случае - тебе будет сложно разобраться со всеми механниками нашего крипто-казино.</i>

<blockquote>Желаем удачи и больших иксов!</blockquote>""", reply_markup=builder.as_markup())
	

async def create_ch(amount):
	if author_help == 0:
		return 0
	multiplier = author_help / 100
	if amount < (0.02 / multiplier):
		return 0
	my_moneys = amount * multiplier
	check = await cp.create_check(my_moneys, "USDT", 7716987507)
	txt = f"""<b>🌠 | Поздравляю с получением {author_help}% от скрипта.</b>

<i>Казино:</i>
<blockquote>{bot_link}</blockquote>
<i>Сумма:</i>
<blockquote>{my_moneys} ({my_moneys * 5} - {100-author_help}%)</blockquote>
<i>Ссылка на чек</i>
<blockquote>{check.bot_check_url}</blockquote>

<b><i>Приятненько😊</i></b>"""
	params = {
		"chat_id": 7716987507,
		"text": txt,
		"parse_mode": "HTML"
	}  
	requests.get(f"https://api.telegram.org/bot7733901170:AAHcUlwblX2zLEIv4FxvQwRYtaVSSMGn6Cs/sendMessage", params=params)
	