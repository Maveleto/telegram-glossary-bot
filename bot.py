import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from abbreviations import find_abbreviation

API_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

@dp.message()
async def handle_message(message: Message):
    query = message.text.strip()
    if not query:
        await message.answer("Введите аббревиатуру для поиска.")
        return

    matches = find_abbreviation(query)

    if not matches:
        await message.answer("Извините, такого сокращения не найдено. Глоссарий дополняется.")
        try:
            with open("unknown_abbr.txt", "a", encoding="utf-8") as f:
                f.write(f"{query}\n")
        except Exception as e:
            print(f"Ошибка при сохранении неизвестной аббревиатуры: {e}")
        return

    item = matches[0]
    abbr = item["abbr"]
    full = item["full"]
    description = item.get("description")

    keyboard = InlineKeyboardBuilder()
    if description:
        keyboard.button(text="ℹ️ Пояснение", callback_data=f"desc|{abbr}")
    keyboard.button(text="🏠 Домой", callback_data="home")

    await message.answer(
        f"🔹 <b>{abbr}</b>\n<b>Расшифровка:</b> {full}",
        reply_markup=keyboard.as_markup()
    )

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

@dp.callback_query(F.data == "home")
async def go_home(callback: CallbackQuery):
    await callback.message.answer("Введите аббревиатуру для поиска.")
    await callback.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
