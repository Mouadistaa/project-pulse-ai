from typing import List, Optional
from pydantic_settings import BaseSettings
import json

class Settings(BaseSettings):
    PROJECT_NAME: str = "Project Pulse AI"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    
    DATABASE_URL: str
    REDIS_URL: str
    BACKEND_CORS_ORIGINS: str = "[]"
    
    MOCK_MODE: bool = True
    LLM_ENABLED: bool = False
    LLM_API_KEY: str = ""
    
    # Trello integration
    TRELLO_KEY: str = ""
    TRELLO_TOKEN: str = ""
    TRELLO_BOARD_IDS: str = ""  # Comma-separated board IDs, empty = all accessible
    
    # GitHub integration
    GITHUB_TOKEN: str = ""
    
    @property
    def CORS_ORIGINS(self) -> List[str]:
        try:
            return json.loads(self.BACKEND_CORS_ORIGINS)
        except:
            return []
    
    @property
    def trello_board_ids_list(self) -> List[str]:
        """Parse comma-separated board IDs into list."""
        if not self.TRELLO_BOARD_IDS:
            return []
        return [bid.strip() for bid in self.TRELLO_BOARD_IDS.split(",") if bid.strip()]

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
