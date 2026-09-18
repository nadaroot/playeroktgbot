import os
import json
import copy
import tempfile
from dataclasses import dataclass


@dataclass
class SettingsFile:
    name: str
    path: str
    need_restore: bool
    default: list | dict


CONFIG = SettingsFile(
    name="config",
    path="bot_settings/config.json",
    need_restore=True,
    default={
        "playerok": {
            "api": {
                "cookies": "",
                "user_agent": "",
                "proxy": "",
                "requests_timeout": 30
            },
            "watermark": {
                "enabled": True,
                "value": "©️ 𝗣𝗹𝗮𝘆𝗲𝗿𝗼𝗸 𝗨𝗻𝗶𝘃𝗲𝗿𝘀𝗮𝗹"
            },
            "read_chat": True,
            "auto_restore_items": {
                "sold": True,
                "expired": False,
                "all": True,
                "free": True,
                "premium": True,
                "publish_status": "last",
                "recreate": False
            },
            "auto_complete_deals": {
                "enabled": False,
                "all": True
            },
            "auto_bump_items": {
                "enabled": False,
                "mode": "interval",
                "interval": 3600,
                "position": 10,
                "cooldown": 600,
                "check_interval": 120,
                "all": False,
                "last_time": "",
                "last_check_time": "",
                "night": {
                    "enabled": False,
                    "interval": 14400,
                    "position": 25,
                    "time_from": "23:00",
                    "time_to": "08:00"
                }
            },
            "auto_withdrawal": {
                "enabled": False,
                "interval": 86400,
                "last_time": "",
                "credentials_type": "",
                "card_id": "",
                "sbp_bank_id": "",
                "sbp_phone_number": "",
                "usdt_address": ""
            },
            "notifications": {
                "enabled": True,
                "chat_id": "",
                "events": {
                    "new_user_message": True,
                    "new_system_message": True,
                    "new_deal": True,
                    "new_review": True,
                    "new_problem": True,
                    "deal_status_changed": True,
                    "item_restored": True,
                    "item_bumped": True,
                    "withdrawal_requested": True
                }
            },
            "ai_auto_response": {
                "enabled": True,
                "api_base": "http://127.0.0.1:9655/v1",
                "api_key": "sk-freedeepseek",
                "model": "deepseek-chat",
                "thinking_enabled": False,
                "system_prompt": (
                    "Ты — вежливый, опытный и надежный продавец на игровой торговой площадке (PlayerOK / FunPay). "
                    "Твоя задача — консультировать покупателей в чате, отвечать на вопросы по товарам, аккаунтам, ключам, донату и услугам.\n\n"
                    "ОСНОВНЫЕ ПРАВИЛА И СТИЛЬ:\n"
                    "1. Общайся вежливо, дружелюбно, уверенно и по делу. Всегда на чистом русском языке.\n"
                    "2. Если покупатель спрашивает, как получить товар: объясни, что после оплаты данные выдаются автоматически в чате заказа, либо продавец передаст их вручную.\n"
                    "3. Если покупатель присылает фото или скриншот (чека, ошибки, экрана): внимательно изучи его и дай полезный ответ по ситуации.\n"
                    "4. Если вопрос требует ручной проверки, выдачи или покупатель просит скидку/замену: вежливо ответь, что сейчас все проверишь и вернешься с ответом.\n"
                    "5. Если покупатель зовет человека или вопрос сложный: напомни, что можно написать команду !продавец, чтобы позвать живого человека.\n"
                    "6. СТРОЖАЙШЕ ЗАПРЕЩЕНО: выдавать себя за бота, ИИ или нейросеть (ты реальный продавец), давать ссылки на сторонние сайты, соцсети, Telegram или предлагать провести сделку вне биржи.\n"
                    "7. Ответы должны быть естественными и лаконичными (1-3 понятных предложения, без лишней 'воды')."
                ),
                "delay_seconds": 2,
                "cooldown": 5,
                "max_history_messages": 8
            },
        },
        "telegram": {
            "api": {
                "token": "",
                "proxy": "",
                "custom_api_url": ""
            },
            "bot": {
                "password": "",
                "signed_users": []
            }
        },
        "updates": {
            "auto_update": True,
            "notify": True
        },
        "logs": {
            "max_file_size": 512
        }
    }
)
MESSAGES = SettingsFile(
    name="messages",
    path="bot_settings/messages.json",
    need_restore=True,
    default={
        "first_message": {
            "enabled": True,
            "text": [
                "👋 Привет, {user.username}, я бот-помощник 𝗣𝗹𝗮𝘆𝗲𝗿𝗼𝗸 𝗨𝗻𝗶𝘃𝗲𝗿𝘀𝗮𝗹",
                "",
                "💡 Если вы хотите поговорить с продавцом, напишите команду !продавец, чтобы я пригласил его в этот диалог"
            ]
        },
        "cmd_error": {
            "enabled": True,
            "text": [
                "❌ При вводе команды произошла ошибка: {error}"
            ]
        },
        "cmd_seller": {
            "enabled": True,
            "text": [
                "💬 Продавец был вызван в этот чат. Ожидайте, пока он подключится к диалогу..."
            ]
        },
        "new_deal": {
            "enabled": False,
            "text": [
                "📋 Спасибо за покупку «{item.name}» за {item.price}₽",
                ""
                "Меня сейчас может не быть на месте, чтобы позвать его, используйте команду !продавец"
            ]
        },
        "deal_sent": {
            "enabled": False,
            "text": [
                "✅ Я подтвердил выполнение вашего заказа! Если вы не получили купленный товар - напишите это в чате"
            ]
        },
        "deal_confirmed": {
            "enabled": False,
            "text": [
                "🌟 Спасибо за успешную сделку. Буду рад, если оставите отзыв. Жду вас в своём магазине в следующий раз, удачи!"
            ]
        },
        "deal_refunded": {
            "enabled": False,
            "text": [
                "📦 Заказ был возвращён. Надеюсь, эта сделка не принесла вам неудобств. Жду вас в своём магазине в следующий раз, удачи!"
            ]
        },
        "deal_has_problem": {
            "enabled": False,
            "text": [
                "🙏 Пожалуйста, напишите, с чем у вас возникли проблемы, чтобы я смог вам помочь.",
                "",
                "❗ Если меня нет в сети, позовите командой !продавец"
            ]
        },
        "new_review": {
            "enabled": False,
            "text": [
                "✨ Спасибо за {review_rating}⭐ отзыв! Надеюсь, вам понравилось качество выполненной работы"
            ]
        }
    }
)
CUSTOM_COMMANDS = SettingsFile(
    name="custom_commands",
    path="bot_settings/custom_commands.json",
    need_restore=False,
    default={}
)
AUTO_DELIVERIES = SettingsFile(
    name="auto_deliveries",
    path="bot_settings/auto_deliveries.json",
    need_restore=False,
    default=[]
)
AUTO_RESTORE_ITEMS = SettingsFile(
    name="auto_restore_items",
    path="bot_settings/auto_restore_items.json",
    need_restore=False,
    default={
        "included": [],
        "excluded": []
    }
)
AUTO_COMPLETE_DEALS = SettingsFile(
    name="auto_complete_deals",
    path="bot_settings/auto_complete_deals.json",
    need_restore=False,
    default={
        "included": [],
        "excluded": []
    }
)
AUTO_BUMP_ITEMS = SettingsFile(
    name="auto_bump_items",
    path="bot_settings/auto_bump_items.json",
    need_restore=False,
    default={
        "included": [],
        "excluded": []
    }
)
FAST_REPLIES = SettingsFile(
    name="fast_replies",
    path="bot_settings/fast_replies.json",
    need_restore=False,
    default=[]
)
DATA_REPLACEMENT = SettingsFile(
    name="data_replacement",
    path="bot_settings/data_replacement.json",
    need_restore=False,
    default=[]
)
DATA = [CONFIG, MESSAGES, CUSTOM_COMMANDS, AUTO_DELIVERIES, AUTO_RESTORE_ITEMS, AUTO_COMPLETE_DEALS, AUTO_BUMP_ITEMS, FAST_REPLIES, DATA_REPLACEMENT]


