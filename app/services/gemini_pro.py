import json
import time

from app.config import Settings
from app.schemas import PanelOutline, PanelStory, PromptRequest
from app.services.prompts import story_prompt


class GeminiProService:
    def __init__(self, settings: Settings):
        if not settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured")

        try:
            from google import genai
            from google.genai import errors
        except ImportError as exc:
            raise RuntimeError(
                "google-genai is not installed. Run: pip install -r requirements.txt"
            ) from exc

        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = settings.gemini_pro_model

        # Use the configured Flash model as a fallback. If it is not configured,
        # use Google's current stable Flash model.
        self.fallback_model = getattr(
            settings, "gemini_flash_model", "gemini-3.8-flash"
        )
        self.api_errors = errors

    @staticmethod
    def _generation_config(**kwargs):
        from google.genai import types
        return types.GenerateContentConfig(**kwargs)

    def _generate_with_retry(self, model: str, prompt: str):
        last_error = None

        # 503/429/5xx responses can be temporary. Retry with exponential backoff.
        for attempt in range(3):
            try:
                return self.client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=self._generation_config(
                        temperature=0.85,
                        response_mime_type="application/json",
                    ),
                )
            except self.api_errors.APIError as exc:
                last_error = exc
                code = getattr(exc, "code", None)

                if code not in (429, 500, 502, 503, 504):
                    raise

                if attempt < 2:
                    time.sleep(2 ** attempt)

        raise last_error

    def generate_story(
        self, request: PromptRequest, outline: list[PanelOutline]
    ) -> list[PanelStory]:
        outline_json = json.dumps(
            [item.model_dump() for item in outline],
            ensure_ascii=False,
        )
        prompt = story_prompt(request, outline_json)

        models = [self.model]
        if self.fallback_model and self.fallback_model not in models:
            models.append(self.fallback_model)

        last_error = None

        for model in models:
            try:
                response = self._generate_with_retry(model, prompt)
                raw = response.text or "[]"

                try:
                    data = json.loads(raw)
                except json.JSONDecodeError as exc:
                    raise RuntimeError(
                        f"{model} returned invalid JSON for the story"
                    ) from exc

                if not isinstance(data, list) or len(data) != len(outline):
                    raise RuntimeError(
                        f"{model} did not return the expected panel count"
                    )

                return [PanelStory.model_validate(item) for item in data]

            except self.api_errors.APIError as exc:
                last_error = exc
                code = getattr(exc, "code", None)

                # Try the fallback model for temporary availability/rate-limit
                # problems or when the configured model is unavailable.
                if code in (404, 429, 500, 502, 503, 504):
                    continue
                raise RuntimeError(
                    f"Gemini API error ({code}): {getattr(exc, 'message', str(exc))}"
                ) from exc

        if last_error is not None:
            code = getattr(last_error, "code", "unknown")
            message = getattr(last_error, "message", str(last_error))
            raise RuntimeError(
                f"Gemini is temporarily unavailable (HTTP {code}). "
                f"Please try again in a moment. Details: {message}"
            ) from last_error

        raise RuntimeError("No Gemini model is configured")
