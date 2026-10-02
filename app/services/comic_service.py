from app.config import Settings
from app.schemas import ComicPanel, PromptRequest
from app.services.exporters import save_pdf
from app.services.gemini_flash import GeminiFlashService
from app.services.gemini_pro import GeminiProService
from app.services.image_generator import ImageGenerator
from app.services.layout_builder import build_comic_layout


class ComicService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.flash = GeminiFlashService(settings)
        self.pro = GeminiProService(settings)
        self.images = ImageGenerator(settings)

    def generate(self, request: PromptRequest) -> tuple[list[ComicPanel], str, str]:
        outline = self.flash.generate_outline(request)
        stories = self.pro.generate_story(request, outline)
        image_urls = [self.images.generate_image(panel.image_prompt) for panel in stories]
        layout = build_comic_layout(stories, image_urls)
        title = f"{request.character_name}'s Comic"
        pdf_url = save_pdf(layout, self.settings)
        return layout, pdf_url, title

    def generate_image_only(self, prompt: str) -> str:
        return self.images.generate_image(prompt)
