import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    ENV: str = os.getenv("ENV", "development")
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")

    # MongoDB (optional - not required for basic operation)
    MONGODB_URI: str | None = os.getenv("MONGODB_URI")
    DB_NAME: str = os.getenv("DB_NAME", "cv_shortlisting")
    MONGODB_ENABLED: bool = os.getenv("MONGODB_ENABLED", "false").lower() == "true"

    # Safety limits
    MAX_UPLOAD_MB: int = int(os.getenv("MAX_UPLOAD_MB", "10"))
    MAX_PDF_PAGES: int = int(os.getenv("MAX_PDF_PAGES", "12"))

    # LLM config
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.0"))


settings = Settings()

# Backward compatibility exports (for mongo.py if needed)
MONGODB_URI = settings.MONGODB_URI
DB_NAME = settings.DB_NAME
