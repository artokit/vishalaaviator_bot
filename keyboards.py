from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from telebot import types

start = InlineKeyboardBuilder()
start.row(InlineKeyboardButton(text='🚀START🚀', callback_data='menu'))

trial_button = InlineKeyboardBuilder()
trial_button.row(InlineKeyboardButton(text='✅3 DAYS FREE✅', callback_data='start_trial'))

make_money = InlineKeyboardBuilder()
make_money.row(InlineKeyboardButton(text='💵MAKE MONEY💵', callback_data='make_money'))

register_button = InlineKeyboardBuilder()
register_button.row(InlineKeyboardButton(text='📲REGISTER', url='https://avtorpromt.com/mbYxys'))

help_button = types.InlineKeyboardMarkup()
help_button.add(types.InlineKeyboardButton(text='HELP', url='https://t.me/vishalaviator'))

res_of_game = InlineKeyboardBuilder()
res_of_game.row(
    InlineKeyboardButton(text='WIN', callback_data='game:win'),
    InlineKeyboardButton(text='LOSE', callback_data='game:lose')
)
