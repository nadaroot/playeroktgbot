from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from packaging.version import Version

from __init__ import VERSION
from settings import Settings as sett
from core.utils import restart

from .. import templates as templ
from ..helpful import throw_float_message, do_auth


import secrets
from datetime import datetime
from data import Data

router = Router()

ADMIN_ID = 821315597


@router.message(Command("code", "cod"))
async def handler_code(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.reply("❌ Команда генерации одноразовых кодов доступна только создателю бота.")

    code = str(secrets.randbelow(900000) + 100000)
    codes = Data.get("one_time_codes") or {}
    codes[code] = {
        "created_at": datetime.now().isoformat(),
        "created_by": message.from_user.id
    }
    Data.set("one_time_codes", codes)

    await message.reply(
        f"🔑 <b>Одноразовый код для входа:</b> <code>{code}</code>\n\n"
        f"<i>Нажмите на код, чтобы скопировать его. Код действует для одной авторизации нового пользователя.</i>",
        parse_mode="HTML"
    )


@router.message(Command("start"))
async def handler_start(message: types.Message, state: FSMContext):
    await state.set_state(None)
    
    config = sett.get("config")
    
    # Владелец всегда авторизован
    if message.from_user.id == ADMIN_ID:
        if ADMIN_ID not in config["telegram"]["bot"]["signed_users"]:
            config["telegram"]["bot"]["signed_users"].append(ADMIN_ID)
            sett.set("config", config)

    if message.from_user.id not in config["telegram"]["bot"]["signed_users"]:
        return await do_auth(message, state)
    
    await throw_float_message(
        state=state,
        message=message,
        text=templ.menu_text(),
        reply_markup=templ.menu_kb()
    )

    from updater import latest_release
    if latest_release and Version(VERSION) < Version(latest_release.get("tag_name", "0.0.0")):
        await throw_float_message(
            state=state,
            message=message,
            text=templ.new_release_text(latest_release),
            reply_markup=templ.new_release_kb(),
            disable_web_page_preview=True,
            send=True
        )


@router.message(Command("restart"))
async def handler_restart(message: types.Message, state: FSMContext):
    await state.set_state(None)
    
    config = sett.get("config")
    if message.from_user.id != ADMIN_ID and message.from_user.id not in config["telegram"]["bot"]["signed_users"]:
        return await do_auth(message, state)
    
    await throw_float_message(
        state=state,
        message=message,
        text="🔄️ <b>Перезагружаю бота</b>, подождите...",
        reply_markup=templ.destroy_kb()
    )
    
    restart(from_tg=True)