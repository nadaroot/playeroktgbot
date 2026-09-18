from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext

from settings import Settings as sett
from utils import is_password_valid

from .. import templates as templ
from .. import states
from .. import callback_datas as calls
from ..helpful import throw_float_message


from data import Data

ADMIN_ID = 821315597

router = Router()


@router.message(states.SystemStates.waiting_for_password, F.text)
async def handler_waiting_for_password(message: types.Message, state: FSMContext):
    try: 
        entered_code = message.text.strip()
        codes = Data.get("one_time_codes") or {}
        config = sett.get("config")
        
        is_valid = False
        
        # Проверяем одноразовый код
        if entered_code in codes:
            is_valid = True
            del codes[entered_code]
            Data.set("one_time_codes", codes)
        # Владелец может авторизоваться напрямую
        elif message.from_user.id == ADMIN_ID:
            is_valid = True
        # Резервный пароль из конфига (если задан)
        elif config.get("telegram", {}).get("bot", {}).get("password") and entered_code == config["telegram"]["bot"]["password"]:
            is_valid = True

        if not is_valid:
            raise Exception("❌ Неверный или уже использованный одноразовый код. Запросите код у владельца бота.")

        await state.set_state(None)
        
        if message.from_user.id not in config["telegram"]["bot"]["signed_users"]:
            config["telegram"]["bot"]["signed_users"].append(message.from_user.id)
            sett.set("config", config)

        try:
            await throw_float_message(
                state=state,
                message=message,
                text=templ.menu_text(),
                reply_markup=templ.menu_kb()
            )
        except:
            await message.bot.send_message(
                chat_id=message.from_user.id,
                text=templ.menu_text(),
                reply_markup=templ.menu_kb(),
                parse_mode="HTML"
            )

        # Уведомляем владельца бота о новой успешной авторизации
        if message.from_user.id != ADMIN_ID:
            try:
                u = message.from_user
                username_str = f"@{u.username}" if u.username else "без username"
                await message.bot.send_message(
                    chat_id=ADMIN_ID,
                    text=(
                        f"🔔 <b>Новая авторизация в боте!</b>\n\n"
                        f"👤 Пользователь: <b>{u.full_name}</b> ({username_str})\n"
                        f"🆔 Telegram ID: <code>{u.id}</code>\n"
                        f"🔑 Код доступа: <code>{entered_code}</code>"
                    ),
                    parse_mode="HTML"
                )
            except Exception:
                pass
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.sign_text(e), 
            reply_markup=templ.destroy_kb()
        )


@router.message(states.SystemStates.waiting_for_current_password, F.text)
async def handler_waiting_for_current_password(message: types.Message, state: FSMContext):
    try: 
        await state.set_state(None)
        config = sett.get("config")

        data = await state.get_data()
        last_page = data.get("last_page", 0)
        
        if message.text != config["telegram"]["bot"]["password"]:
            raise Exception("❌ Неверный ключ-пароль")

        await state.set_state(states.SystemStates.waiting_for_new_password)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.signed_users_float_text("🆕 Введите <b>новый ключ-пароль</b> от бота (не менее 6 и не более 64 символов):"),
            reply_markup=templ.back_kb(calls.SignedUsersPagination(page=last_page).pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.signed_users_float_text(e), 
            reply_markup=templ.back_kb(calls.SignedUsersPagination(page=last_page).pack())
        )


@router.message(states.SystemStates.waiting_for_new_password, F.text)
async def handler_waiting_for_new_password(message: types.Message, state: FSMContext):
    try: 
        await state.set_state(None)

        config = sett.get("config")
        old_passwd = config["telegram"]["bot"]["password"]

        data = await state.get_data()
        last_page = data.get("last_page", 0)
        
        if not is_password_valid(message.text):
            raise Exception("❌ Ваш пароль не подходит. Убедитесь, что он соответствует формату и не является лёгким и попробуйте ещё раз")
        
        new_passwd = message.text
        await state.update_data(new_password=new_passwd)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.signed_users_float_text(
                "✔️ Подтвердите <b>смену пароля</b> для бота:"
                f"\n\n・ <b>Старый:</b> {old_passwd}"
                f"\n・ <b>Новый:</b> {new_passwd}"
            ),
            reply_markup=templ.confirm_kb(
                confirm_cb="change_password",
                cancel_cb=calls.SignedUsersPagination(page=last_page).pack()
            )
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.signed_users_float_text(e), 
            reply_markup=templ.back_kb(calls.SignedUsersPagination(page=last_page).pack())
        )