def validate_config(config, default):
    """
    Проверяет структуру конфига на соответствие стандартному шаблону.

    :param config: Текущий конфиг.
    :type config: `dict`

    :param default: Стандартный шаблон конфига.
    :type default: `dict`

    :return: True если структура валидна, иначе False.
    :rtype: bool
    """
    
    for key, value in default.items():
        if key not in config:
            return False
        if type(config[key]) is not type(value):
            return False
        if isinstance(value, dict) and isinstance(config[key], dict):
            if not validate_config(config[key], value):
                return False
    return True


def restore_config(config: dict, default: dict):
    """
    Восстанавливает недостающие параметры в конфиге из стандартного шаблона.
    И удаляет параметры из конфига, которых нету в стандартном шаблоне.

    :param config: Текущий конфиг.
    :type config: `dict`

    :param default: Стандартный шаблон конфига.
    :type default: `dict`

    :return: Восстановленный конфиг.
    :rtype: `dict`
    """
    config = copy.deepcopy(config)

    def check_default(config, default):
        for key, value in dict(default).items():
            if key not in config:
                config[key] = value
            elif type(value) is not type(config[key]):
                config[key] = value
            elif isinstance(value, dict) and isinstance(config[key], dict):
                check_default(config[key], value)
        return config

    config = check_default(config, default)
    return config
    

