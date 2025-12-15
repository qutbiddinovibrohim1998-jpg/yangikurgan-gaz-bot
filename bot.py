import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

class GazForm(StatesGroup):
    zapravka = State()
    gaz = State()
    navbat = State()
    vaqt = State()

def kb_gaz():
    kb = InlineKeyboardBuilder()
    kb.button(text="🟢 Gaz BOR", callback_data="gaz:bor")
    kb.button(text="🔴 Gaz YO‘Q", callback_data="gaz:yoq")
    kb.adjust(2)
    return kb.as_markup()

def kb_navbat():
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Yo‘q", callback_data="navbat:yoq")
    kb.button(text="🟡 Kam", callback_data="navbat:kam")
    kb.button(text="🟠 O‘rtacha", callback_data="navbat:ortacha")
    kb.button(text="🔴 Ko‘p", callback_data="navbat:kopp")
    kb.adjust(2)
    return kb.as_markup()

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "Salom! ⛽\n\n"
        "Guruhga tez va chiroyli xabar chiqarish uchun:\n"
        "👉 /gaz buyrug‘ini bosing."
    )

@dp.message(Command("gaz"))
async def gaz_start(message: Message, state: FSMContext):
    await state.set_state(GazForm.zapravka)
    await message.answer("📍 Qaysi zapravka? (nomi yoki joyi)")

@dp.message(GazForm.zapravka)
async def set_zapravka(message: Message, state: FSMContext):
    await state.update_data(zapravka=message.text.strip())
    await state.set_state(GazForm.gaz)
    await message.answer("⛽ Gaz holati?", reply_markup=kb_gaz())

@dp.callback_query(F.data.startswith("gaz:"), GazForm.gaz)
async def set_gaz(call: CallbackQuery, state: FSMContext):
    gaz_val = call.data.split(":")[1]
    await state.update_data(gaz=gaz_val)
    await state.set_state(GazForm.navbat)
    await call.message.edit_text("🚗 Navbat holati?", reply_markup=kb_navbat())
    await call.answer()

@dp.callback_query(F.data.startswith("navbat:"), GazForm.navbat)
async def set_navbat(call: CallbackQuery, state: FSMContext):
    nav_val = call.data.split(":")[1]
    await state.update_data(navbat=nav_val)
    await state.set_state(GazForm.vaqt)
    await call.message.edit_text("⏰ Vaqt? (masalan: 11:25)")
    await call.answer()

@dp.message(GazForm.vaqt)
async def finish(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()

    zapravka = data.get("zapravka", "—")
    gaz_val = data.get("gaz", "—")
    nav_val = data.get("navbat", "—")
    vaqt = message.text.strip()

    gaz_txt = "BOR" if gaz_val == "bor" else "YO‘Q"
    nav_map = {"yoq": "Yo‘q", "kam": "Kam", "ortacha": "O‘rtacha", "kopp": "Ko‘p"}
    nav_txt = nav_map.get(nav_val, nav_val)

    user = message.from_user
    mention = user.mention_html(user.full_name)

    out = (
        f"📍 <b>Zapravka:</b> {zapravka}\n"
        f"⛽ <b>Gaz:</b> {gaz_txt}\n"
        f"🚗 <b>Navbat:</b> {nav_txt}\n"
        f"⏰ <b>Vaqt:</b> {vaqt}\n\n"
        f"🙏 Rahmat, {mention}"
    )

    await message.answer(out, parse_mode="HTML")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
