from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "RojinMatch"
    DATABASE_URL: str = "sqlite+aiosqlite:///./rojinmatch.db"
    
    # Mock settings
    MOCK_TWILIO: bool = True
    MOCK_DEEPGRAM: bool = True

    class Config:
        env_file = ".env"

settings = Settings()
