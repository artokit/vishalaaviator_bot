import random
import threading
from aiogram import Dispatcher, Bot, F
import os
import asyncio
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile, CallbackQuery
from telebot import TeleBot
import keyboards
import states
import time
import db_api


VIDEO_PATH = os.path.join(os.path.dirname(__file__), 'videos')
PHOTOS_PATH = os.path.join(os.path.dirname(__file__), 'photos')
CHANNEL_ID_POSTBACK = -1001919193583
TEST_GAME_IDS = {

}

ID_TO_CHECK = {

}


async def send_video(user_id, video_name, **kwargs):
    if video_name not in media_hash:
        message = await bot.send_video(
            user_id,
            FSInputFile(os.path.join(VIDEO_PATH, video_name), filename=video_name),
            **kwargs
        )
        media_hash[video_name] = message.video.file_id
    else:
        await bot.send_video(user_id, media_hash[video_name], **kwargs)


async def register(user_id, code):
    await send_photo(
        user_id,
        'reg.jpg',
        caption='Friend, you have passed the registration!🔥\n'
                'To activate my bot you need to make a deposit of 2000Rs on this link - https://avtorpromt.com/mbYxys\n'
                'But I will make an exception for you!\n'
                'Deposit 🛑1000Rs🛑 and write here your ID\n'
                'This is a prerequisite! \n'
                '🔥My subscribers are already earning from 5000Rs per day! 🔥\n'
                'Don\'t miss your chance!🙏\n',
        reply_markup=keyboards.contact_button.as_markup()
    )

    await db_api.update_postback(user_id, code)


async def send_photo(user_id, photo_name, **kwargs):
    if photo_name not in media_hash:
        message = await bot.send_photo(
            user_id,
            FSInputFile(os.path.join(PHOTOS_PATH, photo_name), filename=photo_name),
            **kwargs
        )
        media_hash[photo_name] = message.photo[-1].file_id
    else:
        await bot.send_photo(user_id, media_hash[photo_name], **kwargs)


async def send_predict(message: Message, markup=None):
    if markup is None:
        markup = keyboards.res_of_game.as_markup()

    site_id = (await db_api.get_postback_by_user_id(message.chat.id))[0][0]
    await message.answer(
        f'PLAYER ID: {site_id}\n'
        f'CASHOUT {random.randint(100, 400) / 100}✅',
        reply_markup=markup
    )


def site_id_in_checker(site_id):
    for i in ID_TO_CHECK:
        if ID_TO_CHECK[i][1] == site_id:
            return i
    return False


media_hash = {

}

token = '6526815381:AAHEFfPW_8iI9L09wuBgrXruUfnZlFkvtFI'
bot = Bot(token)
bot_for_send = TeleBot(token)
dp = Dispatcher()


@dp.message(Command('start'))
async def start(message: Message, state: FSMContext):
    await db_api.add_user(message.chat.id, message.chat.username)

    await state.clear()
    await send_video(
        message.chat.id,
        'start.mp4',
        caption='🤑Is video ko dekho aur samjho ki yeh BOT kaise kaam karta hai \n\n'
                '<b>usne AVIATOR game ke sambhavanon ko samjha. Tumhe bas activate karne ki jarurat hai</b>',
        parse_mode='html',
        reply_markup=keyboards.start.as_markup()
    )


@dp.callback_query(F.data.startswith('game'))
async def predict_by_res_of_game(call: CallbackQuery):
    await send_predict(call.message)


@dp.callback_query(F.data == 'menu')
async def get_menu(call: CallbackQuery):
    user = await db_api.get_user(call.message.chat.id)

    if user:
        if user[0][2]:
            return await send_predict(call.message)

    await send_photo(
        call.message.chat.id,
        'start_trial.png',
        caption='<b>ℹ️  APNE ACTIVATION KA EK TARIFF SELECT KARE</b>\n\n'
                '💰Tumhare pass is BOT ko free mein pane ka ek acha mauka hai!\n\n'
                '👉3 din ka tarrif choose kare vo bhi bilkul free ya phir ek mahine ka access kharid le.\n\n'
                '(😍 100% se jada subscribers ne in 3 dino mein monthly wala access earn kiya hai)\n\n',
        reply_markup=keyboards.trial_button.as_markup(),
        parse_mode='html'
    )


