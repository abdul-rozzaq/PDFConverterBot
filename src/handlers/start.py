from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.utils.i18n import gettext as _

from src.keyboards.start import build_main_keyboard


router = Router()


@router.message(CommandStart())
async def start(message: Message):
    await message.answer(_("Faylni yuboring"), reply_markup=build_main_keyboard())
