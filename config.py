from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # .env fine load karne ke liye config
    model_config = SettingsConfigDict(env_file='.env')

# Settings ka single instance create karein
settings = Settings()