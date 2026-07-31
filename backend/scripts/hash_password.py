"""
Генерує bcrypt-хеш пароля для .env (ADMIN_PASSWORD_HASH).

Використання:
    python scripts/hash_password.py "мій_секретний_пароль"
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.security import hash_password  # noqa: E402


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Використання: python scripts/hash_password.py "пароль"')
        sys.exit(1)

    password = sys.argv[1]
    print(hash_password(password))
