"""
Скрипт для получения OAuth токена Яндекс.Директ.

Использует Client ID и Client Secret для получения токена через OAuth flow.
"""

import webbrowser
import sys
from urllib.parse import urlencode, parse_qs, urlparse

# Ваши OAuth credentials
CLIENT_ID = "1f7754a45747445099c12580a7db63b0"
CLIENT_SECRET = "f82ef7f6944f4467ac606c154a524445"

# OAuth URLs
AUTH_URL = "https://oauth.yandex.ru/authorize"
TOKEN_URL = "https://oauth.yandex.ru/token"


def get_authorization_url():
    """
    Генерирует URL для авторизации.
    
    Returns:
        URL для открытия в браузере
    """
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "force_confirm": "yes"  # Всегда показывать окно подтверждения
    }
    
    return f"{AUTH_URL}?{urlencode(params)}"


def exchange_code_for_token(code: str):
    """
    Обменивает authorization code на access token.
    
    Args:
        code: Authorization code из URL
        
    Returns:
        Access token
    """
    try:
        import requests
    except ImportError:
        print("❌ Требуется библиотека requests")
        print("   Установите: pip install requests")
        sys.exit(1)
    
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    
    try:
        response = requests.post(TOKEN_URL, data=data)
        response.raise_for_status()
        
        result = response.json()
        
        if "access_token" in result:
            return result["access_token"]
        else:
            raise Exception(f"Токен не найден в ответе: {result}")
    
    except Exception as e:
        raise Exception(f"Ошибка получения токена: {e}")


def main():
    """Интерактивный процесс получения токена."""
    print("=" * 70)
    print("🔑 Получение OAuth токена для Яндекс.Директ API")
    print("=" * 70)
    
    # Если передан код как аргумент
    if len(sys.argv) > 1:
        code = sys.argv[1]
        print(f"\n✅ Используется код: {code}")
    else:
        print("\n📋 Шаг 1: Авторизация")
        print("-" * 70)
        
        auth_url = get_authorization_url()
        
        print("\nСейчас откроется браузер с формой авторизации Яндекс.")
        print("После авторизации вы будете перенаправлены на страницу с кодом.")
        print("\nURL для авторизации:")
        print(auth_url)
        
        input("\n👉 Нажмите Enter для открытия браузера...")
        
        # Открываем браузер
        webbrowser.open(auth_url)
        
        print("\n📋 Шаг 2: Получение кода")
        print("-" * 70)
        print("\nПосле авторизации вы увидите код подтверждения.")
        print("Скопируйте его и вставьте сюда.")
        
        code = input("\n👉 Введите код подтверждения: ").strip()
    
    if not code:
        print("\n❌ Код не введен!")
        return 1
    
    print("\n📋 Шаг 3: Получение токена")
    print("-" * 70)
    
    try:
        token = exchange_code_for_token(code)
        
        print("\n✅ Токен успешно получен!")
        print("=" * 70)
        print("\n🔑 Ваш OAuth токен:")
        print(f"\n{token}\n")
        print("=" * 70)
        
        # Сохраняем в .env файл
        print("\n📝 Сохранение токена в .env файл...")
        
        env_content = f"""# Яндекс.Директ API
YANDEX_DIRECT_TOKEN={token}

# OAuth credentials (не удаляйте!)
YANDEX_CLIENT_ID={CLIENT_ID}
YANDEX_CLIENT_SECRET={CLIENT_SECRET}

# Опциональные настройки
# YANDEX_DIRECT_LOGIN=your_login
# YANDEX_DIRECT_CLIENT_LOGIN=client_login
"""
        
        with open(".env", "w", encoding="utf-8") as f:
            f.write(env_content)
        
        print("✅ Токен сохранен в .env файл")
        
        print("\n🎉 Готово!")
        print("\nТеперь вы можете использовать API:")
        print("  python yandex_direct_api.py test")
        print("  python yandex_direct_api.py campaigns")
        print("  python yandex_direct_api.py stats 2026-06-08 2026-06-14")
        
        return 0
    
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
