import os
import json
import logging

logger = logging.getLogger("Jarvis.Agent.UserMemory")

class UserMemory:
    def __init__(self, filepath=None):
        if filepath is None:
            # Default location in workspace
            self.filepath = r"c:\Users\Prajwal HY\Voice_assistant\agent\user_memory.json"
        else:
            self.filepath = filepath
            
        self.data = {
            "user_name": "Prajwal",
            "preferences": {
                "favorite_apps": ["notepad++", "vs code", "chrome", "blender", "discord"],
                "favorite_websites": ["youtube", "github", "google"],
                "theme": "dark"
            },
            "facts": [
                "User's name is Prajwal.",
                "User is a programmer developing an advanced voice assistant.",
                "User prefers a dark visual theme.",
                "User likes sleek, premium glassmorphic UI designs."
            ],
            "reminders": [],
            "notes": []
        }
        self.load()

    def load(self):
        """Loads user memory from local disk if it exists, otherwise creates it."""
        try:
            if os.path.exists(self.filepath):
                with open(self.filepath, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    # Merge keys to support schema upgrades
                    for key in self.data:
                        if key in loaded:
                            if isinstance(self.data[key], dict) and isinstance(loaded[key], dict):
                                self.data[key].update(loaded[key])
                            else:
                                self.data[key] = loaded[key]
                logger.info(f"User memory loaded successfully from: '{self.filepath}'")
            else:
                self.save()
                logger.info(f"Created new user memory file at: '{self.filepath}'")
        except Exception as e:
            logger.error(f"Error loading user memory: {e}")

    def save(self):
        """Saves current state of memory back to disk."""
        try:
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            logger.debug("User memory saved to disk.")
        except Exception as e:
            logger.error(f"Error saving user memory: {e}")

    def get_user_name(self) -> str:
        return self.data.get("user_name", "Prajwal")

    def set_user_name(self, name: str):
        self.data["user_name"] = name.strip()
        self.save()

    def add_fact(self, fact: str):
        fact_clean = fact.strip()
        if fact_clean and fact_clean not in self.data["facts"]:
            self.data["facts"].append(fact_clean)
            self.save()
            logger.info(f"Learned new user fact: '{fact_clean}'")

    def add_reminder(self, reminder: str):
        reminder_clean = reminder.strip()
        if reminder_clean and reminder_clean not in self.data["reminders"]:
            self.data["reminders"].append(reminder_clean)
            self.save()
            logger.info(f"Added reminder: '{reminder_clean}'")

    def add_note(self, note: str):
        note_clean = note.strip()
        if note_clean and note_clean not in self.data["notes"]:
            self.data["notes"].append(note_clean)
            self.save()
            logger.info(f"Added note: '{note_clean}'")

    def set_preference(self, key: str, value):
        self.data["preferences"][key] = value
        self.save()

    def get_all_context_string(self) -> str:
        """Returns a compiled representation of all user memories for injection into contexts."""
        facts_str = "\n".join([f"- {f}" for f in self.data["facts"]])
        reminders_str = "\n".join([f"- {r}" for r in self.data["reminders"]])
        notes_str = "\n".join([f"- {n}" for n in self.data["notes"]])
        
        context = f"User Name: {self.get_user_name()}\n"
        context += f"User Preferences:\n"
        for k, v in self.data["preferences"].items():
            context += f"  - {k}: {v}\n"
            
        context += f"\nKnown User Facts:\n{facts_str or '- None recorded'}\n"
        context += f"\nActive Reminders:\n{reminders_str or '- None'}\n"
        context += f"\nSaved Notes:\n{notes_str or '- None'}\n"
        return context
