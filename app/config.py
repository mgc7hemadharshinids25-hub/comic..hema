from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "ComicCraft"
    debug: bool = True

    gemini_api_key: str = ""
    gemini_flash_model: str = "gemini-3.7-flash"
    gemini_pro_model: str = "gemini-3.7-pro"

    hf_api_key: str = ""
    hf_image_model: str = "stabilityai/stable-diffusion-3-medium-diffusers"
    image_provider: str = "hf_api"
    local_image_model: str = "runwayml/stable-diffusion-v1-5"

    max_panels: int = 5
    image_width: int = 768
    image_height: int = 768
    static_dir: str = "static"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def static_path(self) -> Path:
        path = BASE_DIR / self.static_dir
        path.mkdir(parents=True, exist_ok=True)
        (path / "panels").mkdir(parents=True, exist_ok=True)
        (path / "exports").mkdir(parents=True, exist_ok=True)
        return path


@lru_cache
def get_settings() -> Settings:
    return Settings()