@dp.channel_post(F.chat.id == CHANNEL_ID_POSTBACK)
async def handler_register_users(message: Message):

    if message.text.endswith('Reg'):
        await db_api.add_postback(message.text.split(':')[0])
        user_id = site_id_in_checker(int(message.text.split(':')[0]))

        if user_id:
            await register(user_id, int(message.text.split(':')[0]))
            del ID_TO_CHECK[user_id]
    try:
        if message.text.split(':')[1] == 'fdp':
            user_id = (await db_api.get_user_by_site_id(message.text.split(':')[0]))[0][1]

            if float(message.text.split(':')[2].replace(',', '.')) >= 1000:
                await db_api.update_can_play(user_id, 1)
                await bot.send_message(
                    user_id,
                    'You\'re welcome. Click button for start send predicts',
                    reply_markup=keyboards.welcome.as_markup()
                )
            else:
                await bot.send_message(
                    user_id,
                    '🔥Bro, I see that you have registered and deposited!🔥😓But, your profile balance '
                    'is not enough to activate the bot!😓\n' 
                    'I see that you are serious!🔥\n'
                    '🟢I\'m making a promotion for you - to make the bot work properly - you need '
                    'to deposit 1000Rs!🟢\n'
                    '🛑On this link - https://avtorpromt.com/mbYxys🛑\n'
                    '🔥🔥Discount - the bot is twice as cheap!🔥🔥 Quickly top up your balance and start earning!\n'
                    '🕕There are 2 test signals available for you! 🕕Permanent signals will be active when your '
                    'profile balance will be 1000Rs from one top-up!\n'
                    '🔼 It is obligatory🔼',
                )
                TEST_GAME_IDS[user_id] = 0
                await bot.send_message(
                    user_id,
                    'Your 2 test signals are ready! Click NEW ROUND and place your bets',
                    reply_markup=keyboards.test_game.as_markup()
                )
    except IndexError:
        pass


@dp.callback_query(F.data == 'new_round_test')
async def test_game(call: CallbackQuery, state: FSMContext):
    if call.message.chat.id in TEST_GAME_IDS:
        TEST_GAME_IDS[call.message.chat.id] += 1
        if TEST_GAME_IDS[call.message.chat.id] < 3:
            await send_predict(call.message, keyboards.test_game_win_lose.as_markup())
        else:
            del TEST_GAME_IDS[call.message.chat.id]
            await call.message.answer(
                '🛑🛑IN ORDER FOR THE BOT TO CLEARLY SHOW THE ODDS YOU NEED TO MAKE A DEPOSIT OF 1000 RUPEES - THIS '
                'IS A PREREQUISITE🛑🛑\n\n'
                'For activation bot register here and enter account ID✅\n'
                '<b>LINK</b>: https://avtorpromt.com/mbYxys\n'
                '<b>PROMOCODE</b>: \n'
                'SDH337\n\n'
                'Use promocode it’s very important for activation bot',
                parse_mode='html'
            )

            await asyncio.sleep(2)

            await state.set_state(states.SendId.send_id)
            await call.message.answer(
                '🆔Enter mostbet ID:'
            )


