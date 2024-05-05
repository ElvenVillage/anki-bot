import asyncio
from os import getenv
from aiogram import Bot, Dispatcher, Router
from aiogram.filters import CommandStart
from aiogram.utils.formatting import Text
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from db import DbPoolMiddleware, create_db_pool
from empty_state_keyboard import empty_state_keyboard

import handlers.create_deck_handler
import handlers.invite_handler
import handlers.learning_handler
import handlers.list_decks_handler
import handlers.select_deck_handler
import handlers.adding_cards_handler
import handlers.help_handler

TOKEN = getenv("TG_TOKEN")
dp = Dispatcher(storage=MemoryStorage())


start_router = Router()


@start_router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    content = Text("Добро пожаловать! Вы можете приступить к работе с колодами.")
    
    await message.answer(**content.as_kwargs(), reply_markup=empty_state_keyboard())

async def main() -> None:
    bot = Bot(TOKEN)
    dp.include_routers(
        start_router, 
        handlers.create_deck_handler.router,
        handlers.invite_handler.router,
        handlers.learning_handler.router,
        handlers.list_decks_handler.router,
        handlers.select_deck_handler.router,
        handlers.adding_cards_handler.router,
        handlers.help_handler.router
    )

    db_pool = await create_db_pool()
    dp.update.middleware(DbPoolMiddleware(db_pool))

    await dp.start_polling(bot)



if __name__ == "__main__":
    asyncio.run(main())
