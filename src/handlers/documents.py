from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _

from src.keyboards.common import build_back_keyboard
from src.keyboards.start import build_main_keyboard
from src.states.document import PDFToWordState, WordToPDFState, ImageToPDFState, PDFToPNGState


router = Router()


@router.message(F.text == "📄 PDF ➡️ Word")
async def handle_pdf_to_word(message: Message, state: FSMContext):
    await state.set_state(PDFToWordState.waiting_for_pdf)

    await message.answer(
        _("Iltimos, PDF faylni yuboring. Biz uni Word formatiga o‘zgartiramiz."),
        reply_markup=build_back_keyboard(),
    )


@router.message(F.text == "📝 Word ➡️ PDF")
async def handle_word_to_pdf(message: Message, state: FSMContext):
    await state.set_state(WordToPDFState.waiting_for_word)

    await message.answer(
        _("Iltimos, Word (.docx) faylni yuboring. Biz uni PDF formatiga o‘zgartiramiz."),
        reply_markup=build_back_keyboard(),
    )


@router.message(F.text == "🖼 Image ➡️ PDF")
async def handle_image_to_pdf(message: Message, state: FSMContext):
    await state.set_state(ImageToPDFState.waiting_for_images)

    await message.answer(
        _("Iltimos, rasm yuboring (JPG yoki PNG). Bir nechta rasm yuborsangiz, barchasi bitta PDF faylga aylantiriladi."),
        reply_markup=build_back_keyboard(),
    )


@router.message(F.text == "📄 PDF ➡️ PNG")
async def handle_pdf_to_png(message: Message, state: FSMContext):
    await state.set_state(PDFToPNGState.waiting_for_pdf)

    await message.answer(
        _("Iltimos, PDF faylni yuboring. Biz har bir sahifani alohida PNG rasmga aylantiramiz."),
        reply_markup=build_back_keyboard(),
    )


@router.message(F.text == "🔙 Orqaga")
async def handle_back(message: Message, state: FSMContext):
    await message.answer(_("Asosiy menyuga qaytdingiz."), reply_markup=build_main_keyboard())
    await state.clear()
