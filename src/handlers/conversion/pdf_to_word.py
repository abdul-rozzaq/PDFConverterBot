import os
import aiofiles

from aiogram import F, Bot, Router
from aiogram.types import Message, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from src.core import settings


from src.states.document import PDFToWordState
from src.utils.common import generate_uniq_filename
from src.utils.conversion import convert_pdf_to_docx


router = Router()


@router.message(PDFToWordState.waiting_for_pdf, F.document.mime_type == "application/pdf")
async def process_pdf_to_word(message: Message, state: FSMContext, bot: Bot):
    await message.answer(_("Fayl qayta ishlanmoqda..."))

    document = message.document

    file_info = await bot.get_file(document.file_id)
    file_path = settings.TEMP_DIR / generate_uniq_filename(document.file_name)
    output_path = settings.TEMP_DIR / generate_uniq_filename(document.file_name, "docx")

    await bot.download_file(file_info.file_path, file_path)

    success = await convert_pdf_to_docx(file_path, output_path)

    if success:
        async with aiofiles.open(output_path, "rb") as f:
            await message.answer_document(
                document=BufferedInputFile(file=await f.read(), filename=output_path.name),
                caption=_("Fayl muvaffaqiyatli o'zgartirildi!"),
            )
    else:
        await message.answer(_("Faylni o'zgartirishda xatolik yuz berdi. Iltimos, qayta urinib ko'ring."))

    for path in [file_path, output_path]:
        if path.exists():
            os.remove(path)


@router.message(PDFToWordState.waiting_for_pdf)
async def process_unknown_message(message: Message):
    await message.answer(_("Iltimos, faqat PDF fayllarni yuboring."))
