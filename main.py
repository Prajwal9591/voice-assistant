import os
import sys
import logging
import threading
import time
import tkinter as tk
import customtkinter as ctk
from speech_engine import SpeechEngine
from ai_engine import AIEngine
from automation import AutomationManager
from command_handler import CommandHandler
from conversation_manager import ConversationManager
from gui import JarvisGUI, QueueLogHandler

# 1. Setup Global Logging
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    handlers=[
        logging.FileHandler("jarvis.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("Jarvis")

class JarvisAssistant:
    def __init__(self):
        logger.info("Initializing J.A.R.V.I.S. Core Modular Systems...")
        
        # Initialize Sub-engines
        self.automation = AutomationManager()
        self.ai = AIEngine()
        self.command_handler = CommandHandler(self.automation, self.ai)
        
        # Conversational intelligence layer (multi-turn dialogue, emotional awareness)
        self.conversation_manager = ConversationManager(self.ai)
        
        # CustomTkinter UI Root
        self.root = ctk.CTk()
        
        # Initialize Speech Engine with callback to GUI state transition
        self.speech = SpeechEngine(
            voice_gender="female",
            speech_rate=175,
            volume=1.0,
            on_state_change=self.on_speech_state_change
        )
        
        # Create and wire GUI
        self.gui = JarvisGUI(
            self.root,
            on_command_submit=self.process_command_intent,
            on_voice_toggle=self.toggle_voice_loop,
            on_settings_change=self.update_settings
        )
        
        # Bind the logging engine to send live updates directly to the GUI's logs box
        queue_handler = QueueLogHandler(self.gui)
        queue_handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
        logging.getLogger().addHandler(queue_handler)
        
        # Control flags
        self.voice_listening_enabled = True
        self.is_running = True
        
        # Launch startup greeting on background thread (non-blocking)
        greet_thread = threading.Thread(target=self.greet_user, daemon=True)
        greet_thread.start()
        
        # Launch Asynchronous Voice Loop in a background worker thread
        self.voice_thread = threading.Thread(target=self.continuous_voice_loop, daemon=True)
        self.voice_thread.start()

    def greet_user(self):
        """Speaks a personalized startup greeting using the user's stored name."""
        time.sleep(1.2)  # short pause for GUI initialization
        user_name = self.ai.memory.get_user_name()
        greeting = f"Systems online, {user_name}. Cognitive layers are running at optimal capacity. How can I assist you today?"
        self.gui.append_log("[Core]: Initializing auditory circuits.")
        self.gui.append_dialog(f"JARVIS: {greeting}", is_user=False)
        self.speech.speak(greeting)

    def on_speech_state_change(self, state):
        """Passes speech engine state transitions safely down to GUI thread."""
        self.gui.set_state(state)

    def update_settings(self, key, value):
        """Processes parameter updates from GUI sliders and menus."""
        if key == "rate":
            self.speech.set_rate(value)
        elif key == "volume":
            self.speech.set_volume(value)
        elif key == "voice":
            self.speech.set_voice(value)
        elif key == "greet":
            greet_thread = threading.Thread(target=self.greet_user, daemon=True)
            greet_thread.start()

    def toggle_voice_loop(self, is_enabled):
        """Enables or disables continuous microphone capture loop."""
        self.voice_listening_enabled = is_enabled
        if is_enabled:
            logger.info("Microphone loop enabled.")
        else:
            logger.info("Microphone loop suspended.")

    def process_command_intent(self, command_text: str):
        """
        Runs on background worker threads. Handles the evaluation, execution,
        and audio reporting of user query strings.

        Pipeline priority:
          1. Structured automation commands (via JarvisAgent cognitive pipeline)
          2. Conversational fallback (via ConversationManager + Gemini)
        """
        # Route through the cognitive agent (intent → plan → execute)
        response = self.command_handler.handle(command_text)

        # Agent returns None when it wants the Conversation Manager to handle it
        # (intent unclear / classified as CONVERSATIONAL)
        if response is None or response == "":
            active_app = self.command_handler.agent.memory.active_application
            active_web = self.command_handler.agent.memory.active_website
            response = self.conversation_manager.process_turn(
                command_text,
                active_app=active_app,
                active_web=active_web
            )

        if response == "TERMINATE":
            farewell = "Powering down cognitive layers. Goodbye, sir."
            self.gui.append_dialog(f"JARVIS: {farewell}", is_user=False)
            self.speech.speak(farewell)
            self.is_running = False
            self.root.after(500, self.shutdown)
            return

        # Return responses back to user interface
        self.gui.append_dialog(f"JARVIS: {response}", is_user=False)
        self.speech.speak(response)

    def continuous_voice_loop(self):
        """
        Continuous voice command recognition worker.
        Runs perpetually in a daemon background thread, routing speech inputs
        safely into the intent execution pipeline.

        Speaking interruption protection: skips microphone capture while
        the TTS engine is actively speaking.
        """
        logger.info("Background Voice Recognition thread started successfully.")

        while self.is_running:
            if not self.voice_listening_enabled:
                time.sleep(0.3)
                continue

            # Phase 6: interruption protection — don't listen while speaking
            if self.speech.is_speaking:
                time.sleep(0.05)
                continue

            query = self.speech.listen(timeout=4, phrase_time_limit=7)

            if query:
                self.gui.append_dialog(f"YOU: {query}", is_user=True)
                # Run command processing on a worker thread so the voice loop
                # can immediately return to listening (no blocking)
                worker = threading.Thread(
                    target=self.process_command_intent,
                    args=(query,),
                    daemon=True
                )
                worker.start()

            # Throttle loop speed slightly to prevent CPU spikes
            time.sleep(0.05)

    def shutdown(self):
        """Performs a safe system shutdown, terminating threads and closing UI."""
        logger.info("Shutting down J.A.R.V.I.S. Core...")
        self.is_running = False
        self.root.destroy()
        sys.exit()

    def run(self):
        """Starts the graphical user interface main thread event loop."""
        logger.info("J.A.R.V.I.S. System active. Starting main UI frame...")
        self.root.mainloop()

if __name__ == "__main__":
    assistant = JarvisAssistant()
    assistant.run()