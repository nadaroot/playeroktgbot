import os
import asyncio
from tempfile import NamedTemporaryFile
from logging import getLogger

from aiogram import Router, types, F
from data import Data
from settings import Settings as sett


logger = getLogger("universal.telegram.topics")
router = Router()


@router.message(F.chat.type.in_({"supergroup", "group"}), F.message_thread_id, F.from_user.is_bot == False)
async def handler_topic_reply(message: types.Message):
    topic_chats = Data.get("topic_chats") or {"chat_to_topic": {}, "topic_to_chat": {}}
    topic_to_chat = topic_chats.get("topic_to_chat", {})

    thread_id_str = str(message.message_thread_id)
    chat_id = topic_to_chat.get(thread_id_str)
    if not chat_id:
        return

    from plbot.playerokbot import get_playerok_bot
    bot_inst = get_playerok_bot()
    if not bot_inst or not bot_inst.account:
        await message.reply("❌ Аккаунт Playerok не подключён!")
        return

    acc = bot_inst.account
    text = None
    photo_paths = []

    try:
        if message.text:
            text = message.text

        if message.photo:
            photo = message.photo[-1]
            with NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                await message.bot.download(photo, destination=tmp.name)
                photo_paths.append(tmp.name)
            if message.caption:
                text = message.caption

        if not text and not photo_paths:
            return

        acc.send_message(
            chat_id=chat_id,
            text=text,
            images=photo_paths
        )

        try:
            await message.react([types.ReactionTypeEmoji(emoji="👍")])
        except Exception:
            pass

    except Exception as e:
        logger.error(f"Ошибка пересылки сообщения из топика {message.message_thread_id} в чат {chat_id}: {e}")
        await message.reply(f"❌ <b>Ошибка отправки на Playerok:</b> <blockquote>{e}</blockquote>", parse_mode="HTML")
    finally:
        for path in photo_paths:
            try:
                os.remove(path)
            except Exception:
                pass
