import uuid

import aiofiles
import img2pdf

from aiogram import F, Router
from aiogram.types import Message, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _

from src.states.document import ImageToPDFState
from src.core import settings


router = Router()


# @router.message(ImageToPDFState.waiting_for_images)
# async def process_image_to_pdf(message: Message, state: FSMContext):
#     data = await state.get_data()
#     session_id = data.get("session_id") or str(uuid.uuid4())
#     user_dir = settings.TEMP_DIR / f"{message.from_user.id}_{session_id}"
#     user_dir.mkdir(parents=True, exist_ok=True)

#     file_id = None
#     extension = ".jpg"

#     if message.photo:
#         file_id = message.photo[-1].file_id
#     elif message.document and message.document.mime_type.startswith("image/"):
#         file_id = message.document.file_id
#         extension = f".{message.document.mime_type.split('/')[-1]}"
#     else:
#         return await message.reply("Faqat rasm yuboring. Boshqa fayllar qabul qilinmaydi.")

#     file = await message.bot.get_file(file_id)

#     file_path = user_dir / f"{uuid.uuid4()}{extension}"

#     await message.bot.download_file(file.file_path, destination=file_path)

#     await state.update_data(session_id=session_id)

#     await message.answer("Rasm qabul qilindi. Tugatish uchun /done ni bosing.")


# @router.message(ImageToPDFState.waiting_for_images, Command("/done"))
# async def convert_to_pdf(message: Message, satate: FSMContext):
#     pass


@router.message(ImageToPDFState.waiting_for_images, F.photo | (F.document & F.document.mime_type.startswith("image/")))
async def collect_images(message: Message, state: FSMContext):
    data = await state.get_data()

    session_id = data.get("session_id")

    if not session_id:
        session_id = str(uuid.uuid4())
        await state.update_data(session_id=session_id)

    user_dir = settings.TEMP_DIR / f"{message.from_user.id}_{session_id}"
    user_dir.mkdir(parents=True, exist_ok=True)

    # 3. Faylni yuklab olish
    file_id = None
    extension = ".jpg"

    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.document:
        file_id = message.document.file_id
        extension = f".{message.document.mime_type.split('/')[-1]}"

    if file_id:
        telegram_file = await message.bot.get_file(file_id)
        destination_path = user_dir / f"{uuid.uuid4()}{extension}"

        await message.bot.download_file(telegram_file.file_path, destination=destination_path)

        image_count = len([p for p in user_dir.iterdir() if p.suffix.lower() in [".jpg", ".jpeg", ".png"]])

        old_msg_id = data.get("last_msg_id")

        if old_msg_id:
            try:
                await message.bot.edit_message_text(chat_id=message.chat.id, message_id=old_msg_id, text=f"✅ {image_count} ta rasm qabul qilindi.\nYana rasm yuboring yoki /done ni bosing.")

                await message.bot.pin_chat_message(
                    chat_id=message.chat.id,
                    message_id=old_msg_id,
                )

            except Exception as e:
                print("❌ Xabarni tahrirlashda xatolik:", e)
        else:
            new_msg = await message.answer("✅ 1 ta rasm qabul qilindi.\nYana rasm yuboring yoki /done ni bosing.")
            await new_msg.pin()
            await state.update_data(last_msg_id=new_msg.message_id)

    else:
        await message.reply("Faqat rasm yuboring. Boshqa fayllar qabul qilinmaydi.")


@router.message(F.text == "/done")
async def convert_to_pdf(message: Message, state: FSMContext):
    data = await state.get_data()
    session_id = data.get("session_id")

    if not session_id:
        return await message.reply("Hech qanday rasm topilmadi.")

    user_dir = settings.TEMP_DIR / f"{message.from_user.id}_{session_id}"
    image_files = sorted([p for p in user_dir.iterdir() if p.suffix.lower() in [".jpg", ".jpeg", ".png"]])

    if not image_files:
        return await message.reply("Rasmlar topilmadi.")

    output_pdf = user_dir / "result.pdf"

    a4_width_pt = img2pdf.mm_to_pt(210)
    a4_height_pt = img2pdf.mm_to_pt(297)
    layout_fun = img2pdf.get_layout_fun(pagesize=(a4_width_pt, a4_height_pt))

    with open(output_pdf, "wb") as f:
        f.write(img2pdf.convert([str(p) for p in image_files], layout_fun=layout_fun))

    async with aiofiles.open(output_pdf, "rb") as f:
        await message.answer_document(
            document=BufferedInputFile(file=await f.read(), filename=output_pdf.name),
            caption=_("Fayl muvaffaqiyatli o'zgartirildi!"),
        )

    for file in user_dir.glob("*"):
        file.unlink()

    user_dir.rmdir()

    await state.clear()
