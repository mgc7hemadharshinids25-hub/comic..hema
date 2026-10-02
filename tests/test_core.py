from pathlib import Path

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import app
from app.schemas import PromptRequest
from app.services.exporters import save_pdf
from app.schemas import ComicPanel


def test_prompt_request_validation():
    payload = PromptRequest(
        story_prompt="A fox explores a magical forest",
        character_name="Fenn",
        setting="Forest",
        tone="Funny",
        art_style="Comic book",
    )
    assert payload.character_name == "Fenn"


def test_health_endpoint():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_homepage():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "Story Prompt" in response.text
    assert "Main Character Name" in response.text


def test_pdf_export(tmp_path, monkeypatch):
    # Use the application's normal static structure but replace BASE_DIR resolution indirectly
    # by creating a real test image under the project static folder.
    from app.services import exporters
    image_dir = Path(exporters.BASE_DIR) / "static" / "panels"
    image_dir.mkdir(parents=True, exist_ok=True)
    image_path = image_dir / "test_export.png"
    from PIL import Image
    Image.new("RGB", (300, 300), "white").save(image_path)

    settings = Settings(static_dir="static")
    panel = ComicPanel(
        panel_number=1,
        title="Beginning",
        scene_description="A fox enters the forest.",
        caption="The forest wakes.",
        narration="Fenn takes the first step.",
        dialogue="Hello, forest!",
        image_prompt="A fox entering a forest.",
        image_url="/static/panels/test_export.png",
    )
    pdf_url = save_pdf([panel], settings)
    assert pdf_url.startswith("/download/")
    pdf_name = pdf_url.rsplit("/", 1)[-1]
    assert (settings.static_path / "exports" / pdf_name).exists()
    image_path.unlink(missing_ok=True)
    (settings.static_path / "exports" / pdf_name).unlink(missing_ok=True)
