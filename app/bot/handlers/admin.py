from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.user import User, ConversionHistory
from app.core.database import async_session_maker
from app.core.config import settings

router = Router()

def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id in settings.ADMIN_IDS

@router.message(Command('stats'))
async def stats_handler(message: Message, _):
    """Show user statistics"""
    user_id = message.from_user.id
    
    async with async_session_maker() as session:
        # Get user's conversion count
        result = await session.execute(
            select(func.count(ConversionHistory.id))
            .where(ConversionHistory.user_id == user_id)
        )
        conversion_count = result.scalar()
        
        # Get user's total file size processed
        result = await session.execute(
            select(func.sum(ConversionHistory.file_size))
            .where(ConversionHistory.user_id == user_id)
        )
        total_size = result.scalar() or 0
        
        # Get most used conversion type
        result = await session.execute(
            select(ConversionHistory.conversion_type, func.count(ConversionHistory.id))
            .where(ConversionHistory.user_id == user_id)
            .group_by(ConversionHistory.conversion_type)
            .order_by(func.count(ConversionHistory.id).desc())
            .limit(1)
        )
        most_used = result.first()
        
        stats_text = f"""
📊 **Your Statistics**

🔄 Total conversions: {conversion_count}
📁 Total data processed: {total_size / (1024*1024):.2f} MB
⭐ Most used: {most_used[0] if most_used else 'None'}

Thank you for using our bot! 🤖
        """
        
        await message.answer(stats_text)

@router.message(Command('admin'))
async def admin_panel(message: Message, _):
    """Admin panel (only for admins)"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Access denied")
        return
        
    async with async_session_maker() as session:
        # Get total users
        result = await session.execute(select(func.count(User.id)))
        total_users = result.scalar()
        
        # Get active users (used bot in last 7 days)
        result = await session.execute(
            select(func.count(func.distinct(ConversionHistory.user_id)))
            .where(ConversionHistory.created_at >= func.date('now', '-7 days'))
        )
        active_users = result.scalar()
        
        # Get total conversions
        result = await session.execute(select(func.count(ConversionHistory.id)))
        total_conversions = result.scalar()
        
        # Get total data processed
        result = await session.execute(select(func.sum(ConversionHistory.file_size)))
        total_data = result.scalar() or 0
        
        # Get top conversion types
        result = await session.execute(
            select(ConversionHistory.conversion_type, func.count(ConversionHistory.id))
            .group_by(ConversionHistory.conversion_type)
            .order_by(func.count(ConversionHistory.id).desc())
            .limit(5)
        )
        top_conversions = result.all()
        
        admin_text = f"""
🔧 **Admin Panel**

👥 Total users: {total_users}
📈 Active users (7 days): {active_users}
🔄 Total conversions: {total_conversions}
💾 Total data processed: {total_data / (1024*1024*1024):.2f} GB

📊 **Top Conversion Types:**
        """
        
        for conv_type, count in top_conversions:
            admin_text += f"\n• {conv_type}: {count}"
            
        await message.answer(admin_text)

@router.message(Command('broadcast'))
async def broadcast_handler(message: Message, _):
    """Broadcast message to all users (admin only)"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Access denied")
        return
        
    # This is a simplified version - in production, use proper broadcast system
    await message.answer("""
📢 **Broadcast System**

To broadcast a message, reply to this message with your broadcast text.
        """)
