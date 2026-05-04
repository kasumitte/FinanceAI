from pydantic_settings import BaseSettings, SettingsConfigDict
import logging
from pathlib import Path
import time
import sys
from pydantic import ValidationError

BASE_DIR = Path(__file__).resolve().parent.parent

class Conf(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")
    database_url: str           # from .env
    llm_api_key: str
    graph_path: Path = BASE_DIR / "graphs"
    
    @classmethod
    def load_config(cls):
        try:
            config = cls() # type: ignore
            """ Graphs saving path """
            config.graph_path.mkdir(parents=True, exist_ok=True)
            return config
        
        except ValidationError as e:
            for error in e.errors():
                logging.error(f"Configuration error:  [{error['msg']}]")
            time.sleep(4)
            sys.exit(1) 
    