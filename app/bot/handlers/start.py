from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.core.database import async_session_maker
from app.bot.keyboards.inline import get_language_keyboard

router = Router()

@router.message(CommandStart())
async def start_handler(message: Message, _):
    """Handle /start command"""
    user_id = message.from_user.id
    
    # Create or update user in database
    async with async_session_maker() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            user = User(
                telegram_id=user_id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name
            )
            session.add(user)
            await session.commit()
    
    await message.answer(_('welcome'))

@router.message(Command('language'))
async def language_handler(message: Message, _):
    """Handle /language command"""
    await message.answer(
        _('select_language'),
        reply_markup=get_language_keyboard()
    )

@router.callback_query(F.data.startswith('lang:'))
async def language_callback(callback: CallbackQuery, _):
    """Handle language selection"""
    lang = callback.data.split(':')[1]
    user_id = callback.from_user.id
    
    # Update user language in database
    async with async_session_maker() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            user.language = lang
            await session.commit()
    
    await callback.answer(_('language_changed'))
    await callback.message.edit_text(_('language_changed'))

@router.message(Command('help'))
async def help_handler(message: Message, _):
    """Handle /help command"""
    help_text = _('''
🤖 **Document Converter Bot Help**

**Supported Conversions:**
📄 PDF ↔ Word (.docx)
🖼 PDF ↔ Images (PNG, JPG)
📝 PDF → Text
📊 Excel ↔ PDF
🔍 OCR: Extract text from images
🖼 Image processing (compress, resize, format conversion)

**How to use:**
1. Send me a document or image
2. Choose the conversion type from the menu
3. Wait for processing
4. Download your converted file

**Commands:**
/start - Start the bot
/help - Show this help
/language - Change language
/stats - View your usage statistics

**File Limits:**
- Maximum file size: 50MB
- Supported formats: PDF, DOCX, XLSX, JPG, PNG, WebP

For support: @your_support_username
    ''')
    
    await message.answer(help_text)