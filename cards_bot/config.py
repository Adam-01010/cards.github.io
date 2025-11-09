from pydantic_settings  import BaseSettings
import os
from dotenv import load_dotenv
load_dotenv()

class Settings(BaseSettings):
    BOT_TOKEN: str = os.getenv('TOKEN')
    DATABASE_URL: str = "sqlite+aiosqlite:///cards.db"

settings = Settings()


