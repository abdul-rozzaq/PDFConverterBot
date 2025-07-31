import os
from typing import List
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.models.user import ConversionHistory
from app.core.database import async_session_maker
from app.bot.keyboards.inline import get_conversion_keyboard
from app.bot.utils.converters import DocumentConverter, ImageProcessor, OCRProcessor, create_zip_archive
from app.bot.utils.helpers import get_file_info, is_file_size_valid, get_file_type_from_mime, cleanup_temp_files, save_telegram_file

router = Router()


class ConversionStates(StatesGroup):
    waiting_for_custom_size = State()
    waiting_for_multiple_images = State()


# Global instances
doc_converter = DocumentConverter()
img_processor = ImageProcessor()
ocr_processor = OCRProcessor()


@router.message(F.document | F.photo)
async def handle_file(message: Message, bot: Bot, _):
    """Handle incoming files"""
    try:
        # Get file info
        if message.document:
            file_id = message.document.file_id
            file_name = message.document.file_name
            file_size = message.document.file_size
        else:  # photo
            file_id = message.photo[-1].file_id  # Get highest resolution
            file_name = f"photo_{file_id[:10]}.jpg"
            file_size = message.photo[-1].file_size

        # Check file size
        if not is_file_size_valid(file_size):
            await message.answer(_("file_too_large"))
            return

        # Download file
        file_info = await bot.get_file(file_id)
        file_content = await bot.download_file(file_info.file_path)

        # Save to temp storage
        local_path = await save_telegram_file(file_name, file_content.read())

        # Get file type
        mime_type, actual_size, extension = await get_file_info(local_path)
        file_type = get_file_type_from_mime(mime_type)

        if not file_type:
            await message.answer(_("unsupported_format"))
            await cleanup_temp_files(local_path)
            return

        # Store file info in user data
        await message.answer(_("choose_conversion"), reply_markup=get_conversion_keyboard(file_type))

        # Store file path for later use (in production, use Redis or similar)
        # For now, we'll store in bot data
        bot.data = getattr(bot, "data", {})
        bot.data[message.from_user.id] = {"file_path": local_path, "file_type": file_type, "original_name": file_name}

    except Exception as e:
        await message.answer(_("error"))
        print(f"File handling error: {e}")


@router.callback_query(F.data.startswith("convert:"))
async def handle_conversion(callback: CallbackQuery, bot: Bot, state: FSMContext, _):
    """Handle conversion requests"""
    try:
        conversion_type = callback.data.split(":")[1]
        user_id = callback.from_user.id

        # Get stored file info
        user_data = getattr(bot, "data", {}).get(user_id)
        if not user_data:
            await callback.answer("File not found. Please send a new file.")
            return

        file_path = user_data["file_path"]
        original_name = user_data["original_name"]

        # Show processing message
        processing_msg = await callback.message.answer(_("processing"))

        # Perform conversion based on type
        result_files = await perform_conversion(conversion_type, file_path, state, _)

        if result_files:
            # Send converted files
            await send_converted_files(callback.message, result_files, bot)

            # Log conversion
            await log_conversion(user_id, conversion_type, original_name, os.path.getsize(file_path))

            await processing_msg.edit_text(_("completed"))
        else:
            await processing_msg.edit_text(_("error"))

        # Cleanup
        await cleanup_temp_files(file_path, *result_files)

        # Clear user data
        if hasattr(bot, "data") and user_id in bot.data:
            del bot.data[user_id]

    except Exception as e:
        await callback.answer(_("error"))
        print(f"Conversion error: {e}")


async def perform_conversion(conversion_type: str, file_path: str, state: FSMContext, _) -> List[str]:
    """Perform the actual conversion"""
    try:
        if conversion_type == "pdf_to_word":
            result = await doc_converter.pdf_to_word(file_path)
            return [result]

        elif conversion_type == "word_to_pdf":
            result = await doc_converter.word_to_pdf(file_path)
            return [result]

        elif conversion_type == "pdf_to_images":
            results = await doc_converter.pdf_to_images(file_path)
            return results

        elif conversion_type == "image_to_pdf":
            result = await doc_converter.images_to_pdf([file_path])
            return [result]

        elif conversion_type == "pdf_to_text":
            result = await doc_converter.pdf_to_text(file_path)
            return [result]

        elif conversion_type == "excel_to_pdf":
            result = await doc_converter.excel_to_pdf(file_path)
            return [result]

        elif conversion_type == "ocr_extract":
            result = await ocr_processor.extract_text_easyocr(file_path)
            return [result]

        elif conversion_type == "compress_image":
            result = await img_processor.compress_image(file_path)
            return [result]

        elif conversion_type == "image_grayscale":
            result = await img_processor.convert_to_grayscale(file_path)
            return [result]

        elif conversion_type == "resize_image":
            # This would need user input for custom sizes
            result = await img_processor.resize_image(file_path, 1024, 768)  # Default size
            return [result]

        elif conversion_type == "convert_format":
            # Default to PNG for now
            result = await img_processor.convert_format(file_path, "PNG")
            return [result]

        return []

    except Exception as e:
        print(f"Conversion failed: {e}")
        return []


async def send_converted_files(message: Message, file_paths: List[str], bot: Bot):
    """Send converted files to user"""
    try:
        if len(file_paths) == 1:
            # Send single file
            file_path = file_paths[0]
            document = FSInputFile(file_path)
            await bot.send_document(message.chat.id, document)
        else:
            # Create ZIP archive for multiple files
            zip_path = await create_zip_archive(file_paths, "converted_files")
            document = FSInputFile(zip_path)
            await bot.send_document(message.chat.id, document)
            file_paths.append(zip_path)  # Add to cleanup list

    except Exception as e:
        print(f"Failed to send files: {e}")


async def log_conversion(user_id: int, conversion_type: str, filename: str, file_size: int):
    """Log conversion to database"""
    try:
        async with async_session_maker() as session:
            history = ConversionHistory(user_id=user_id, conversion_type=conversion_type, original_filename=filename, file_size=file_size, status="completed")
            session.add(history)
            await session.commit()
    except Exception as e:
        print(f"Failed to log conversion: {e}")


# Callback handlers for specific conversion options
@router.callback_query(F.data.startswith("format:"))
async def handle_format_selection(callback: CallbackQuery, bot: Bot, _):
    """Handle image format selection"""
    format_type = callback.data.split(":")[1]
    user_id = callback.from_user.id

    user_data = getattr(bot, "data", {}).get(user_id)
    if not user_data:
        await callback.answer("File not found. Please send a new file.")
        return

    file_path = user_data["file_path"]

    try:
        processing_msg = await callback.message.answer(_("processing"))
        result = await img_processor.convert_format(file_path, format_type.upper())

        if result:
            document = FSInputFile(result)
            await bot.send_document(callback.message.chat.id, document)
            await processing_msg.edit_text(_("completed"))

            # Cleanup
            await cleanup_temp_files(result)
        else:
            await processing_msg.edit_text(_("error"))

    except Exception as e:
        await callback.answer(_("error"))
        print(f"Format conversion error: {e}")


@router.callback_query(F.data.startswith("resize:"))
async def handle_resize_selection(callback: CallbackQuery, bot: Bot, state: FSMContext, _):
    """Handle image resize selection"""
    resize_option = callback.data.split(":")[1]
    user_id = callback.from_user.id

    user_data = getattr(bot, "data", {}).get(user_id)
    if not user_data:
        await callback.answer("File not found. Please send a new file.")
        return

    if resize_option == "custom":
        await callback.message.answer("Please send the desired dimensions (e.g., 800x600):")
        await state.set_state(ConversionStates.waiting_for_custom_size)
        return

    # Parse predefined dimensions
    if "x" in resize_option:
        width, height = map(int, resize_option.split("x"))
        file_path = user_data["file_path"]

        try:
            processing_msg = await callback.message.answer(_("processing"))
            result = await img_processor.resize_image(file_path, width, height)

            if result:
                document = FSInputFile(result)
                await bot.send_document(callback.message.chat.id, document)
                await processing_msg.edit_text(_("completed"))

                # Cleanup
                await cleanup_temp_files(result)
            else:
                await processing_msg.edit_text(_("error"))

        except Exception as e:
            await callback.answer(_("error"))
            print(f"Resize error: {e}")


@router.message(ConversionStates.waiting_for_custom_size)
async def handle_custom_size(message: Message, bot: Bot, state: FSMContext, _):
    """Handle custom size input"""
    try:
        dimensions = message.text.strip()
        if "x" not in dimensions:
            await message.answer("Invalid format. Please use format like: 800x600")
            return

        width, height = map(int, dimensions.split("x"))
        user_id = message.from_user.id

        user_data = getattr(bot, "data", {}).get(user_id)
        if not user_data:
            await message.answer("File not found. Please send a new file.")
            await state.clear()
            return

        file_path = user_data["file_path"]

        processing_msg = await message.answer(_("processing"))
        result = await img_processor.resize_image(file_path, width, height)

        if result:
            document = FSInputFile(result)
            await bot.send_document(message.chat.id, document)
            await processing_msg.edit_text(_("completed"))

            # Cleanup
            await cleanup_temp_files(result)
        else:
            await processing_msg.edit_text(_("error"))

        await state.clear()

    except ValueError:
        await message.answer("Invalid dimensions. Please use format like: 800x600")
    except Exception as e:
        await message.answer(_("error"))
        await state.clear()
        print(f"Custom resize error: {e}")
