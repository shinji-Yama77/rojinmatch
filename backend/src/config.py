from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "RojinMatch"
    DATABASE_URL: str = "sqlite+aiosqlite:///./rojinmatch.db"
    
    # Twilio Settings
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""
    TWILIO_API_KEY_SID: str = ""
    TWILIO_API_KEY_SECRET: str = ""
    
    # Mock settings
    MOCK_TWILIO: bool = False
    MOCK_DEEPGRAM: bool = True

    class Config:
        env_file = ".env"

settings = Settings()
