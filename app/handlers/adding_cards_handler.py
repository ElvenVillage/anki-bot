from aiogram.types import Message
from aiogram import Router
from asyncpg.connection import Connection
from aiogram.fsm.context import FSMContext
from aiogram.utils.formatting import Text
from state import AnkiState
from empty_state_keyboard import empty_state_keyboard
router = Router()

@router.message(AnkiState.adding_cards)
async def adding_cards_handler(message: Message, state: FSMContext, conn: Connection) -> None:
    user_state = await state.get_data()
    selected_deck = user_state["selected_deck"]
    # if not selected_deck:
    #     await message.answer("Не выбрана колода")
    #     await state.clear()
    #     return
    
    data = message.text
    lines = data.split("\n")
    
    if len(lines) % 2 != 0:
        await message.answer("Некорректный формат", reply_markup=empty_state_keyboard())
        await state.clear()
        return
    
    data_to_insert = []
    
    for i in range(0, len(lines), 2):
        data_to_insert.append(
            (selected_deck, lines[i], lines[i+1])
        )
    
    await conn.executemany(
        "INSERT INTO cards (deck_id, front, back) VALUES "
        "($1, $2, $3)", 
        data_to_insert)
    
    content = Text("Добавлены ", str(len(data_to_insert)), " новые карточки")
    await message.answer(**content.as_kwargs(), reply_markup=empty_state_keyboard())
    await state.clear()
    return
