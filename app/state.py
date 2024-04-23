from aiogram.fsm.state import State, StatesGroup

class AnkiState(StatesGroup):
    selecting_deck = State()
    confirm_deck_selection = State()
    adding_cards = State()
    inviting_deck = State()
    creating_deck = State()
    learning = State()
