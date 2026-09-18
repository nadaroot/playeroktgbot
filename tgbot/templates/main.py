import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils import github_str_to_dt
from ..emojis import tg_emoji, p_btn
from .. import callback_datas as calls


def error_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>{tg_emoji('cross', '❌')} Ошибка</b>
        \n<blockquote>{placeholder}</blockquote>
    """)
    return txt


def back_kb(cb: str):
    rows = [[p_btn("Назад", "download", callback_data=cb)]]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def confirm_kb(confirm_cb: str, cancel_cb: str):
    rows = [[
        p_btn("Подтвердить", "check", callback_data=confirm_cb),
        p_btn("Отменить", "cross", callback_data=cancel_cb)
    ]]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def destroy_kb():
    rows = [[p_btn("Закрыть", "cross", callback_data="destroy")]]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def new_release_text(release):
    tag = release["tag_name"]
    desc = release.get("body", "Без описания")
    url = release["html_url"]
    published_at = github_str_to_dt(
        release["published_at"]
    ).strftime("%d.%m.%Y %H:%M:%S")

    txt = textwrap.dedent(f"""
        <b>{tg_emoji('party', '🚀')} Доступна новая версия — <a href="{url}">{tag}</a></b>
        \n<b>{tg_emoji('gift', '💎')} Изменения:</b>\n<blockquote>{desc}</blockquote>
        \n<b>{tg_emoji('calendar', '📅')} Дата выхода:</b> {published_at}
    """)
    return txt


def new_release_kb():
    rows = [
        [p_btn("Установить", "download", callback_data="install_update")],
        [p_btn("Закрыть", "cross", callback_data="destroy")]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def new_sign_text(user):
    username = "@" + user.username.replace("@", "")
    txt = textwrap.dedent(f"""
        <b>{tg_emoji('lock_closed', '🔑')} Новая авторизация</b>

        Пользователь <b>{username}</b> только что авторизовался в боте
        
        {tg_emoji('horn', '❗')} <b>Если это были не Вы</b>, как можно скорее перейдите в раздел <b>«Авторизации»</b> в меню бота и удалите этого пользователя, а после смените пароль от Telegram бота
    """)
    return txt


def do_action_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>{tg_emoji('plugins', '🧩')} Действие</b>
        \n{placeholder}
    """)
    return txt


def log_text(title: str, text=""):
    txt = textwrap.dedent(f"""
        <b>{title}</b>
        \n{text}
    """)
    return txt


def log_new_mess_kb(chat_id: str):
    rows = [
        [
            p_btn("Ответить", "pencil", callback_data=calls.RememberChatId(id=chat_id, do="send_mess").pack()),
            p_btn("Быстрый ответ", "horn", callback_data=calls.RememberChatId(id=chat_id, do="send_fast_reply").pack())
        ],
        [p_btn("Диалог", "write", callback_data=calls.ChatPage(id=chat_id).pack())],
        [p_btn("Закрыть", "cross", callback_data="destroy")]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def log_new_deal_kb(chat_id: str, deal_id: str):
    rows = [
        [
            p_btn("Ответить", "pencil", callback_data=calls.RememberChatId(id=chat_id, do="send_mess").pack()),
            p_btn("Быстрый ответ", "horn", callback_data=calls.RememberChatId(id=chat_id, do="send_fast_reply").pack())
        ],
        [
            p_btn("Выполнил", "check", callback_data=calls.RememberDealId(de_id=deal_id, do="complete").pack()),
            p_btn("Возврат", "box", callback_data=calls.RememberDealId(de_id=deal_id, do="refund").pack())
        ],
        [
            p_btn("Диалог", "write", callback_data=calls.ChatPage(id=chat_id).pack()),
            p_btn("Сделка", "file", callback_data=calls.DealPage(id=deal_id).pack())
        ],
        [p_btn("Закрыть", "cross", callback_data="destroy")]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def log_new_problem_kb(chat_id: str, deal_id: str):
    rows = [
        [
            p_btn("Ответить", "pencil", callback_data=calls.RememberChatId(id=chat_id, do="send_mess").pack()),
            p_btn("Быстрый ответ", "horn", callback_data=calls.RememberChatId(id=chat_id, do="send_fast_reply").pack())
        ],
        [
            p_btn("Диалог", "write", callback_data=calls.ChatPage(id=chat_id).pack()),
            p_btn("Сделка", "file", callback_data=calls.DealPage(id=deal_id).pack())
        ],
        [p_btn("Закрыть", "cross", callback_data="destroy")]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def log_item_kb(item_id: str):
    rows = [
        [p_btn("Товар", "box", callback_data=calls.ItemPage(id=item_id).pack())],
        [p_btn("Закрыть", "cross", callback_data="destroy")]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def log_deal_kb(deal_id: str):
    rows = [
        [p_btn("Сделка", "file", callback_data=calls.DealPage(id=deal_id).pack())],
        [p_btn("Закрыть", "cross", callback_data="destroy")]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def log_transaction_kb(deal_id: str):
    rows = [
        [p_btn("Транзакция", "money", callback_data=calls.TransactionPage(id=deal_id).pack())],
        [p_btn("Закрыть", "cross", callback_data="destroy")]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def sign_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>{tg_emoji('lock_closed', '🔐')} Авторизация</b>
        \n{placeholder}
    """)
    return txt


def call_seller_text(username: str, chat_id: str):
    txt = textwrap.dedent(f"""
        {tg_emoji('horn', '❗')} <b>{username}</b> вызывает вас в <a href="https://playerok.com/chats/{chat_id}">чат</a>
    """)
    return txt


def call_seller_kb(chat_id: str):
    rows = [
        [p_btn("Перейти в диалог", "write", callback_data=calls.ChatPage(id=chat_id).pack())],
        [p_btn("Закрыть", "cross", callback_data="destroy")]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb