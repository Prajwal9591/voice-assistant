import os
import json
import logging

logger = logging.getLogger("Jarvis.ConversationMemory")

class ConversationMemory:
    """
    Handles local JSON-based persistence of user information, profile metrics, 
    interests, and previous conversation facts.
    """
    def __init__(self, filepath=None):
        if filepath is None:
            self.filepath = r"c:\Users\Prajwal HY\Voice_assistant\memory_store\user_memory.json"
        else:
            self.filepath = filepath
            
        self.data = {
            "user_name": "Prajwal",
            "preferences": {
                "theme": "dark",
                "assistant_volume": 1.0,
                "speech_rate": 175
            },
            "interests": [
                "python programming",
                "voice assistant engineering",
                "quantum physics"
            ],
            "favorite_applications": [
                "notepad++",
                "vs code",
                "chrome",
                "discord"
            ],
            "previous_conversation_facts": [
                "User is a passionate software engineer.",
                "User loves smooth glassmorphic interfaces."
            ]
        }
        self.load_memory()

    def load_memory(self):
        """Loads conversation memory from local disk inside the memory_store directory."""
        try:
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            if os.path.exists(self.filepath):
                with open(self.filepath, "r", encoding="utf-8") as f:
                    loaded_data = json.load(f)
                    for key in self.data:
                        if key in loaded_data:
                            if isinstance(self.data[key], dict) and isinstance(loaded_data[key], dict):
                                self.data[key].update(loaded_data[key])
                            else:
                                self.data[key] = loaded_data[key]
                logger.info(f"Persistent conversation memory loaded from: '{self.filepath}'")
            else:
                self.save_memory()
                logger.info(f"Initialized new persistent memory database at: '{self.filepath}'")
        except Exception as e:
            logger.error(f"Error loading conversation memory: {e}")

    def save_memory(self):
        """Persists the memory schema to local disk using JSON formatting."""
        try:
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            logger.debug("Conversation memory successfully written to disk.")
        except Exception as e:
            logger.error(f"Error saving conversation memory: {e}")

    def get_user_name(self) -> str:
        return self.data.get("user_name", "Prajwal")

    def set_user_name(self, name: str):
        self.data["user_name"] = name.strip()
        self.save_memory()
        logger.info(f"User name updated in memory to: '{self.data['user_name']}'")

    def add_fact(self, fact: str):
        fact_clean = fact.strip()
        if fact_clean and fact_clean not in self.data["previous_conversation_facts"]:
            self.data["previous_conversation_facts"].append(fact_clean)
            self.save_memory()
            logger.info(f"Learned conversational fact: '{fact_clean}'")

    def add_interest(self, interest: str):
        interest_clean = interest.strip().lower()
        if interest_clean and interest_clean not in self.data["interests"]:
            self.data["interests"].append(interest_clean)
            self.save_memory()
            logger.info(f"Learned new interest: '{interest_clean}'")

    def add_favorite_app(self, app: str):
        app_clean = app.strip().lower()
        if app_clean and app_clean not in self.data["favorite_applications"]:
            self.data["favorite_applications"].append(app_clean)
            self.save_memory()
            logger.info(f"Learned new favorite application: '{app_clean}'")

    def set_preference(self, key: str, value):
        self.data["preferences"][key] = value
        self.save_memory()

    def get_profile_context(self) -> str:
        """Compiles user metrics and facts into a context prompt string."""
        facts_str = "\n".join([f"- {f}" for f in self.data["previous_conversation_facts"]])
        interests_str = ", ".join(self.data["interests"])
        apps_str = ", ".join(self.data["favorite_applications"])
        
        context = f"User Name: {self.get_user_name()}\n"
        context += f"Interests: {interests_str}\n"
        context += f"Favorite Applications: {apps_str}\n"
        context += f"Known Facts:\n{facts_str or '- None'}"
        return context
