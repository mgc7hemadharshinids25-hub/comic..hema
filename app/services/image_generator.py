from pathlib import Path
from uuid import uuid4

from PIL import Image
from huggingface_hub import InferenceClient

from app.config import Settings


class ImageGenerator:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.output_dir = settings.static_path / "panels"
        self._local_pipe = None

    def generate_image(self, prompt: str) -> str:
        provider = self.settings.image_provider.lower().strip()
        filename = f"panel_{uuid4().hex}.png"
        output_path = self.output_dir / filename

        if provider == "hf_api":
            self._generate_hf(prompt, output_path)
        elif provider == "local_diffusers":
            self._generate_local(prompt, output_path)
        else:
            raise RuntimeError(
                f"Unsupported IMAGE_PROVIDER '{provider}'. Use 'hf_api' or 'local_diffusers'."
            )

        return f"/static/panels/{filename}"

    def _generate_hf(self, prompt: str, output_path: Path) -> None:
        if not self.settings.hf_api_key:
            raise RuntimeError("HF_API_KEY is not configured for Hugging Face image generation")
        client = InferenceClient(
            provider="auto",
            api_key=self.settings.hf_api_key,
        )
        image = client.text_to_image(
            prompt=prompt,
            model=self.settings.hf_image_model,
            width=self.settings.image_width,
            height=self.settings.image_height,
            num_inference_steps=25,
        )
        if not isinstance(image, Image.Image):
            raise RuntimeError("Hugging Face did not return an image")
        image.convert("RGB").save(output_path, format="PNG")

    def _generate_local(self, prompt: str, output_path: Path) -> None:
        try:
            import torch
            from diffusers import StableDiffusionPipeline
        except ImportError as exc:
            raise RuntimeError(
                "Local Diffusers mode requires requirements-local-image.txt to be installed"
            ) from exc

        if self._local_pipe is None:
            dtype = torch.float16 if torch.cuda.is_available() else torch.float32
            kwargs = {"torch_dtype": dtype}
            if torch.cuda.is_available():
                kwargs["variant"] = "fp16"
            self._local_pipe = StableDiffusionPipeline.from_pretrained(
                self.settings.local_image_model,
                **kwargs,
            )
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self._local_pipe = self._local_pipe.to(device)

        result = self._local_pipe(
            prompt=prompt,
            width=self.settings.image_width,
            height=self.settings.image_height,
            num_inference_steps=25,
        )
        result.images[0].convert("RGB").save(output_path, format="PNG")