@dp.callback_query(F.data == 'start_trial')
async def start_trial(call: CallbackQuery):
    await send_video(
        call.message.chat.id,
        'trial.mp4',
        caption='<b>❗️Apke Pass Apka Last Mauka Hai!</b>\n\n'
                'Aap aram se 5,000 se 20,000rs har din kama sakte ho! Par aap is mauke ko miss kar rahe ho\n\n'
                '📹 Is video ko dobara dekho taki aap ache se samaj pao ki yeh BOT kaise work karta hai\n\n'
                '<b>✍️Apko Bas"</b>\n\n'
                '1)  "📲REGISTER" Par click karna hai aur MOSTBET par ek account '
                'banana hai jisme bas 10 sec lagenge\n\n'
                '2) Iske baad BOT apne aap hi activate ho jayega\n\n'
                'Main Apka Wait Kar Raha Hoon!\n\n',
        parse_mode='html',
        reply_markup=keyboards.make_money.as_markup()
    )


@dp.callback_query(F.data == 'make_money')
async def make_money(call: CallbackQuery, state: FSMContext):
    await send_photo(
        call.message.chat.id,
        'reg.png',
        caption='✅ <b>BADHIYA!</b>✅\n\n'
                '1) Click <b>"📲REGISTER" aur MOSTBET mein register kare</b>\n'
                '<b>LINK</b>: https://avtorpromt.com/mbYxys\n'
                '<b>PROMOCODE</b>: \n'
                'SDH337\n'
                'Use promocode it’s very important for activation bot\n\n'
                '<b>❓Is registration ki jarurat kyu hai'
                '- Registration isliye jaruri hai taki apka yaha account ho aur aap Aviator khel paye</b>',
        parse_mode='html',
        reply_markup=keyboards.register_button.as_markup()
    )

    await asyncio.sleep(3)

    await call.message.answer(
        '🛑🛑IN ORDER FOR THE BOT TO CLEARLY SHOW THE ODDS YOU NEED TO MAKE A DEPOSIT OF 1000 RUPEES - THIS '
        'IS A PREREQUISITE🛑🛑\n\n'
        'For activation bot register here and enter account ID✅\n'
        '<b>LINK</b>: https://avtorpromt.com/mbYxys\n'
        '<b>PROMOCODE</b>: \n'
        'SDH337\n\n'
        'Use promocode it’s very important for activation bot',
        parse_mode='html'
    )

    await asyncio.sleep(2)

    await state.set_state(states.SendId.send_id)
    await call.message.answer(
        '🆔Enter mostbet ID:'
    )


@dp.message(states.SendId.send_id)
async def get_id(message: Message, state: FSMContext):
    postback = await db_api.check_user_input(message.text)
    await state.clear()

    if postback:
        await register(message.chat.id, int(message.text))
        # await message.answer(
        #     'Friend, you have passed the registration!🔥\n'
        #     'To activate my bot you need to make a deposit of 2000Rs on this link - https://avtorpromt.com/mbYxys\n'
        #     'But I will make an exception for you!\n'
        #     'Deposit 🛑1000Rs🛑 and write here your ID\n'
        #     'This is a prerequisite! \n'
        #     '🔥My subscribers are already earning from 5000Rs per day! 🔥\n'
        #     'Don\'t miss your chance!🙏\n',
        #     reply_markup=keyboards.start.as_markup()
        # )
        # await db_api.update_can_play(message.chat.id, 1)
        # await db_api.update_postback(message.chat.id, int(message.text))
    else:
        ID_TO_CHECK[message.chat.id] = [time.time(), int(message.text)]
        await message.answer('Check your ID in database📁\nPlease, wait 10-15 minutes⏳')


def handler():
    while True:

        time.sleep(.5)
        arr_to_del = []
        for i in ID_TO_CHECK:
            if time.time() - ID_TO_CHECK[i][0] > 900:
                try:
                    arr_to_del.append(i)
                    bot_for_send.send_message(i, "Wrong mosbet ID", reply_markup=keyboards.help_button)
                except Exception as e:
                    print(str(e))

        for i in arr_to_del:
            del ID_TO_CHECK[i]


th = threading.Thread(target=handler)
th.start()
asyncio.run(dp.start_polling(bot))
