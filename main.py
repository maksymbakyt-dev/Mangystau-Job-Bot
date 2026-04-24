import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from database.engine import init_db, AsyncSessionLocal
from handlers import common, seeker, employer

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Токен бота
BOT_TOKEN = "8699990512:AAEZELT7aYObPfwVKpKUKYGA-WWgA1m0Zs0"

# Middleware для передачи сессии БД в хэндлеры
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Callable, Dict, Any, Awaitable

class DbSessionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async with AsyncSessionLocal() as session:
            data['session'] = session
            return await handler(event, data)

async def dummy_server():
    from aiohttp import web
    import os
    
    async def handle(request):
        return web.Response(text="Bot is running!")
        
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Dummy web server started on port {port}")

async def main():
    # Инициализация БД
    await init_db()
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Подключаем middleware
    dp.message.middleware(DbSessionMiddleware())
    dp.callback_query.middleware(DbSessionMiddleware())
    
    # Подключаем роутеры
    dp.include_router(common.router)
    dp.include_router(seeker.router)
    dp.include_router(employer.router)
    
    # Запускаем фейковый веб-сервер для Render
    await dummy_server()
    
    print("Бот успешно запущен!")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
