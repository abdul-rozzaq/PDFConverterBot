from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_conversion_keyboard(file_type: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    if file_type == "pdf":
        builder.row(
            InlineKeyboardButton(text="📄 To Word", callback_data="convert:pdf_to_word"),
            InlineKeyboardButton(text="🖼 To Images", callback_data="convert:pdf_to_images")
        )
        builder.row(
            InlineKeyboardButton(text="📝 To Text", callback_data="convert:pdf_to_text")
        )
    elif file_type == "docx":
        builder.row(
            InlineKeyboardButton(text="📄 To PDF", callback_data="convert:word_to_pdf")
        )
    elif file_type == "xlsx":
        builder.row(
            InlineKeyboardButton(text="📊 To PDF", callback_data="convert:excel_to_pdf")
        )
    elif file_type in ["jpg", "jpeg", "png", "webp"]:
        builder.row(
            InlineKeyboardButton(text="📄 To PDF", callback_data="convert:image_to_pdf"),
            InlineKeyboardButton(text="🔍 OCR", callback_data="convert:ocr_extract")
        )
        builder.row(
            InlineKeyboardButton(text="🗜 Compress", callback_data="convert:compress_image"),
            InlineKeyboardButton(text="⚫ Grayscale", callback_data="convert:image_grayscale")
        )
        builder.row(
            InlineKeyboardButton(text="📏 Resize", callback_data="convert:resize_image"),
            InlineKeyboardButton(text="🔄 Format", callback_data="convert:convert_format")
        )
    
    return builder.as_markup()

def get_language_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🇺🇸 English", callback_data="lang:en"),
        InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang:uz"),
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru")
    )
    return builder.as_markup()

def get_image_format_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="JPG", callback_data="format:jpg"),
        InlineKeyboardButton(text="PNG", callback_data="format:png"),
        InlineKeyboardButton(text="WebP", callback_data="format:webp")
    )
    return builder.as_markup()

def get_resize_options_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📱 Mobile (480x640)", callback_data="resize:480x640"),
        InlineKeyboardButton(text="💻 Desktop (1920x1080)", callback_data="resize:1920x1080")
    )
    builder.row(
        InlineKeyboardButton(text="📐 Custom", callback_data="resize:custom")
    )
    return builder.as_markup()
