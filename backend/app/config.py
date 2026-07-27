from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from dotenv import load_dotenv

# Force load local .env to override pre-existing OS env vars
load_dotenv(override=True)

class Settings(BaseSettings):
    SECRET_KEY: str = 'skylark-secret-key-for-dev-only-32chars'
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    FOUNDER_USERNAME: str = 'founder'
    FOUNDER_PASSWORD: str = 'skylark2026'
    
    USE_MOCK_MONDAY: bool = True
    MONDAY_API_KEY: str = ''
    DEALS_BOARD_ID: str = ''
    WORK_ORDERS_BOARD_ID: str = ''
    
    OPENAI_API_KEY: str = ''
    OPENAI_MODEL: str = 'gpt-4o-mini'
    
    GEMINI_API_KEY: str = ''
    GEMINI_MODEL: str = 'gemini-1.5-flash'
    
    DATA_DIR: str = '../data'
    FRONTEND_URL: str = 'http://localhost:5173'
    DATABASE_URL: str = 'sqlite:///./skylark.db'

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

@lru_cache
def get_settings():
    return Settings()
