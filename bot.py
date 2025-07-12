import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from abbreviations import find_abbreviation

API_TOKEN = "7316017191:AAHlJrgk1n_WsgOpHeHUB2zd97m3-tugfs8"

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
        with open("unknown_abbr.txt", "a", encoding="utf-8") as f:
            f.write(query + "\n")
        return

    item = matches[0]
    abbr = item["abbr"]
    full = item["full"]
    description = item.get("description")
    source = item.get("source")

    keyboard = InlineKeyboardBuilder()
    if description:
        keyboard.button(text="ℹ️ Пояснение", callback_data=f"desc_{abbr}")
    keyboard.button(text="🏠 Домой", callback_data="home")

    await message.answer(
        f"🔹 <b>{abbr}</b>\n<b>Расшифровка:</b> {full}",
        reply_markup=keyboard.as_markup()
    )

@dp.callback_query()
async def handle_callback(callback: CallbackQuery):
    try:
        data = callback.data

        if data == "home":
            await callback.message.answer("Введите новую аббревиатуру:")
            await callback.answer()
            return

        if data.startswith("desc_"):
            abbr = data.split("_", 1)[1]
            matches = find_abbreviation(abbr)
            if not matches:
                await callback.message.answer("Информация не найдена.")
                await callback.answer()
                return

            item = matches[0]
            description = item.get("description", "Нет пояснения.")
            source = item.get("source", "Источник не указан.")

            await callback.message.answer(
                f"<b>Пояснение:</b> {description}\n<b>Источник:</b> {source}",
                parse_mode=ParseMode.HTML
            )
            await callback.answer()
    except Exception:
        try:
            await callback.answer()
        except:
            pass

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

