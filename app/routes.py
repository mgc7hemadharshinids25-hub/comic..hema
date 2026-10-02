from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import BASE_DIR, get_settings
from app.schemas import ComicResponse, ImageRequest, PromptRequest
from app.services.comic_service import ComicService

router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def service() -> ComicService:
    return ComicService(get_settings())


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})


@router.post("/generate", response_class=HTMLResponse)
async def generate(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):
    try:
        data = PromptRequest(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )
        layout, pdf_url, title = service().generate(data)
        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={"layout": layout, "pdf_url": pdf_url, "title": title},
        )
    except Exception as exc:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"error": str(exc)},
            status_code=500,
        )


@router.post("/generate-comic/json", response_model=ComicResponse)
async def generate_json(payload: PromptRequest):
    try:
        layout, pdf_url, title = service().generate(payload)
        return ComicResponse(title=title, panels=layout, pdf_url=pdf_url)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/test-image")
async def test_image(payload: ImageRequest):
    try:
        image_url = service().generate_image_only(payload.prompt)
        return {"success": True, "image_url": image_url}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/export-success", response_class=HTMLResponse)
async def export_success(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={},
    )


@router.get("/download/{filename}")
async def download_pdf(filename: str):
    # Kept as a dedicated route so the browser receives a download rather than exposing directory traversal.
    if Path(filename).name != filename or not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid PDF filename")
    path = get_settings().static_path / "exports" / filename
    if not path.is_file():
        raise HTTPException(status_code=404, detail="PDF not found")
    return FileResponse(path, media_type="application/pdf", filename=filename)
