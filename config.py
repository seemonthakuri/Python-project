import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration, values pulled from environment variables."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

    # Build the PostgreSQL URI from individual pieces if DATABASE_URL
    # isn't set directly. Makes it easy to run locally with a .env file.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql://{user}:{pw}@{host}:{port}/{db}".format(
            user=os.environ.get("DB_USER", "postgres"),
            pw=os.environ.get("DB_PASSWORD", "123456789"),
            host=os.environ.get("DB_HOST", "localhost"),
            port=os.environ.get("DB_PORT", "5432"),
            db=os.environ.get("DB_NAME", "load_shedding"),
        ),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Timezone used when displaying / calculating durations.
    # Kept simple (UTC) - convert in the template if you need local time.
    TIMEZONE = os.environ.get("TZ", "UTC")
