from aiogram import Router
from asyncpg.connection import Connection
from aiogram.utils.formatting import Text, Spoiler, Bold
from datetime import datetime, timedelta
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from state import AnkiState
from empty_state_keyboard import empty_state_keyboard

router = Router()

__enough_for_now = "Пока хватит"
__add_cards_from_deck = "Добавить карт из колоды"

__next_repetitions_by_progress = {
    1: timedelta(minutes=2),
    2: timedelta(minutes=15),
    3: timedelta(days=1),
    4: timedelta(days=5),
    5: timedelta(days=30)
}

def get_next_repetition(last_repetition: datetime, progress: int, user_answer: bool) -> tuple[datetime, int]:
    new_progress = progress
    if user_answer:
        new_progress += 1
    else:
        new_progress -= 1
        
    if new_progress <= 0:
        new_progress = 1
    if new_progress >= 5:
        new_progress = 5
    
    
    return (
        last_repetition + __next_repetitions_by_progress[new_progress], 
        new_progress
    )


@router.message(AnkiState.learning)
async def learning_handler(message: Message, state: FSMContext, conn: Connection) -> None:
    user_id = message.chat.id

    user_data = await state.get_data()
    current_deck_id = user_data["selected_deck"]

    current_repetition = user_data.get("current_repetition") # id текущей карты в repetitions
    prev_progress = user_data.get("progress")

    user_command = message.text.lower()

    if (user_command == __add_cards_from_deck.lower()):
        available_cards = await conn.fetch(
            "SELECT (cards.card_id) FROM cards "
            "LEFT JOIN repetitions ON repetitions.card_id = cards.card_id "
            "WHERE repetitions.card_id IS NULL LIMIT 10"
        )

        if not available_cards:
            await state.clear()
            await message.reply(
                "Колода полностью изучена! Возвращайтесь позже", 
                reply_markup=empty_state_keyboard()
            )
            return
        else:
            await conn.execute(
                "INSERT INTO repetitions (user_id, card_id, latest_review, progress, next_repeat) "
                f"SELECT {user_id}, cards.card_id, NOW(), 1, NOW() FROM cards "
                "LEFT JOIN repetitions ON repetitions.card_id = cards.card_id "
                "WHERE repetitions.card_id IS NULL LIMIT 10"
            )
            
            buttons = [[KeyboardButton(text="Продолжить повторение")]]
            keyboard = ReplyKeyboardMarkup(keyboard=buttons,resize_keyboard=True)
            await message.reply(f"Добавлено {len(available_cards)} карт!", reply_markup=keyboard)
            return

    if (user_command == __enough_for_now.lower()):
        await state.clear()
        await message.reply("OK!", reply_markup=empty_state_keyboard())
        return
    
    if current_repetition and (user_command == "помню" or user_command == "не помню"):
        user_answer = user_command == "помню"
        (next_repetition, new_progress) = get_next_repetition(datetime.now(), prev_progress, user_answer)
        
        await conn.execute(
            "UPDATE repetitions "
            "SET "
                "latest_review = $1, "
                "next_repeat = $2, "
                "progress = $3 "
            "WHERE rep_id = $4",
            datetime.now(), next_repetition, new_progress, current_repetition
        )

    # найдем слова, которые необходимо повторить
    need_repetition_card = await conn.fetch(
        "SELECT repetitions.rep_id, repetitions.card_id, cards.front, cards.back, repetitions.latest_review, repetitions.progress FROM repetitions "
        "INNER JOIN cards ON cards.card_id = repetitions.card_id "
        "INNER JOIN decks ON cards.deck_id = decks.deck_id "
        "WHERE  "
            "repetitions.user_id = $1 "
            "AND cards.deck_id = $2 "
            "AND repetitions.next_repeat < now()"
            "ORDER BY repetitions.next_repeat LIMIT 1", 
        user_id, current_deck_id
    )
    
    if not need_repetition_card:
        # не удалось найти ни одной карточки -> нужно добавить больше
        buttons = [[
            KeyboardButton(text=__add_cards_from_deck),
            KeyboardButton(text=__enough_for_now)
        ]]
    
        keyboard = ReplyKeyboardMarkup(
            keyboard=buttons,
            resize_keyboard=True
        )

        await message.answer("У вас нет карточек для изучения!", reply_markup=keyboard)
        return
    else:
        card_data = [dict(card) for card in need_repetition_card][0]
        front = card_data["front"]
        back = card_data["back"]

        learning_buttons = [[KeyboardButton(text="Помню"), KeyboardButton(text="Не помню")]]
    
        learning_keyboard = ReplyKeyboardMarkup(
            keyboard=learning_buttons,
            resize_keyboard=True
        )
        await state.update_data(
            current_repetition=card_data["rep_id"], 
            progress=card_data["progress"],
            latest_review=card_data["latest_review"]
        )

        answer_content = Text(Bold(front), '\n\n', Spoiler(back))
        await message.answer(**answer_content.as_kwargs(), reply_markup=learning_keyboard)



