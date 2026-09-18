import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from __init__ import VERSION
from ..emojis import tg_emoji, p_btn
from .. import callback_datas as calls


def menu_text():
    return (
        f"<b>{tg_emoji('home', '🏠')} Playerok Universal</b> v{VERSION}\n"
        f"Ваш бот-помощник для Playerok"
    )


def menu_kb():
    rows = [
        [InlineKeyboardButton(text="━━━  НАСТРОЙКИ  ━━━", callback_data="null_answer")],
        [
            p_btn("Авторизация", "lock_closed", callback_data=calls.MenuNavigation(to="auth").pack()),
            p_btn("Соединение", "link", callback_data=calls.MenuNavigation(to="conn").pack()),
        ],
        [
            p_btn("Сообщения", "write", callback_data=calls.MessagesPagination(page=0).pack()),
            p_btn("Команды", "code", callback_data=calls.CustomCommandsPagination(page=0).pack()),
        ],
        [
            p_btn("Авто-выдача", "send_up", callback_data=calls.AutoDeliveriesPagination(page=0).pack()),
            p_btn("Авто-поднятие", "growth", callback_data=calls.MenuNavigation(to="bump").pack()),
        ],
        [
            p_btn("Восстановление", "refresh", callback_data=calls.MenuNavigation(to="restore").pack()),
            p_btn("Подтверждение", "check", callback_data=calls.MenuNavigation(to="complete").pack()),
        ],
        [
            p_btn("Авто-вывод", "wallet", callback_data=calls.MenuNavigation(to="withdrawal").pack()),
            p_btn("Быстрые ответы", "horn", callback_data=calls.FastRepliesPagination(page=0).pack()),
        ],
        [
            p_btn("Уведомления", "bell", callback_data=calls.MenuNavigation(to="notifications").pack()),
            p_btn("Прочее", "settings", callback_data=calls.MenuNavigation(to="other").pack()),
        ],
        [InlineKeyboardButton(text="━━━  УПРАВЛЕНИЕ  ━━━", callback_data="null_answer")],
        [
            p_btn("Профиль", "profile", callback_data=calls.MenuNavigation(to="profile").pack()),
            p_btn("Статистика", "stats", callback_data=calls.StatsNavigation(to="day").pack()),
        ],
        [
            p_btn("Чаты", "write", callback_data=calls.ChatsPagination(page=0).pack()),
            p_btn("Сделки", "file", callback_data=calls.DealsPagination(page=0).pack()),
        ],
        [
            p_btn("Товары", "box", callback_data=calls.ItemsPagination(page=0).pack()),
            p_btn("Транзакции", "money", callback_data=calls.TransactionsPagination(page=0).pack()),
        ],
        [p_btn("Отзывы", "smile", callback_data=calls.ReviewsPagination(page=0).pack())],
        [InlineKeyboardButton(text="━━━  СИСТЕМА  ━━━", callback_data="null_answer")],
        [
            p_btn("Обновления", "refresh", callback_data=calls.MenuNavigation(to="updates").pack()),
            p_btn("Логи", "file", callback_data=calls.MenuNavigation(to="logs").pack()),
        ],
        [
            p_btn("Плагины", "plugins", callback_data=calls.ModulesPagination(page=0).pack()),
            p_btn("Авторизации", "users", callback_data=calls.SignedUsersPagination(page=0).pack()),
        ],
        [
            p_btn("Конфиги", "file", callback_data=calls.MenuNavigation(to="configs").pack()),
            p_btn("Загрузить плагин", "send_up", callback_data="send_module_file"),
        ]
    ]
    
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb