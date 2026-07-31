from decouple import config, Csv

# --- Database ---
# Рядок підключення у "django-style" форматі, напр.:
# postgres://user:password@host:5432/dbname
DATABASE_URL: str = config("DATABASE_URL")

# Чи виводити SQL-запити в консоль (echo для SQLAlchemy). На проді - вимкнено.
DEBUG: bool = config("DEBUG", default=False, cast=bool)

# --- JWT / Auth ---
SECRET_KEY: str = config("SECRET_KEY")
ALGORITHM: str = config("ALGORITHM", default="HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = config(
    "ACCESS_TOKEN_EXPIRE_MINUTES", default=60 * 24, cast=int
)

# --- Superuser (єдиний адмін всього проєкту) ---
ADMIN_USERNAME: str = config("ADMIN_USERNAME")
ADMIN_PASSWORD_HASH: str = config("ADMIN_PASSWORD_HASH")

# --- Cloudflare R2 ---
R2_ACCOUNT_ID: str = config("R2_ACCOUNT_ID")
R2_ACCESS_KEY_ID: str = config("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY: str = config("R2_SECRET_ACCESS_KEY")
R2_BUCKET_NAME: str = config("R2_BUCKET_NAME")
R2_PUBLIC_URL: str = config("R2_PUBLIC_URL", default="")

# --- CORS ---
CORS_ORIGINS: list[str] = config(
    "CORS_ORIGINS", default="http://localhost:5173", cast=Csv()
)