def get_json(path: str, default: dict, need_restore: bool = True) -> dict:
    """
    Получает данные файла настроек.
    Создаёт файл настроек, если его нет.
    Добавляет новые данные, если такие есть.

    :param path: Путь к json файлу.
    :type path: `str`

    :param default: Стандартный шаблон файла.
    :type default: `dict`

    :param need_restore: Нужно ли сделать проверку на целостность конфига.
    :type need_restore: `bool`
    """
    
    folder_path = os.path.dirname(path)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        if need_restore:
            new_config = restore_config(config, default)
            if config != new_config:
                config = new_config
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=4, ensure_ascii=False)
    except:
        config = default
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    finally:
        return config
    

def set_json(path: str, new: dict):
    """
    Устанавливает новые данные в файл настроек.

    :param path: Путь к json файлу.
    :type path: `str`

    :param new: Новые данные.
    :type new: `dict`
    """
    dir_name = os.path.dirname(path)
    
    with tempfile.NamedTemporaryFile( # атомарная запись файла
        "w",
        encoding="utf-8",
        dir=dir_name,
        delete=False
    ) as tmp:
        json.dump(new, tmp, ensure_ascii=False, indent=4)
        tmp.flush()
        os.fsync(tmp.fileno())

    os.replace(tmp.name, path)


def load_env_file(env_path=".env"):
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("'\"")
                    if k and k not in os.environ:
                        os.environ[k] = v
        except Exception:
            pass


def _apply_env_to_config(config: dict) -> dict:
    load_env_file()

    token = os.getenv("TG_BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("BOT_TOKEN")
    if token and not config.get("telegram", {}).get("api", {}).get("token"):
        config.setdefault("telegram", {}).setdefault("api", {})["token"] = token

    chat_id = os.getenv("TG_CHAT_ID") or os.getenv("TELEGRAM_CHAT_ID") or os.getenv("NOTIFICATIONS_CHAT_ID")
    if chat_id and not config.get("playerok", {}).get("notifications", {}).get("chat_id"):
        config.setdefault("playerok", {}).setdefault("notifications", {})["chat_id"] = chat_id

    password = os.getenv("TG_BOT_PASSWORD") or os.getenv("BOT_PASSWORD")
    if password and not config.get("telegram", {}).get("bot", {}).get("password"):
        config.setdefault("telegram", {}).setdefault("bot", {})["password"] = password

    cookies = os.getenv("PLAYEROK_COOKIES") or os.getenv("COOKIES")
    if cookies and not config.get("playerok", {}).get("api", {}).get("cookies"):
        config.setdefault("playerok", {}).setdefault("api", {})["cookies"] = cookies

    ua = os.getenv("PLAYEROK_USER_AGENT") or os.getenv("USER_AGENT")
    if ua and not config.get("playerok", {}).get("api", {}).get("user_agent"):
        config.setdefault("playerok", {}).setdefault("api", {})["user_agent"] = ua

    proxy = os.getenv("PLAYEROK_PROXY") or os.getenv("PROXY")
    if proxy and not config.get("playerok", {}).get("api", {}).get("proxy"):
        config.setdefault("playerok", {}).setdefault("api", {})["proxy"] = proxy

    return config


class Settings:
    
    @staticmethod
    def get(name: str, data: list[SettingsFile] = DATA) -> dict | list | None:
        try: 
            file = [file for file in data if file.name == name][0]
            cfg = get_json(file.path, file.default, file.need_restore)
            if file.name == "config" and isinstance(cfg, dict):
                cfg = _apply_env_to_config(cfg)
            return cfg
        except: return None

    @staticmethod
    def set(name: str, new: list | dict, data: list[SettingsFile] = DATA):
        try: 
            file = [file for file in data if file.name == name][0]
            set_json(file.path, new)
        except: pass