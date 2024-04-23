import uuid
from aiogram.types import Message
from aiogram import Router
from asyncpg.connection import Connection
from aiogram.fsm.context import FSMContext
from state import AnkiState
from empty_state_keyboard import empty_state_keyboard
router = Router()

# создание новой колоды (с нуля)
@router.message(AnkiState.creating_deck)
async def name_new_deck_handler(message: Message, conn: Connection, state: FSMContext) -> None:
    user_id = message.chat.id
    deck_name = message.text
    last_row = await conn.fetch("SELECT deck_id FROM decks ORDER BY deck_id DESC LIMIT 1")
    last_deck = [dict(row) for row in last_row]
    
    deck_id = 0
    if last_deck:
        deck_id = last_deck[0]["deck_id"] + 1

    invite_link = str(uuid.uuid4())

    await conn.execute("INSERT INTO decks (deck_id, deck_name, deck_invite_link) VALUES ($1, $2, $3)", 
                       deck_id, deck_name, invite_link)
    await conn.execute("INSERT INTO user_decks (user_id, deck_id) VALUES ($1, $2)", user_id, deck_id)
    
    await message.answer(f"Создана колода {deck_name}!\nИнвайт-код: {invite_link}", 
                         reply_markup=empty_state_keyboard())
    await state.clear()
