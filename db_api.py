import asyncio
import aiosqlite
from typing import Union
import os

connect: Union[None | aiosqlite.Connection] = None
cursor: Union[None | aiosqlite.Cursor] = None


async def connect_to_database():
    global connect, cursor
    connect = await aiosqlite.connect(os.path.join(os.path.dirname(__file__), 'db.sqlite'))
    cursor = await connect.cursor()


async def add_user(user_id, username):
    try:
        await cursor.execute('INSERT INTO USERS VALUES(?, ?, ?)', (user_id, username, 0))
        await connect.commit()
    except aiosqlite.IntegrityError:
        pass


async def update_can_play(user_id, value):
    await cursor.execute('UPDATE users SET can_play = ? where user_id = ?', (value, user_id))
    await connect.commit()


async def update_postback(user_id, site_id):
    await cursor.execute('UPDATE POSTBACKS SET tg_id = ? where id = ?', (user_id, site_id))
    await connect.commit()


async def get_user(user_id):
    return await (await cursor.execute('SELECT * FROM USERS WHERE USER_ID = ?', (user_id, ))).fetchall()


async def add_postback(site_id):
    await cursor.execute('INSERT INTO POSTBACKS VALUES(?, ?)', (site_id, 0))
    await connect.commit()


async def check_user_input(site_id):
    return await (await cursor.execute('SELECT * FROM POSTBACKS WHERE id = ?', (site_id, ))).fetchall()


async def get_postback_by_user_id(user_id):
    return await (await cursor.execute('SELECT * FROM POSTBACKS where tg_id = ?', (user_id, ))).fetchall()


async def get_user_by_site_id(site_id):
    return await (await cursor.execute('SELECT * FROM POSTBACKS where id = ?', (site_id,))).fetchall()

loop = asyncio.get_event_loop()
waits = asyncio.wait([loop.create_task(connect_to_database())])
loop.run_until_complete(waits)
