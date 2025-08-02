import os
import aiofiles

from aiogram import Router, F, Bot
from aiogram.types import Message, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from anyio import Path
from src.core import settings


from src.states.document import WordToPDFState
from src.utils.common import generate_uniq_filename
from src.utils.conversion import convert_docx_to_pdf


router = Router()


@router.message(WordToPDFState.waiting_for_word, F.document.mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
async def process_word_to_pdf(message: Message, state: FSMContext, bot: Bot):
    await message.answer(_("Fayl qayta ishlanmoqda..."))

    document = message.document

    file_info = await bot.get_file(document.file_id)
    file_path = settings.TEMP_DIR / generate_uniq_filename(document.file_name)
    output_path = settings.TEMP_DIR / (Path(file_path).stem + ".pdf")

    await bot.download_file(file_info.file_path, file_path)

    success = convert_docx_to_pdf(file_path, output_path)

    if success:
        async with aiofiles.open(output_path, "rb") as f:
            await message.answer_document(
                document=BufferedInputFile(file=await f.read(), filename=output_path.name),
                caption=_("Fayl muvaffaqiyatli o'zgartirildi!"),
            )
    else:
        await message.answer(_("Faylni o‘zgartirishda xatolik yuz berdi. Iltimos, qayta urinib ko‘ring."))

    for path in [file_path, output_path]:
        if path.exists():
            os.remove(path)


@router.message(WordToPDFState.waiting_for_word)
async def process_unknown_message(message: Message):
    await message.answer(_("Iltimos, faqat PDF fayllarni yuboring."))
