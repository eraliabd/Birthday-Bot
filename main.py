import asyncio
import pandas as pd
from datetime import datetime, time


from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardRemove, InputFile
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from buttons import main_buttons, employee_button
from states import RegisterState
from write_to_excel import write_to_excel, get_employee_list_with_details, check_employee

# Bot token
BOT_TOKEN = ""
ADMINS = []

PROXY_URL = "http://proxy.server:3128"

# PROXY_URL = "http://proxy.server:3128"
# bot = Bot(proxy=PROXY_URL)

bot = Bot(token=BOT_TOKEN, proxy=PROXY_URL)

dp = Dispatcher(bot=bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

# file
file_path = "employees.xlsx"


@dp.message_handler(commands='start')
async def send_welcome_handler(message: types.Message):
    await message.reply(
        f"Assalomu alaykum {message.from_user.first_name}!\nTug'ilgan kun botiga xush kelibsiz!\n\n"
        f"Sizga tabrik yuborishimiz uchun `Xodimlar` bo'limiga o'tib ro'yxatdan o'tishingizni so'rab qolamiz!\n",
        reply_markup=main_buttons
    )


@dp.message_handler(Text("Xodimlar ro'yxati"), user_id=ADMINS[0])
async def employees_list_handler(message: types.Message):
    try:
        df = pd.read_excel(file_path)

        with open(file_path, 'rb') as file:
            await bot.send_document(
                chat_id=ADMINS[0],
                document=InputFile(path_or_bytesio=file),
                caption="Botdan ro'yxatdan o'tgan xodimlar ro'yxati.",
            )

    except FileNotFoundError:
        print("File not found!")
        return

    except Exception as e:
        print(f"An error occurred: {e}")
        return


@dp.message_handler(Text(startswith="Orqaga"))
async def back_handler(message: types.Message):
    await message.answer(text="Tanlang:", reply_markup=main_buttons)


@dp.message_handler(Text("Lavozimlar"))
async def position_section_handler(message: types.Message):
    await message.answer(text="Lavozim nomlari:\n\n"
                              "Direktor\n"
                              "Bo'lim boshlig'i\n"
                              "Jamoa yetakchisi\n"
                              "Loyiha menejeri\n"
                              "Dasturchi\n"
                              "Dizayner\n"
                              "Marketolog\n"
                              "Sotuvchi",
                         reply_markup=main_buttons
                         )


@dp.message_handler(Text("Xodimlar"))
async def employees_section_handler(message: types.Message):
    await message.answer(text="Tanlang:", reply_markup=employee_button)


@dp.message_handler(Text(startswith="Ro'yxatdan o'tish"))
async def main_handler(message: types.Message):
    employee_id = message.from_user.id
    if check_employee(employee_id, file_path=file_path):
        await message.answer(text="Siz allaqachon ro'yxatdan o'tgansiz!", reply_markup=main_buttons)
    else:
        await message.answer(text="Ism kiriting: ", reply_markup=ReplyKeyboardRemove())
        await RegisterState.first_name.set()


@dp.message_handler(state=RegisterState.first_name)
async def first_handler(message: types.Message, state: FSMContext):
    first_name = message.text
    await state.update_data({"first_name": first_name})

    await message.answer(text="Familiya kiriting: ")
    await RegisterState.next()


@dp.message_handler(state=RegisterState.last_name)
async def last_handler(message: types.Message, state: FSMContext):
    last_name = message.text
    await state.update_data({"last_name": last_name})

    await message.answer(text="Tug'ilgan kun kiriting:\nMasalan: (yil-oy-kun: 2005-03-04)")
    await RegisterState.next()


@dp.message_handler(state=RegisterState.date_of_birth)
async def date_handler(message: types.Message, state: FSMContext):
    date_of_birth = message.text
    await state.update_data({"date_of_birth": date_of_birth})

    await message.answer(text="Shaxsiy rasm yuboring: ")
    await RegisterState.next()


@dp.message_handler(content_types='photo', state=RegisterState.image)
async def photo_handler(message: types.Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await state.update_data({"image_url": photo_id})

    user_data = await state.get_data()
    employee_id = message.from_user.id
    first_name = user_data.get("first_name")
    last_name = user_data.get("last_name")
    string_date = user_data.get("date_of_birth")
    date_of_birth = datetime.strptime(string_date, '%Y-%m-%d').date()

    write_to_excel(employee_id=employee_id, first_name=first_name, last_name=last_name, date_of_birth=date_of_birth,
                   image_url=photo_id, file_path=file_path)

    await message.answer_photo(
        photo=photo_id,
        caption=f"<b>Ro'yxatdan muaffaqiyatli o'tdingiz!</b>\n\n"
                f"<b>👤 Ismi:</b> {first_name} {last_name}\n"
                f"<b>🎂 Tug'ilgan kuni (yil-oy-kun):</b> {date_of_birth}\n\n"
                f"👉 @happy_birthday_uzbot 👈",
        parse_mode="HTML",
        reply_markup=main_buttons
    )
    await state.finish()


async def reminder_birthday():
    """
    Bu funksiyani vazifasi, botga start bosgan
    va ro'yxatdan o'tgan xodimlar uchun
    tug'ilgan kun tabriklarini yuborib turish.
    """

    today = datetime.now().strftime("%Y-%m-%d")

    employees_list = get_employee_list_with_details(file_path)

    for employee in employees_list:
        if employee["date_of_birth"].strftime("%Y-%m-%d")[5:] == today[5:]:
            try:
                # Clock setting
                reminder_time = datetime.combine(datetime.today(), time(hour=8))
                print("R-Time: ", reminder_time - datetime.now())

                await asyncio.sleep((reminder_time - datetime.now()).total_seconds())
                # for admin
                await bot.send_photo(
                    chat_id=ADMINS[0],
                    photo=employee["image_url"],
                    caption=f"<b>Bugun shu hodimni tug'ilgan kuni</b> 🥳\n\n"
                            f"<b>👤 Ismi:</b> {employee['first_name']} {employee['last_name']}\n"
                            f"<b>🎂 Tug'ilgan kuni (yil-oy-kun):</b> {employee['date_of_birth']}\n\n"
                            f"👉 @happy_birthday_uzbot 👈",
                    parse_mode="HTML"
                )
                # for employee
                await bot.send_photo(
                    chat_id=employee["employee_id"],
                    photo=employee["image_url"],
                    caption=f"<b>Bugungi tavallud ayyomingiz bilan</b> 🥳\n\n"
                            f"<b>👤 Ismi:</b> {employee['first_name']} {employee['last_name']}\n"
                            f"<b>🎂 Tug'ilgan kuni (yil-oy-kun):</b> {employee['date_of_birth']}\n\n"
                            f"👉 @happy_birthday_uzbot 👈",
                    parse_mode="HTML"
                )

            except Exception as e:
                print(f"An error occurred: {e}")

        else:
            pass


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(reminder_birthday())
    executor.start_polling(dispatcher=dp, skip_updates=True)
