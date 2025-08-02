from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def build_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📄 PDF ➡️ Word"), KeyboardButton(text="📝 Word ➡️ PDF")],
            [KeyboardButton(text="🖼 Image ➡️ PDF"), KeyboardButton(text="📄 PDF ➡️ PNG")],
        ],
        resize_keyboard=True,
    )
