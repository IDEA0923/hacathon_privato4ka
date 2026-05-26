from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import env
class Settings(BaseSettings):
    bot_token: str = Field(..., alias="BOT_TOKEN")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,  # <-- Add this line
    )

def get_settings() -> Settings:
    return Settings(bot_token=env.TOKEN)  # Now this works perfectly!