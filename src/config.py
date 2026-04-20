from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    base_path: str = "mind-vault"
    port: int = 10016

    data_dir: Path = Path("./data")
    cache_dir: Path | None = None

    ai_provider: str = "gemini"
    ai_api_key: str | None = None
    ai_model: str | None = None
    ai_base_url: str | None = None

    def model_post_init(self, __context) -> None:
        self.base_path = self.base_path.strip("/")
        if self.cache_dir is None:
            object.__setattr__(self, "cache_dir", self.data_dir / "cache")

    @property
    def root_path(self) -> str:
        return f"/{self.base_path}" if self.base_path else ""


settings = Settings()
