from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()

@router.message(Command("help"))
async def help_handler(message: Message) -> None:
    await message.answer("/decks для начала работы с колодами")