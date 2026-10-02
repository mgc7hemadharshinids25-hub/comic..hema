from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.routes import router

settings = get_settings()
settings.static_path.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="ComicCraft API",
    description="AI comic story creator using Gemini and Stable Diffusion-compatible image generation.",
    version="1.0.0",
)
app.mount("/static", StaticFiles(directory=str(settings.static_path)), name="static")
app.include_router(router)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "app": settings.app_name,
        "image_provider": settings.image_provider,
        "gemini_flash_model": settings.gemini_flash_model,
        "gemini_pro_model": settings.gemini_pro_model,
    }
