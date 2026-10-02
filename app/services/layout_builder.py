from app.schemas import ComicPanel, PanelStory


def build_comic_layout(stories: list[PanelStory], image_urls: list[str]) -> list[ComicPanel]:
    if len(stories) != len(image_urls):
        raise ValueError("Every story panel must have a matching image")
    return [
        ComicPanel(
            panel_number=story.panel_number,
            title=story.title,
            scene_description=story.scene_description,
            caption=story.caption,
            narration=story.narration,
            dialogue=story.dialogue,
            image_prompt=story.image_prompt,
            image_url=image_url,
        )
        for story, image_url in zip(stories, image_urls)
    ]
