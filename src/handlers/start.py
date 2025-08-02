from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.utils.i18n import gettext as _

from aiogram.fsm.context import FSMContext

from src.keyboards.start import build_main_keyboard


router = Router()


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        _(
            "Assalomu alaykum!\n\n"
            "PDFConverterBot - bu bot sizga PDF fayllarni yuborish va ularni turli formatlarga o‘zgartirish imkonini beradi.\n"
            "PDF faylni yuboring yoki pastdagi menyudan kerakli funksiyani tanlang."
        ),
        reply_markup=build_main_keyboard()
    )
