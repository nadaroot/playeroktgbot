"""
Модуль ИИ Авто-ответчика для торговой площадки (PlayerOK / FunPay).
Интегрирован с локальным FreeDeepseekAPI (OpenAI-compatible) с поддержкой Vision и памяти диалогов.
"""

import time
import asyncio
import logging
from collections import deque
import aiohttp

logger = logging.getLogger("universal.ai_responder")


class AIAutoResponder:
    """
    Класс для автоматических ответов покупателям в чатах маркетплейса от лица продавца.
    """

    def __init__(self, config_getter=None):
        self.config_getter = config_getter
        # История диалогов по chat_id: chat_id -> deque(maxlen=N)
        self._dialog_history: dict[str, deque] = {}
        # Время последнего ответа в чат: chat_id -> timestamp
        self._last_reply_times: dict[str, float] = {}

    def _get_config(self) -> dict:
        if callable(self.config_getter):
            cfg = self.config_getter()
            if isinstance(cfg, dict):
                return cfg.get("playerok", {}).get("ai_auto_response", {})
        return {}

    def is_enabled(self) -> bool:
        cfg = self._get_config()
        return bool(cfg.get("enabled", False))

    def _get_history(self, chat_id: str, maxlen: int = 8) -> deque:
        if chat_id not in self._dialog_history:
            self._dialog_history[chat_id] = deque(maxlen=maxlen)
        return self._dialog_history[chat_id]

    def reset_chat_history(self, chat_id: str | None = None):
        if chat_id:
            self._dialog_history.pop(chat_id, None)
            self._last_reply_times.pop(chat_id, None)
        else:
            self._dialog_history.clear()
            self._last_reply_times.clear()

    async def generate_reply(
        self,
        chat_id: str,
        user_text: str | None = None,
        username: str = "Покупатель",
        seller_name: str = "Продавец",
        images: list[str] | None = None
    ) -> str | None:
        """
        Генерирует ответ покупателю с использованием DeepSeek API.
        """
        cfg = self._get_config()
        if not cfg.get("enabled", False):
            return None

        now = time.time()
        cooldown = float(cfg.get("cooldown", 5))
        last_time = self._last_reply_times.get(chat_id, 0)
        if (now - last_time) < cooldown:
            logger.debug(f"[AI] Chat {chat_id} is in cooldown ({(now - last_time):.1f}s < {cooldown}s)")
            return None

        api_base = cfg.get("api_base", "http://127.0.0.1:9655/v1").rstrip("/")
        api_key = cfg.get("api_key", "sk-freedeepseek")
        model = cfg.get("model", "deepseek-chat")
        thinking_enabled = cfg.get("thinking_enabled", False)
        raw_system_prompt = cfg.get("system_prompt", "")
        delay_seconds = float(cfg.get("delay_seconds", 2))
        max_history = int(cfg.get("max_history_messages", 8))

        # Форматирование системного промпта переменными
        system_prompt = raw_system_prompt.replace("{seller_name}", seller_name).replace("{username}", username)

        # Формирование контента пользователя (мультимодальный если есть картинки)
        user_content = []
        clean_text = (user_text or "").strip()
        if clean_text:
            user_content.append({"type": "text", "text": clean_text})

        if images:
            for img_url in images:
                if img_url and isinstance(img_url, str):
                    user_content.append({
                        "type": "image_url",
                        "image_url": {"url": img_url}
                    })

        if not user_content:
            return None

        # Сборка цепочки сообщений
        history = self._get_history(chat_id, maxlen=max_history)
        messages = [{"role": "system", "content": system_prompt}]

        for h_msg in history:
            messages.append(h_msg)

        # Если в контенте только текст, отправляем как простую строку для экономии
        current_msg_content = clean_text if (len(user_content) == 1 and user_content[0].get("type") == "text") else user_content
        messages.append({"role": "user", "content": current_msg_content})

        payload = {
            "model": model,
            "messages": messages,
            "thinking_enabled": thinking_enabled,
            "temperature": 0.7,
            "max_tokens": 400
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "X-Agent-Session": f"market-chat-{chat_id}"
        }

        try:
            timeout = aiohttp.ClientTimeout(total=45)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(f"{api_base}/chat/completions", json=payload, headers=headers) as resp:
                    if resp.status != 200:
                        err_body = await resp.text()
                        logger.warning(f"[AI] DeepSeek API returned HTTP {resp.status}: {err_body[:150]}")
                        return None

                    data = await resp.json()
                    choices = data.get("choices", [])
                    if not choices:
                        return None

                    reply_text = choices[0].get("message", {}).get("content", "")
                    if not reply_text:
                        return None

                    reply_text = reply_text.strip()
                    # Сохраняем в историю диалога
                    history.append({"role": "user", "content": clean_text or "[Изображение]"})
                    history.append({"role": "assistant", "content": reply_text})
                    self._last_reply_times[chat_id] = time.time()

                    # Имитация живого набора текста
                    if delay_seconds > 0:
                        await asyncio.sleep(delay_seconds)

                    logger.info(f"[AI] Generated reply for {username} (chat {chat_id}): {reply_text[:60]}...")
                    return reply_text

        except asyncio.TimeoutError:
            logger.warning(f"[AI] Timeout while contacting DeepSeek API for chat {chat_id}")
            return None
        except Exception as e:
            logger.error(f"[AI] Error generating AI auto-reply for chat {chat_id}: {e}")
            return None
