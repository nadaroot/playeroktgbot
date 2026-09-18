#!/usr/bin/env python3
"""
Утилита для быстрой авторизации аккаунта PlayerOK.
Позволяет открыть браузер на ПК, захватить сессию (cookies и user-agent)
и сохранить их в файл playerok_auth.json или bot_settings/config.json.
"""

import os
import sys
import json
import time
import shutil
import platform
import subprocess
import urllib.request
import http.cookiejar

def clear_screen():
    os.system("cls" if platform.system() == "Windows" else "clear")

def print_banner():
    print("=" * 60)
    print("  PlayerOK Bot — Мастер авторизации и получения сессии")
    print("=" * 60)
    print()

def find_browser():
    system = platform.system()
    if system == "Darwin":
        paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
            "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
        ]
    elif system == "Windows":
        paths = [
            os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
            os.path.expandvars(r"%ProgramFiles%\BraveSoftware\Brave-Browser\Application\brave.exe")
        ]
    else:
        paths = [
            shutil.which("google-chrome"),
            shutil.which("google-chrome-stable"),
            shutil.which("chromium"),
            shutil.which("chromium-browser"),
            shutil.which("brave-browser")
        ]

    for p in paths:
        if p and os.path.exists(p):
            return p
    return None

def parse_cookie_string(raw_cookie: str) -> str:
    raw_cookie = raw_cookie.strip()
    if raw_cookie.startswith("Cookie:"):
        raw_cookie = raw_cookie[7:].strip()
    return raw_cookie

def save_auth(cookies: str, user_agent: str, profile_data: dict = None):
    auth_data = {
        "cookies": cookies,
        "user_agent": user_agent,
        "saved_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    if profile_data:
        auth_data["profile"] = profile_data

    # Сохраняем в локальный playerok_auth.json
    with open("playerok_auth.json", "w", encoding="utf-8") as f:
        json.dump(auth_data, f, indent=2, ensure_ascii=False)

    # Если есть папка bot_settings/config.json, обновляем и ее
    config_path = os.path.join("bot_settings", "config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            if "playerok" in cfg and "api" in cfg["playerok"]:
                cfg["playerok"]["api"]["cookies"] = cookies
                cfg["playerok"]["api"]["user_agent"] = user_agent
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(cfg, f, indent=4, ensure_ascii=False)
                print(f"[OK] Конфигурация в {config_path} успешно обновлена!")
        except Exception as e:
            print(f"[WARN] Не удалось обновить {config_path}: {e}")

    print()
    print("=" * 60)
    print("  АВТОРИЗАЦИЯ УСПЕШНО ЗАВЕРШЕНА!")
    print("=" * 60)
    print(f"Данные сохранены в файл: playerok_auth.json")
    print("Теперь вы можете запустить бота через docker-compose up -d или python bot.py.")
    print("=" * 60)

def manual_input():
    print("--- Ручной ввод данных ---")
    print("1. Откройте https://playerok.com в браузере и войдите в аккаунт.")
    print("2. Откройте DevTools (F12) -> вкладка Network (Сеть).")
    print("3. Обновите страницу и скопируйте заголовок Cookie и User-Agent любого запроса.")
    print()
    cookies = input("Вставьте Cookie (строку целиком): ").strip()
    if not cookies:
        print("[ERROR] Cookie не могут быть пустыми.")
        return

    ua = input("Вставьте User-Agent (Enter для значения по умолчанию): ").strip()
    if not ua:
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    save_auth(parse_cookie_string(cookies), ua)

def open_browser_login():
    browser_path = find_browser()
    if not browser_path:
        print("[WARN] Браузер Chrome/Chromium не найден в стандартных путях.")
        return manual_input()

    print(f"[INFO] Найден браузер: {browser_path}")
    print("Открываю страницу авторизации https://playerok.com/...")
    
    try:
        proc = subprocess.Popen([browser_path, "https://playerok.com/"])
    except Exception as e:
        print(f"[ERROR] Ошибка запуска браузера: {e}")
        return manual_input()

    print()
    print("Инструкция:")
    print("1. В открывшемся браузере войдите в свой аккаунт PlayerOK.")
    print("2. После успешного входа нажмите F12 (DevTools) -> вкладка Application -> Cookies -> playerok.com.")
    print("3. Скопируйте значение cookie или скопируйте Cookie из любого запроса в Network.")
    print()
    return manual_input()

def main():
    clear_screen()
    print_banner()
    print("Выберите способ авторизации:")
    print("1. Открыть браузер на ПК и ввести данные")
    print("2. Ввести Cookie и User-Agent вручную")
    print("3. Выход")
    print()

    choice = input("Ваш выбор (1-3): ").strip()
    if choice == "1":
        open_browser_login()
    elif choice == "2":
        manual_input()
    else:
        print("Отмена.")

if __name__ == "__main__":
    main()
