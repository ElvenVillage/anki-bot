from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def empty_state_keyboard() -> ReplyKeyboardMarkup:
    buttons = [[
        KeyboardButton(text="Доступные колоды")
    ]]
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )
    
    return keyboard