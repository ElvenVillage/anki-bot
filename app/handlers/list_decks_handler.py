from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.formatting import as_list, as_marked_section, Bold
from aiogram import Router, F
from asyncpg.connection import Connection
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from state import AnkiState

router = Router()

# список колод, к которым имеет доступ пользователь
@router.message(F.text, Command("decks"))
@router.message(F.text == "Доступные колоды")
async def list_decks_handler(message: Message, conn: Connection, state: FSMContext) -> None:
    user_id = message.chat.id
    await state.set_state(AnkiState.selecting_deck)

    deck_rows = await conn.fetch("SELECT decks.deck_id, decks.deck_name "
                                 "FROM user_decks "
                                 "LEFT JOIN decks ON user_decks.deck_id = decks.deck_id "
                                  "WHERE user_id = $1", 
                                 user_id)
    
    decks = [dict(deck_row) for deck_row in deck_rows]
    
    buttons = [[
        KeyboardButton(text="Создать колоду"),
        KeyboardButton(text="У меня есть инвайт")
        ]]
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )

    if not decks:
        await message.answer("У вас нет ни одной колоды", reply_markup=keyboard)
    else:
        buttons = [ 
        [
          KeyboardButton(text="Создать колоду"),
          KeyboardButton(text="У меня есть инвайт")
        ]]
        
        for deck in decks:
            buttons.insert(0, [KeyboardButton(text=deck["deck_name"])])
       
        keyboard = ReplyKeyboardMarkup(
            keyboard=buttons,
            resize_keyboard=True
        )
        
        content = as_list(
            as_marked_section(
                Bold("Колоды: "),
                *[deck["deck_name"] for deck in decks],
                marker="✅ "
            )
        )
        await message.answer(**content.as_kwargs(), reply_markup=keyboard)
