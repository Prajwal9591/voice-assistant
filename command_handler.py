import logging
import re
from automation import AutomationManager
from ai_engine import AIEngine
from agent import JarvisAgent

logger = logging.getLogger("Jarvis.CommandHandler")

class CommandHandler:
    def __init__(self, automation_manager: AutomationManager, ai_engine: AIEngine):
        """
        Initializes the CommandHandler, acting as the primary gateway to the
        new intelligent agent reasoning framework.
        """
        self.automation = automation_manager
        self.ai = ai_engine
        
        # Instantiate the new Cognitive Agent Architecture
        self.agent = JarvisAgent(self.ai, self.automation)
        self.wake_words = ["jarvis", "hey jarvis", "ok jarvis", "hello jarvis"]

    def clean_command(self, raw_command: str) -> str:
        """
        Strips wake words and normalizes whitespace from a raw spoken command.
        """
        cleaned = raw_command.lower().strip()
        for wake in self.wake_words:
            cleaned = re.sub(rf"\b{re.escape(wake)}\b", "", cleaned).strip()
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned

    def handle(self, raw_command: str) -> str:
        """
        Routes the voice commands through the intelligent cognitive agent pipeline.
        """
        logger.info(f"Command Received: '{raw_command}'")
        command = self.clean_command(raw_command)
        logger.info(f"Cleaned Command: '{command}'")

        # Empty query (wake word only)
        if not command:
            logger.info("Empty command processed - Wake word only detected.")
            return "Yes, sir?"

        # Execute cognitive reasoning loop
        response = self.agent.process_query(command)
        return response
