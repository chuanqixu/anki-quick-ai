from pydantic import BaseSettings
import os


class Settings(BaseSettings):
    deck_name : str = "current"
    query : str = f'"deck:{deck_name}" introduced:1'
    field : str = ""

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), '.env')
        # env_file =".env"


settings = Settings()
