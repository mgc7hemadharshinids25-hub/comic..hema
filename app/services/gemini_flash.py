import json
from app.config import Settings
from app.schemas import PanelOutline, PromptRequest
from app.services.prompts import outline_prompt


class GeminiFlashService:
    def __init__(self, settings: Settings):
        if not settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured")
        try:
            from google import genai
        except ImportError as exc:
            raise RuntimeError("google-genai is not installed. Run: pip install -r requirements.txt") from exc
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = settings.gemini_flash_model
        self.settings = settings

    @staticmethod
    def _generation_config(**kwargs):
        from google.genai import types
        return types.GenerateContentConfig(**kwargs)

    def generate_outline(self, request: PromptRequest) -> list[PanelOutline]:
        response = self.client.models.generate_content(
            model=self.model,
            contents=outline_prompt(request, self.settings.max_panels),
            config=self._generation_config(
                temperature=0.9,
                response_mime_type="application/json",
            ),
        )
        raw = response.text or "[]"
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError("Gemini Flash returned invalid JSON for the outline") from exc
        if not isinstance(data, list) or len(data) != self.settings.max_panels:
            raise RuntimeError("Gemini Flash did not return exactly 5 panels")
        return [PanelOutline.model_validate(item) for item in data]
