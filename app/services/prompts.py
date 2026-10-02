from app.schemas import PromptRequest


def outline_prompt(request: PromptRequest, panel_count: int = 5) -> str:
    return f"""
You are the outline writer for ComicCraft, an AI comic creator.
Create exactly {panel_count} connected comic panels.

User concept: {request.story_prompt}
Main character: {request.character_name}
Setting: {request.setting}
Tone: {request.tone}
Art style: {request.art_style}

Return ONLY valid JSON: an array of exactly {panel_count} objects.
Each object must contain:
- panel_number: integer from 1 to {panel_count}
- title: short panel title
- scene_description: 1-2 sentence visual scene description
- image_prompt: detailed image-generation prompt; describe characters, action, environment, composition and the requested art style. Do not include text, speech bubbles, captions, logos, or watermarks.

Keep the same main character visually and narratively consistent across all panels.
The story must have a clear beginning, development, turning point, and ending.
""".strip()


def story_prompt(request: PromptRequest, outline_json: str) -> str:
    return f"""
You are the story writer for ComicCraft.
Expand the supplied 5-panel outline into polished comic narration and dialogue.

Original user concept: {request.story_prompt}
Character: {request.character_name}
Setting: {request.setting}
Tone: {request.tone}
Art style: {request.art_style}

Outline:
{outline_json}

Return ONLY valid JSON: an array with exactly 5 objects in panel order.
Each object must contain:
- panel_number
- title
- scene_description
- caption: a short atmospheric caption
- narration: concise comic narration
- dialogue: natural character dialogue; if no dialogue is needed, use an empty string
- image_prompt: preserve the outline image prompt and improve it only when useful

Do not invent extra panels. Keep names, setting and story continuity consistent.
""".strip()
