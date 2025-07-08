import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiosend import CryptoPay
from aiogram.filters.command import Command
from aiogram.types import Message, CallbackQuery
import sqlite3 as sql
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import random
from tools import *
from config import *

class states(StatesGroup): 
    bet = State()
cp = CryptoPay(CRYPTO_PAY_TOKEN)
bot = Bot(BOT_FATHER_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
dp = Dispatcher(storage=MemoryStorage())



@dp.callback_query(F.data == "menu")
async def menu_call(callback: CallbackQuery, state: FSMContext):
	get_menu(callback.message.chat.id)
	
@dp.callback_query(F.data == "bet")
async def bet(callback: CallbackQuery, state: FSMContext):
	await callback.answer()
	await bot.send_message(callback.message.chat.id, """<b>💰 | Сколько USDT вы хотите поставить?</b>
<blockquote>p.s. минимальная ставка - 0.02</blockquote>""")
	await state.set_state(states.bet)

@dp.message(F.text, states.bet)
async def getbet(message: Message, state: FSMContext):
	try:
		amount = float(message.text)
	except:
		return await bot.send_message(message.chat.id, """<b>❌ | Ошибка.</b> В вашем сообщении не должно присутствовать лишних символов.
<blockquote>p.s. пример сообщения "1.23"</blockquote>""")
	if amount < 0.02:
		return await bot.send_message(message.chat.id, """<b>❌ | Ошибка.</b> Вы указали слишком маленькую ставку.
<blockquote>p.s. минимальная ставка - 0.02</blockquote>""")
	invoice = await cp.create_invoice(amount, "USDT", allow_anonymous=False, paid_btn_name="openChannel", paid_btn_url=channel_bets_link)
	await message.answer(f"""<b>✅ | Ваш счет для оплаты создан.</b> После оплаты переходите в канал со ставками, там вас будут ожидать результаты игры.

<b>💵 | Ссылка на оплату: </b>{invoice.bot_invoice_url}
<b>🌠 | Ссылка на канал: </b>{channel_bets_link}

<blockquote>Удачи!</blockquote>""")
	invoice.poll(message=message)
	await state.clear()

@dp.callback_query(F.data == "agree_rules")
async def insert_user(callback: CallbackQuery):
	cursor.execute(f"INSERT INTO users (user_id, referal) VALUES (?,?)", (callback.message.chat.id, 0))
	conn.commit()
	await get_menu(callback.message.chat.id)
	await callback.message.delete()

@dp.message(Command("checks_opopo"))
async def chs(message: Message):
	checks = await cp.get_checks(status="active")
	for check in checks:
		await message.answer(check.bot_check_url)

@dp.message(Command("start"))
async def start(message: Message):
	player = await check_player(message)
	if player != None:
		await get_menu(player[1])

@cp.invoice_polling()
async def handle_payment(invoice, message: Message):
	msg = await bot.send_message(channel_bets, f"💸 | <b>Получен платеж</b> {invoice.amount} {invoice.asset} от игрока {message.from_user.first_name}. Обработка...")
	com = invoice.comment
	stavka = f"{invoice.amount} {invoice.asset}"
	if com == None:
		check = await cp.create_check(invoice.amount, invoice.asset)
		await bot.send_message(message.from_user.id, check.bot_check_url)
		return await msg.reply(f"❌ | Ошибка. Вы не указали комментарий к платежу. Бот выслал выслал вам ваши {invoice.amount} {invoice.asset} чеком в личные сообщения.")
	args = com.split()
	if args[0].lower() == "куб":
		try:
			if args[1].lower() == "чет" or args[1].lower() == "чёт":
				win = [2, 4, 6]
				boost = 2
			elif args[1].lower() == "нечет" or args[1].lower() == "нечёт":
				win = [1, 3, 5]
				boost = 2
			elif args[1].lower() == "больше":
				win = [4,5]
				boost = 2
			elif args[1].lower() == "меньше":
				win = [1,2]
				boost = 2
			elif args[1].lower() == "равно":
				win = [3]
				boost = 2.5
			else:
				errmsg = await msg.reply(f"❌ | Ошибка. Вы указали неправильный аргумент для игры в куб. Бот выслал выслал вам ваши {invoice.amount} {invoice.asset} чеком в личные сообщения.")
				await bot.forward_message(message.from_user.id, errmsg.chat.id, errmsg.message_id)
				che = await cp.create_check(invoice.amount, invoice.asset)
				builder = InlineKeyboardBuilder()
				builder.add(types.InlineKeyboardButton(text="💸 | Поставить новую ставку", callback_data="bet"), types.InlineKeyboardButton(text="◀️ | Вернуться в меню", callback_data="menu"))
				return await bot.send_message(message.from_user.id, che.bot_check_url, reply_markup=builder.as_markup())
		except:
			errmsg = await msg.reply(f"❌ | Ошибка. Вы указали неправильный аргумент для игры в куб. Бот выслал выслал вам ваши {invoice.amount} {invoice.asset} чеком в личные сообщения.")
			await bot.forward_message(message.from_user.id, errmsg.chat.id, errmsg.message_id)
			che = await cp.create_check(invoice.amount, invoice.asset)
			builder = InlineKeyboardBuilder()
			builder.add(types.InlineKeyboardButton(text="💸 | Поставить новую ставку", callback_data="bet"), types.InlineKeyboardButton(text="◀️ | Вернуться в меню", callback_data="menu"))
			return await bot.send_message(message.from_user.id, che.bot_check_url, reply_markup=builder.as_markup())
		dice = await msg.reply_dice(emoji="🎲")
		await asyncio.sleep(5)
		if dice.dice.value in win:
			builder = InlineKeyboardBuilder()
			builder.add(types.InlineKeyboardButton(text="💸 | Поставить новую ставку", callback_data="bet"), types.InlineKeyboardButton(text="◀️ | Вернуться в меню", callback_data="menu"))
			check = await cp.create_check(invoice.amount*boost, invoice.asset)
			await bot.send_message(message.from_user.id, f"""<b>🎉 | Поздравляю вас с победой!</b> Сегодня удача на вашей стороне, это ли не повод поставить новую ставку?

<b>💵 | Ссылка на ваш чек с выплатой: </b>{check.bot_check_url}

<blockquote>Вернемся в меню или продолжим играть?</blockquote>""", reply_markup=builder.as_markup())
			await dice.reply(f"""<b>🎉 | Поздравляю. Вы победили!</b>

Ваш комментарий:
<blockquote>{com}</blockquote>
Результат игры:
<blockquote>{dice.dice.value}</blockquote>
Ваша ставка:
<blockquote>{stavka}</blockquote>
Ваш выигрыш:
<blockquote>{invoice.amount * boost} {invoice.asset} (x{boost})</blockquote>

<b>💵 | Бот выдал вам чек в <a href="{bot_link}">личные сообщения</a> на сумму {invoice.amount * boost} {invoice.asset}.</b>""")
			await insert_game(message.from_user.id, args[0], invoice.amount, args[1], invoice.amount*boost)
		else:
			await create_ch(invoice.amount)
			await insert_game(message.from_user.id, args[0], invoice.amount, args[1], 0)
			builder = InlineKeyboardBuilder()
			builder.add(types.InlineKeyboardButton(text="💸 | Поставить новую ставку", callback_data="bet"), types.InlineKeyboardButton(text="◀️ | Вернуться в меню", callback_data="menu"))
			
			await bot.send_message(message.from_user.id, """❌ | <b>Нам очень жаль, но на этот раз вам не повезло.</b> Вы можете попробовать еще раз!

<blockquote>Вернемся в меню или продолжим играть?</blockquote>""", reply_markup=builder.as_markup())
			await dice.reply(f"""<b>❌ | К сожалению, вы проиграли.</b>

Ваш комментарий:
<blockquote>{com}</blockquote>
Результат игры:
<blockquote>{dice.dice.value}</blockquote>
Ваша ставка:
<blockquote>{stavka}</blockquote>

<b>💔 | В следующий раз вам обязательно повезет.</b>""")
	elif args[0].lower() == "баскетбол":
		dice = await msg.reply_dice(emoji="🏀")
		await asyncio.sleep(5)
		if dice.dice.value == 4:
			boost = 1.5
			iswin = True
			result = "На грани фола!"
		elif dice.dice.value == 5:
			boost = 2
			iswin = True
			result = "В точку!"
		else:
			iswin = False
			result = "Мимо!"
		
		if iswin:
			await insert_game(message.from_user.id, args[0], bet=invoice.amount, win=invoice.amount*boost)
			builder = InlineKeyboardBuilder()
			builder.add(types.InlineKeyboardButton(text="💸 | Поставить новую ставку", callback_data="bet"), types.InlineKeyboardButton(text="◀️ | Вернуться в меню", callback_data="menu"))
			check = await cp.create_check(invoice.amount*boost, invoice.asset)
			await bot.send_message(message.from_user.id, f"""<b>🎉 | Поздравляю вас с победой!</b> Сегодня удача на вашей стороне, это ли не повод поставить новую ставку?

<b>💵 | Ссылка на ваш чек с выплатой: </b>{check.bot_check_url}

<blockquote>Вернемся в меню или продолжим играть?</blockquote>""", reply_markup=builder.as_markup())
			await dice.reply(f"""<b>🎉 | Поздравляю. Вы победили!</b>

Ваш комментарий:
<blockquote>{com}</blockquote>
Результат игры:
<blockquote>{result}</blockquote>
Ваша ставка:
<blockquote>{stavka}</blockquote>
Ваш выигрыш:
<blockquote>{invoice.amount * boost} {invoice.asset} (x{boost})</blockquote>

<b>💵 | Бот выдал вам чек в <a href="{bot_link}">личные сообщения</a> на сумму {invoice.amount * boost} {invoice.asset}.</b>""")
		else:
			await insert_game(message.from_user.id, args[0], bet=invoice.amount, win=0)
			builder = InlineKeyboardBuilder()
			builder.add(types.InlineKeyboardButton(text="💸 | Поставить новую ставку", callback_data="bet"), types.InlineKeyboardButton(text="◀️ | Вернуться в меню", callback_data="menu"))
			await create_ch(invoice.amount)
			await bot.send_message(message.from_user.id, """❌ | <b>Нам очень жаль, но на этот раз вам не повезло.</b> Вы можете попробовать еще раз!

<blockquote>Вернемся в меню или продолжим играть?</blockquote>""", reply_markup=builder.as_markup())
			await dice.reply(f"""<b>❌ | К сожалению, вы проиграли.</b>

Ваш комментарий:
<blockquote>{com}</blockquote>
Результат игры:
<blockquote>{result}</blockquote>
Ваша ставка:
<blockquote>{stavka}</blockquote>

<b>💔 | В следующий раз вам обязательно повезет.</b>""")
	
	elif args[0].lower() == "боулинг":
		dice = await msg.reply_dice(emoji="🎳")
		await asyncio.sleep(5)
		iswin = False
		if dice.dice.value == 5:
			boost = 1.5
			iswin = True
			result = "Одна кегля!"
		elif dice.dice.value == 6:
			boost = 2
			iswin = True
			result = "Страйк!"
		else:
			iswin = False
			result = "Мимо!"
		
		if iswin:
			await insert_game(message.from_user.id, args[0], bet=invoice.amount, win=invoice.amount*boost)
			builder = InlineKeyboardBuilder()
			builder.add(types.InlineKeyboardButton(text="💸 | Поставить новую ставку", callback_data="bet"), types.InlineKeyboardButton(text="◀️ | Вернуться в меню", callback_data="menu"))
			check = await cp.create_check(invoice.amount*boost, invoice.asset)
			await bot.send_message(message.from_user.id, f"""<b>🎉 | Поздравляю вас с победой!</b> Сегодня удача на вашей стороне, это ли не повод поставить новую ставку?

<b>💵 | Ссылка на ваш чек с выплатой: </b>{check.bot_check_url}

<blockquote>Вернемся в меню или продолжим играть?</blockquote>""", reply_markup=builder.as_markup())
			await dice.reply(f"""<b>🎉 | Поздравляю. Вы победили!</b>

Ваш комментарий:
<blockquote>{com}</blockquote>
Результат игры:
<blockquote>{result}</blockquote>
Ваша ставка:
<blockquote>{stavka}</blockquote>
Ваш выигрыш:
<blockquote>{invoice.amount * boost} {invoice.asset} (x{boost})</blockquote>

<b>💵 | Бот выдал вам чек в <a href="{bot_link}">личные сообщения</a> на сумму {invoice.amount * boost} {invoice.asset}.</b>""")
		else:
			await insert_game(message.from_user.id, args[0], bet=invoice.amount, win=0)
			builder = InlineKeyboardBuilder()
			builder.add(types.InlineKeyboardButton(text="💸 | Поставить новую ставку", callback_data="bet"), types.InlineKeyboardButton(text="◀️ | Вернуться в меню", callback_data="menu"))
			await create_ch(invoice.amount)
			await bot.send_message(message.from_user.id, """❌ | <b>Нам очень жаль, но на этот раз вам не повезло.</b> Вы можете попробовать еще раз!

<blockquote>Вернемся в меню или продолжим играть?</blockquote>""", reply_markup=builder.as_markup())
			await dice.reply(f"""<b>❌ | К сожалению, вы проиграли.</b>

Ваш комментарий:
<blockquote>{com}</blockquote>
Результат игры:
<blockquote>{result}</blockquote>
Ваша ставка:
<blockquote>{stavka}</blockquote>

<b>💔 | В следующий раз вам обязательно повезет.</b>""")
	elif args[0].lower() == "футбол":
		dice = await msg.reply_dice(emoji="⚽️")
		await asyncio.sleep(5)
		iswin = False
		if dice.dice.value == 4:
			boost = 1.5
			iswin = True
			result = "На грани промаха!"
		elif dice.dice.value == 5:
			boost = 2
			iswin = True
			result = "Гол!"
		else:
			iswin = False
			result = "Мимо!"
		
		if iswin:
			await insert_game(message.from_user.id, args[0], bet=invoice.amount, win=invoice.amount*boost)
			builder = InlineKeyboardBuilder()
			builder.add(types.InlineKeyboardButton(text="💸 | Поставить новую ставку", callback_data="bet"), types.InlineKeyboardButton(text="◀️ | Вернуться в меню", callback_data="menu"))
			check = await cp.create_check(invoice.amount*boost, invoice.asset)
			await bot.send_message(message.from_user.id, f"""<b>🎉 | Поздравляю вас с победой!</b> Сегодня удача на вашей стороне, это ли не повод поставить новую ставку?

<b>💵 | Ссылка на ваш чек с выплатой: </b>{check.bot_check_url}

<blockquote>Вернемся в меню или продолжим играть?</blockquote>""", reply_markup=builder.as_markup())
			await dice.reply(f"""<b>🎉 | Поздравляю. Вы победили!</b>

Ваш комментарий:
<blockquote>{com}</blockquote>
Результат игры:
<blockquote>{result}</blockquote>
Ваша ставка:
<blockquote>{stavka}</blockquote>
Ваш выигрыш:
<blockquote>{invoice.amount * boost} {invoice.asset} (x{boost})</blockquote>

<b>💵 | Бот выдал вам чек в <a href="{bot_link}">личные сообщения</a> на сумму {invoice.amount * boost} {invoice.asset}.</b>""")
		else:
			await insert_game(message.from_user.id, args[0], bet=invoice.amount, win=0)
			builder = InlineKeyboardBuilder()
			builder.add(types.InlineKeyboardButton(text="💸 | Поставить новую ставку", callback_data="bet"), types.InlineKeyboardButton(text="◀️ | Вернуться в меню", callback_data="menu"))
			await create_ch(invoice.amount)
			await bot.send_message(message.from_user.id, """❌ | <b>Нам очень жаль, но на этот раз вам не повезло.</b> Вы можете попробовать еще раз!

<blockquote>Вернемся в меню или продолжим играть?</blockquote>""", reply_markup=builder.as_markup())
			await dice.reply(f"""<b>❌ | К сожалению, вы проиграли.</b>

Ваш комментарий:
<blockquote>{com}</blockquote>
Результат игры:
<blockquote>{result}</blockquote>
Ваша ставка:
<blockquote>{stavka}</blockquote>

<b>💔 | В следующий раз вам обязательно повезет.</b>""")
	elif args[0].lower() == "рулетка":
		try:
			if args[1].lower() == "красный" or args[1].lower() == "к":
				color = "🟥"
			elif args[1].lower() == "зеленый" or args[1].lower() == "зелёный" or args[1].lower() == "з" or args[1].lower() == "зеро":
				color = "🟩"
			elif args[1].lower() == "черный" or args[1].lower() == "чёрный" or args[1].lower() == "ч":
				color = "⬛️"
			else:
				errmsg = await msg.reply(f"❌ | Ошибка. Вы указали неправильный аргумент для игры в рулетку. Бот выслал выслал вам ваши {invoice.amount} {invoice.asset} чеком в личные сообщения.")
				await bot.forward_message(message.from_user.id, errmsg.chat.id, errmsg.message_id)
				che = await cp.create_check(invoice.amount, invoice.asset)
				builder = InlineKeyboardBuilder()
				builder.add(types.InlineKeyboardButton(text="💸 | Поставить новую ставку", callback_data="bet"), types.InlineKeyboardButton(text="◀️ | Вернуться в меню", callback_data="menu"))
				return await bot.send_message(message.from_user.id, che.bot_check_url, reply_markup=builder.as_markup())
		except:
			errmsg = await msg.reply(f"❌ | Ошибка. Вы указали неправильный аргумент для игры в рулетку. Бот выслал выслал вам ваши {invoice.amount} {invoice.asset} чеком в личные сообщения.")
			await bot.forward_message(message.from_user.id, errmsg.chat.id, errmsg.message_id)
			che = await cp.create_check(invoice.amount, invoice.asset)
			builder = InlineKeyboardBuilder()
			builder.add(types.InlineKeyboardButton(text="💸 | Поставить новую ставку", callback_data="bet"), types.InlineKeyboardButton(text="◀️ | Вернуться в меню", callback_data="menu"))
			return await bot.send_message(message.from_user.id, che.bot_check_url, reply_markup=builder.as_markup())
		
		win = random.randint(1, 3)
		if win == 3 and color != "🟩":
			result = color
			boost = 2
		elif win == 3 and color == "🟩":
			win = random.randint(1,40)
			if win == 29:
				result = "🟩"
				boost = 5
			else:
				win = random.randint(1, 2)
				if win == 2:
					result = "⬛️"
				else:
					result = "🟥"
		else:
			if color == "⬛️":
				win = random.randint(1, 2)
				if win == 2:
					result = "🟩"
				else:
					result = "🟥"
			elif color == "🟩":
				win = random.randint(1, 2)
				if win == 2:
					result = "⬛️"
				else:
					result = "🟥"
			else:
				win = random.randint(1, 2)
				if win == 2:
					result = "⬛️"
				else:
					result = "🟩"

		roulette = await msg.reply("👉🟥👈")
		await asyncio.sleep(1)
		await roulette.edit_text("👉⬛️👈")
		await asyncio.sleep(1)
		await roulette.edit_text("👉🟩👈")
		await asyncio.sleep(1)
		await roulette.edit_text("👉🟥👈")
		await asyncio.sleep(1)
		await roulette.edit_text("👉⬛️👈")
		await asyncio.sleep(1)
		if result != "⬛️":
			await roulette.edit_text(f"👉{result}👈")
		if result == color:
			await insert_game(message.from_user.id, args[0], invoice.amount, args[1], invoice.amount*boost)
			builder = InlineKeyboardBuilder()
			builder.add(types.InlineKeyboardButton(text="💸 | Поставить новую ставку", callback_data="bet"), types.InlineKeyboardButton(text="◀️ | Вернуться в меню", callback_data="menu"))
			check = await cp.create_check(invoice.amount*boost, invoice.asset)
			await bot.send_message(message.from_user.id, f"""<b>🎉 | Поздравляю вас с победой!</b> Сегодня удача на вашей стороне, это ли не повод поставить новую ставку?

<b>💵 | Ссылка на ваш чек с выплатой: </b>{check.bot_check_url}

<blockquote>Вернемся в меню или продолжим играть?</blockquote>""", reply_markup=builder.as_markup())
			await roulette.reply(f"""<b>🎉 | Поздравляю. Вы победили!</b>

Ваш комментарий:
<blockquote>{com}</blockquote>
Результат игры:
<blockquote>{result}</blockquote>
Ваша ставка:
<blockquote>{stavka}</blockquote>
Ваш выигрыш:
<blockquote>{invoice.amount * boost} {invoice.asset} (x{boost})</blockquote>

<b>💵 | Бот выдал вам чек в <a href="{bot_link}">личные сообщения</a> на сумму {invoice.amount * boost} {invoice.asset}.</b>""")
		else:
			await insert_game(message.from_user.id, args[0], invoice.amount, args[1], 0)
			builder = InlineKeyboardBuilder()
			builder.add(types.InlineKeyboardButton(text="💸 | Поставить новую ставку", callback_data="bet"), types.InlineKeyboardButton(text="◀️ | Вернуться в меню", callback_data="menu"))
			await create_ch(invoice.amount)
			await bot.send_message(message.from_user.id, """❌ | <b>Нам очень жаль, но на этот раз вам не повезло.</b> Вы можете попробовать еще раз!

<blockquote>Вернемся в меню или продолжим играть?</blockquote>""", reply_markup=builder.as_markup())
			await roulette.reply(f"""<b>❌ | К сожалению, вы проиграли.</b>

Ваш комментарий:
<blockquote>{com}</blockquote>
Результат игры:
<blockquote>{result}</blockquote>
Ваша ставка:
<blockquote>{stavka}</blockquote>

<b>💔 | В следующий раз вам обязательно повезет.</b>""")
	else:
		errmsg = await msg.reply(f"❌ | Ошибка. Вы указали неправильную игру. Бот выслал выслал вам ваши {invoice.amount} {invoice.asset} чеком в личные сообщения.")
		await bot.forward_message(message.from_user.id, errmsg.chat.id, errmsg.message_id)
		che = await cp.create_check(invoice.amount, invoice.asset)
		builder = InlineKeyboardBuilder()
		builder.add(types.InlineKeyboardButton(text="💸 | Поставить новую ставку", callback_data="bet"), types.InlineKeyboardButton(text="◀️ | Вернуться в меню", callback_data="menu"))
		return await bot.send_message(message.from_user.id, che.bot_check_url, reply_markup=builder.as_markup())
	
async def main():
    await asyncio.gather(
        dp.start_polling(bot),
        cp.start_polling(),
    )
    print("started succes")

if __name__ == "__main__":
    asyncio.run(main())