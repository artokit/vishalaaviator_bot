from typing import Union
from aiogram import Dispatcher, Bot, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from db_api import get_users


dp: Union[None | Dispatcher] = None
bot: Union[None | Bot] = None
ADMINS = [5833820044, 6076339332]


async def get_ids():
    return [i[0] for i in (await get_users())]


class SenderKeyboards:
    @staticmethod
    def cancel_or_not():
        keyboard = InlineKeyboardBuilder()
        keyboard.row(InlineKeyboardButton(text='Начать рассылку', callback_data='start_send'))
        keyboard.add(InlineKeyboardButton(text='Отмена', callback_data='not_start_send'))
        return keyboard

    @staticmethod
    def stop_urls():
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text='Остановить получение ссылок', callback_data='urls_stop'))
        return keyboard

    @staticmethod
    def without_text():
        keyboard = InlineKeyboardBuilder()
        keyboard.row(InlineKeyboardButton(text='В рассылке не нужен текст', callback_data='without_text'))
        return keyboard

    @staticmethod
    def no_media():
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text='Поставить ссылки', callback_data='set_urls'))
        return keyboard


class SenderStates(StatesGroup):
    send_media = State()
    send_caption = State()
    send_urls = State()
    final = State()


def set_bot(d: Dispatcher, b: Bot):
    global dp, bot
    dp = d
    bot = b


async def builder(data, ids):
    urls_keyboard = None
    caption = data.get('caption')
    if data.get('urls'):
        urls_keyboard = InlineKeyboardBuilder()
        for i in data.get('urls'):
            urls_keyboard.row(InlineKeyboardButton(text=i[0], url=i[1]))
            urls_keyboard = urls_keyboard.as_markup()

    if data.get('media'):
        media = []
        first = True
        if len(data.get('media')) > 1:
            for i in data.get('media'):
                if i[0] == 'photo':
                    media.append(InputMediaPhoto(media=i[1], caption=caption if first else None))
                    # media.attach_photo(i[1], caption if first else None)
                if i[0] == 'video':
                    media.append(InputMediaPhoto(media=i[1], caption=caption if first else None))
                    # media.attach_video(InputFile(i[1]), caption if first else None)
                first = False
            for i in ids:
                try:
                    await bot.send_media_group(i, media=media)
                except Exception as e:
                    print(str(e))

        if len(data.get('media')) == 1:
            d = data.get('media')[0]

            if d[0] == 'photo':
                for i in ids:
                    try:
                        await bot.send_photo(i, d[1], caption=caption, reply_markup=urls_keyboard)
                    except Exception as e:
                        print(str(e))

            if d[0] == 'video':
                for i in ids:
                    try:
                        await bot.send_video(i, d[1], caption=caption, reply_markup=urls_keyboard)
                    except Exception as e:
                        print(str(e))
        return

    else:
        for i in ids:
            try:
                await bot.send_message(i, caption, reply_markup=urls_keyboard)
            except Exception as e:
                print(str(e))


def init_handlers():
    @dp.message(Command('send'))
    async def start_sender(message: Message, state: FSMContext):
        await state.clear()
        await state.set_state(SenderStates.send_caption)

        await message.answer('Отправьте текст для рассылки', reply_markup=SenderKeyboards.without_text().as_markup())

    @dp.message(SenderStates.send_media, F.photo)
    @dp.message(SenderStates.send_media, F.video)
    async def get_media(message: Message, state: FSMContext):
        data = await state.get_data()
        media = data.get('media', [])

        if message.video:
            media.append(['video', message.video.file_id])

        if message.photo:
            media.append(['photo', message.photo[-1].file_id])

        await state.update_data({'media': media})
        await message.answer(
            'Загружено. Если хотите поставить ссылки, то жмите на кнопку.\n'
            'Если хотите загрузить ещё другие фото/видео, то отправляйте их',
            reply_markup=SenderKeyboards.no_media().as_markup()
        )

    @dp.callback_query(F.data == 'not_start_send')
    async def not_start(call: CallbackQuery, state: FSMContext):
        await state.clear()
        await call.message.answer('Действие отменено')

    @dp.callback_query(F.data == 'urls_stop', SenderStates.send_urls)
    async def send_message_for_test(call: CallbackQuery, state: FSMContext):
        await state.set_state(SenderStates.final)
        await call.message.answer('Вот выглядит рассылка сейчас: ')
        await builder(await state.get_data(), [call.message.chat.id, ])
        await call.message.answer('Отправляем?', reply_markup=SenderKeyboards.cancel_or_not().as_markup())

    @dp.callback_query(F.data == 'without_text', SenderStates.send_caption)
    async def without_text(call: CallbackQuery, state: FSMContext):
        await state.set_state(SenderStates.send_media)
        await call.message.answer('Отправьте фотографию или видео')

    @dp.callback_query(F.data == 'start_send', SenderStates.final)
    async def start_send(call: CallbackQuery, state: FSMContext):
        await call.message.answer('Рассылка началась')
        data = await state.get_data()
        await state.clear()
        await builder(data, await get_ids())

    @dp.callback_query(F.data == 'set_urls', SenderStates.send_media)
    async def get_urls(call: CallbackQuery, state: FSMContext):
        await state.set_state(SenderStates.send_urls)
        await call.message.answer(
            'Отправьте ссылки в таком формате:\n'
            'Текст Ссылки\n'
            'Ссылка',
            reply_markup=SenderKeyboards.stop_urls().as_markup()
        )

    @dp.message(SenderStates.send_urls)
    async def get_url(message: Message, state: FSMContext):
        data = await state.get_data()
        urls = data.get('urls', [])
        t = message.text.split('\n')
        urls.append([t[0], t[1]])
        await state.update_data({'urls': urls})
        await message.answer('Заканчиваем или ещё хотите ?', reply_markup=SenderKeyboards.stop_urls().as_markup())

    @dp.message(SenderStates.send_caption)
    async def get_caption(message: Message, state: FSMContext):
        await state.set_data({'caption': message.text})
        await state.set_state(SenderStates.send_media)
        await message.answer('Отправьте фотографию или видео', reply_markup=SenderKeyboards.no_media().as_markup())
