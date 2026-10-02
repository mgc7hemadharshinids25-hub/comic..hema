from pathlib import Path
from uuid import uuid4
from urllib.parse import urlparse

from fpdf import FPDF
from fpdf.enums import XPos, YPos
from PIL import Image

from app.config import BASE_DIR, Settings
from app.schemas import ComicPanel


def _local_image_path(image_url: str) -> Path:
    parsed = urlparse(image_url)
    relative = parsed.path.lstrip("/")
    path = BASE_DIR / relative
    if not path.is_file():
        raise FileNotFoundError(f"Comic image not found: {path}")
    return path


def _safe_text(value: str) -> str:
    return value.encode("latin-1", "replace").decode("latin-1")


def save_pdf(panels: list[ComicPanel], settings: Settings) -> str:
    export_dir = settings.static_path / "exports"
    filename = f"comic_{uuid4().hex}.pdf"
    output_path = export_dir / filename

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=14)

    for panel in panels:
        image_path = _local_image_path(panel.image_url)
        with Image.open(image_path) as image:
            width, height = image.size
        max_width = 180
        max_height = 125
        scale = min(max_width / width, max_height / height)
        render_width = width * scale
        render_height = height * scale

        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, _safe_text(f"Panel {panel.panel_number}: {panel.title}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        x = (210 - render_width) / 2
        pdf.image(str(image_path), x=x, y=25, w=render_width, h=render_height)
        pdf.set_y(30 + render_height)

        sections = [
            ("Scene", panel.scene_description),
            ("Caption", panel.caption),
            ("Narration", panel.narration),
        ]
        if panel.dialogue:
            sections.append(("Dialogue", panel.dialogue))

        for heading, text in sections:
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(0, 7, _safe_text(heading), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("Helvetica", size=10)
            pdf.multi_cell(0, 5, _safe_text(text))
            pdf.ln(2)

    pdf.output(str(output_path))
    return f"/download/{filename}"
