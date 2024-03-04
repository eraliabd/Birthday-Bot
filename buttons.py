from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_buttons = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton(text="Lavozimlar"),
            KeyboardButton(text="Xodimlar")
        ]
    ]
)

employee_button = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton(text="Xodimlar ro'yxati"),
            KeyboardButton(text="Ro'yxatdan o'tish"),
        ],
        [
            KeyboardButton(text="Orqaga")
        ]
    ]
)
