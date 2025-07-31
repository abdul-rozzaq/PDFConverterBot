import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.types import Update
from aiohttp import web
from aiohttp.web_app import Application

from app.core.config import settings
from app.core.database import create_tables
from app.bot.handlers import start, convert, admin
from app.bot.middlewares.lang import LanguageMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

# Register middlewares
dp.message.middleware(LanguageMiddleware())
dp.callback_query.middleware(LanguageMiddleware())

# Register routers
dp.include_router(start.router)
dp.include_router(convert.router)
dp.include_router(admin.router)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await create_tables()
    
    # Set webhook
    webhook_url = f"{settings.WEBHOOK_URL}{settings.WEBHOOK_PATH}"
    await bot.set_webhook(
        url=webhook_url,
        secret_token=settings.WEBHOOK_SECRET
    )
    
    logger.info(f"Webhook set to {webhook_url}")
    
    yield
    
    # Shutdown
    await bot.delete_webhook()
    await bot.session.close()

# Create FastAPI app
app = FastAPI(
    title="Telegram Document Converter Bot",
    description="A powerful document and image converter bot for Telegram",
    version="1.0.0",
    lifespan=lifespan
)

@app.post(settings.WEBHOOK_PATH)
async def webhook_handler(request: Request):
    """Handle webhook updates from Telegram"""
    try:
        # Verify secret token
        secret_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if secret_token != settings.WEBHOOK_SECRET:
            raise HTTPException(status_code=403, detail="Invalid secret token")
        
        # Get update data
        update_data = await request.json()
        update = Update(**update_data)
        
        # Process update
        await dp.feed_update(bot, update)
        
        return JSONResponse({"status": "ok"})
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Telegram Document Converter Bot is running"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        # Test bot connection
        bot_info = await bot.get_me()
        
        return {
            "status": "healthy",
            "bot": {
                "id": bot_info.id,
                "username": bot_info.username,
                "first_name": bot_info.first_name
            },
            "webhook": {
                "url": f"{settings.WEBHOOK_URL}{settings.WEBHOOK_PATH}",
                "is_set": True
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )

@app.get("/stats")
async def get_stats():
    """Get bot statistics (admin endpoint)"""
    try:
        from app.core.database import async_session_maker
        from app.models.user import User, ConversionHistory
        from sqlalchemy import select, func
        
        async with async_session_maker() as session:
            # Get total users
            result = await session.execute(select(func.count(User.id)))
            total_users = result.scalar()
            
            # Get total conversions
            result = await session.execute(select(func.count(ConversionHistory.id)))
            total_conversions = result.scalar()
            
            return {
                "total_users": total_users,
                "total_conversions": total_conversions
            }
            
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )
