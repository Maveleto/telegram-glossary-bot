import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from abbreviations import find_abbreviation

API_TOKEN = os.getenv("BOT_TOKEN")  # получаем токен из переменной окружения

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Хэндлер на входящее сообщение
@dp.message()
async def handle_message(message: Message):
    query = message.text.strip()
    if not query:
        await message.answer("Введите аббревиатуру для поиска.")
        return

    matches = find_abbreviation(query)

    if not matches:
        await message.answer("Извините, такого сокращения не найдено. Глоссарий дополняется.")
        with open("unknown_abbr.txt", "a", encoding="utf-8") as f:
            f.write(f"{query}\n")
        return

    for item in matches:
        # Создаем текст для расшифровки
        text = f"<b>{item['abbr']}</b>\n<b>Расшифровка:</b> {item['full']}"

        # Создаем кнопки
        keyboard = InlineKeyboardBuilder()
        if item.get("description"):
            keyboard.button(text="Пояснение", callback_data=f"desc|{item['abbr']}")
        keyboard.button(text="⬅️ Домой", callback_data="home")
        await message.answer(text, reply_markup=keyboard.as_markup())

# Обработчик кнопки "Пояснение"
@dp.callback_query(F.data.startswith("desc|"))
async def send_description(callback: CallbackQuery):
    abbr = callback.data.split("|")[1]
    match = find_abbreviation(abbr)
    if match and match[0].get("description"):
        description = match[0]["description"]
        source = match[0].get("source", "")
        text = f"<b>Пояснение:</b> {description}"
        if source:
            text += f"\n<b>Источник:</b> {source}"
        await callback.message.answer(text)
    else:
        await callback.answer("Нечего показать.", show_alert=True)

# Обработчик кнопки "Домой"
@dp.callback_query(F.data == "home")
async def go_home(callback: CallbackQuery):
    await callback.message.answer("Введите аббревиатуру для поиска.")

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

