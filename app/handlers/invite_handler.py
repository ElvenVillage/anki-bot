from aiogram.types import Message
from aiogram import Router
from asyncpg.connection import Connection
from aiogram.fsm.context import FSMContext
from state import AnkiState
from empty_state_keyboard import empty_state_keyboard
router = Router()

@router.message(AnkiState.inviting_deck)
async def accept_invite_handler(message: Message, conn: Connection, state: FSMContext) -> None:
    invite_link = message.text
    deck = await conn.fetch("SELECT (deck_id, deck_name) FROM decks WHERE deck_invite_link = $1", invite_link)
    if not deck:
        await message.reply("Некорректное приглашение", reply_markup=empty_state_keyboard())
        await state.clear()
        return
    
    deck_name = deck[0]["row"][1]
    deck_id = deck[0]["row"][0]
    user_id = message.chat.id
    
    try:
        await conn.execute("INSERT INTO user_deck (user_id, deck_id) VALUES ($1, $2)", 
                       user_id, deck_id)
    except:
        await message.reply("Вы уже изучаете эту колоду!", reply_markup=empty_state_keyboard())
        await state.clear()
        return
    
    await message.reply(f"Колода {deck_name} добавлена для изучения!")
