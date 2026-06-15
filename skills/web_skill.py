import logging
from agent.skill_system import BaseSkill

logger = logging.getLogger("Jarvis.Skill.Web")

class WebSkill(BaseSkill):
    def __init__(self):
        super().__init__(
            name="WebSkill",
            description="Handles web navigation, Google search queries, and YouTube video/search operations."
        )
        self.intents = {
            "OPEN_WEBSITE": {
                "description": "Opens specific websites or URLs in the default web browser.",
                "entities": {
                    "Target": "The website name or URL (e.g. YouTube, GitHub, google.com)"
                },
                "examples": [
                    "Open YouTube",
                    "Go to github.com",
                    "Open google",
                    "Launch stackoverflow"
                ]
            },
            "SEARCH_GOOGLE": {
                "description": "Performs a Google search in the default web browser.",
                "entities": {
                    "Query": "The text search query to submit to Google"
                },
                "examples": [
                    "Search Google for python tutorials",
                    "Google the weather today",
                    "Search for best programming languages"
                ]
            },
            "SEARCH_YOUTUBE": {
                "description": "Performs a video search on YouTube.",
                "entities": {
                    "Query": "The video search keywords"
                },
                "examples": [
                    "Search YouTube for Python tutorial",
                    "Find on YouTube space documentary",
                    "Look up standard model on YouTube"
                ]
            },
            "PLAY_YOUTUBE": {
                "description": "Streams a specific video directly on YouTube.",
                "entities": {
                    "Query": "The name or topic of the video to play"
                },
                "examples": [
                    "Play lo-fi hip hop on YouTube",
                    "Play standard model explanation",
                    "Stream code review music"
                ]
            }
        }
        
    def execute(self, intent: str, entities: dict, memory, automation_manager) -> str:
        if intent == "OPEN_WEBSITE":
            target = entities.get("Target")
            if not target:
                raise ValueError("A website target name or URL is required.")
            # Set active website context
            memory.set_active_web(target)
            return automation_manager.open_website(target)
            
        elif intent == "SEARCH_GOOGLE":
            query = entities.get("Query")
            if not query:
                raise ValueError("A search query is required.")
            return automation_manager.search_google(query)
            
        elif intent == "SEARCH_YOUTUBE":
            query = entities.get("Query")
            if not query:
                raise ValueError("A video search query is required.")
            memory.set_active_web("youtube")
            return automation_manager.search_youtube(query)
            
        elif intent == "PLAY_YOUTUBE":
            query = entities.get("Query")
            if not query:
                raise ValueError("A video stream title is required.")
            memory.set_active_web("youtube")
            return automation_manager.play_youtube(query)
            
        raise ValueError(f"Unsupported intent '{intent}' in WebSkill.")
