# ComicCraft — AI Comic Story Creator

ComicCraft is a FastAPI web application that turns a user's idea into a 5-panel comic using a two-stage Gemini story pipeline, AI-generated panel artwork, and PDF export.

## Architecture

- **Frontend:** Jinja2 + HTML + CSS + small JavaScript enhancements
- **Backend:** FastAPI + Pydantic
- **Story AI:** Gemini Flash for a structured 5-panel outline, Gemini Pro for narration/dialogue
- **Image AI:** Hugging Face Inference API by default, with an optional local Diffusers provider
- **Export:** fpdf2
- **Assets:** `static/panels` and `static/exports`

## Important model note

The original project document names Gemini 1.5 Flash/Pro and `runwayml/stable-diffusion-v1-5`. Model availability changes over time. This implementation keeps the same Flash → Pro → image architecture but reads model IDs from `.env`. The included defaults are modern configurable Gemini model names; if your API account exposes different models, change the variables without changing application code.

## Quick start on Windows

```powershell
cd ComicCraft
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
```

Open `.env` and add:

```env
GEMINI_API_KEY=...
HF_API_KEY=...
```

Then run:

```powershell
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000

API docs: http://127.0.0.1:8000/docs

## Image provider options

### Hugging Face API (recommended for a normal laptop)

```env
IMAGE_PROVIDER=hf_api
HF_API_KEY=...
HF_IMAGE_MODEL=stabilityai/stable-diffusion-xl-base-1.0
```

### Local Diffusers

Install the optional local requirements:

```powershell
pip install -r requirements-local-image.txt
```

Then set:

```env
IMAGE_PROVIDER=local_diffusers
LOCAL_IMAGE_MODEL=runwayml/stable-diffusion-v1-5
```

A GPU is strongly recommended for local image generation.

## API example

POST `/generate-comic/json`:

```json
{
  "story_prompt": "A brave fox exploring an enchanted forest",
  "character_name": "Fenn",
  "setting": "enchanted forest",
  "tone": "dramatic",
  "art_style": "comic book"
}
```

## Test image generation

POST `/test-image` with:

```json
{"prompt":"A brave fox in an enchanted forest, comic book style"}
```

## Testing

Run unit tests:

```powershell
pytest -q
```

The tests validate schemas, prompt construction, PDF generation, and route availability without requiring live AI calls.
