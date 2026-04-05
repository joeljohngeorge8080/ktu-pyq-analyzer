from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://ktu_user:ktu_pass@localhost:5432/ktu_pyq"
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    SECRET_KEY: str = "dev-secret-key"

    @property
    def upload_path(self) -> Path:
        return Path(self.UPLOAD_DIR)

    @property
    def papers_path(self) -> Path:
        return self.upload_path / "papers"

    @property
    def questions_path(self) -> Path:
        return self.upload_path / "questions"

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        env_file = ".env"

settings = Settings()
