from aiogram.types import Message, ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.formatting import Text, Bold, Italic
from aiogram import Router
from asyncpg.connection import Connection
from aiogram.fsm.context import FSMContext
from state import AnkiState
from handlers import learning_handler
from empty_state_keyboard import empty_state_keyboard


router = Router()

__start_learning = "Приступить к изучению"
__add_new_cards = "Добавить карточек"
__cancel_command = "Отменить"
__create_new_deck = "Создать колоду"
__handle_invite_code = "У меня есть инвайт"

@router.message(AnkiState.confirm_deck_selection)
async def confirm_deck_selection_handler(message: Message, state: FSMContext, conn: Connection) -> None:
    command = message.text.lower()

    if command == __start_learning.lower():
        await state.set_state(AnkiState.learning)
        await learning_handler.learning_handler(message, state, conn)
        return
    
    if command == __add_new_cards.lower():
        await state.set_state(AnkiState.adding_cards)
        content = Text("Вводите пары слов, разделенных переводом строки. Например:\n", 
                Italic("la ciudad\nгород"))
        await message.answer(**content.as_kwargs(), reply_markup=ReplyKeyboardRemove())
        return

    if command == __cancel_command.lower():
        await state.clear()
        await message.answer("ОК", reply_markup=empty_state_keyboard())
        return

# Выбор колоды для изучения из списка доступных
@router.message(AnkiState.selecting_deck)
async def select_deck_handler(message: Message, state: FSMContext, conn: Connection) -> None:
    user_id = message.chat.id

    command = message.text.lower()
    if command == __create_new_deck.lower():
        await state.set_state(AnkiState.creating_deck)
        await message.answer("Введите название для новой колоды:", reply_markup=ReplyKeyboardRemove())
        return
    
    if command == __handle_invite_code.lower():
        await state.set_state(AnkiState.inviting_deck)
        await message.answer("Введите инвайт-код", reply_markup=ReplyKeyboardRemove())
        return


    deck_row = await conn.fetch(
        "SELECT user_decks.deck_id, decks.deck_name FROM user_decks "
        "LEFT JOIN decks ON decks.deck_id = user_decks.deck_id "
        "WHERE decks.deck_name = $1 AND user_decks.user_id = $2", 
        message.text, user_id
    )
    
    if not deck_row:
        await message.answer("Некорректная колода", reply_markup=empty_state_keyboard())
        return
    
    deck_id = deck_row[0]["deck_id"]
    deck_name = deck_row[0]["deck_name"]

    await state.set_state(AnkiState.confirm_deck_selection)
    await state.update_data(selected_deck=deck_id)

    content = Text("Выбрана колода ", Bold(deck_name))
    buttons = [
        [KeyboardButton(text=__start_learning), KeyboardButton(text=__add_new_cards)],
        [KeyboardButton(text=__cancel_command),]
    ]
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )

    await message.answer(**content.as_kwargs(), reply_markup=keyboard)
