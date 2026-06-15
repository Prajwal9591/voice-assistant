import random
import logging
import datetime

logger = logging.getLogger("Jarvis.ResponseManager")

class ResponseManager:
    def __init__(self):
        # 1. Conversational Intent Mapping with rich random variations
        self.conversational_templates = {
            "hello": [
                "Greetings, sir. I am fully operational and ready for your commands.",
                "Hello, sir. How may I assist you today?",
                "Welcome back, sir. Systems are at your disposal.",
                "Good to hear from you, sir. What is our next objective?"
            ],
            "good_morning": [
                "Good morning, sir. All core grids are active and operating at peak capacity.",
                "Good morning, sir. I trust you slept well. Standing by for instructions.",
                "A very good morning to you, sir. Ready to assist in today's workspace."
            ],
            "good_afternoon": [
                "Good afternoon, sir. Tactical arrays are online and fully synced.",
                "Good afternoon, sir. How is your project progression coming along?",
                "Greetings, sir. Standing by to assist you this afternoon."
            ],
            "good_evening": [
                "Good evening, sir. Power margins are steady. Ready for evening operations.",
                "Good evening, sir. I am here to help you conclude today's tasks.",
                "A pleasant evening, sir. Standing by for your directives."
            ],
            "how_are_you": [
                "I am operating at optimal efficiency, sir. All power grids are fully nominal.",
                "Core processor temperature is stable at thirty-eight degrees Celsius. Thank you for asking, sir.",
                "My cognitive matrix is functioning perfectly, sir. Ready to streamline your productivity.",
                "All diagnostics are green, sir. Ready to assist."
            ],
            "thank_you": [
                "Always at your service, sir.",
                "The pleasure is entirely mine, sir.",
                "No need to thank me, sir. It is what I was programmed to do.",
                "Any time, sir. Glad I could assist."
            ],
            "goodbye": [
                "Goodbye, sir. Deactivating cognitive arrays and going into standby mode.",
                "Very well, sir. Powering down local systems. Have a pleasant evening.",
                "Understood, sir. Systems are transitioning to hibernation. Goodbye."
            ]
        }

        # 2. Contextual Templates for Automation Confirmation
        self.contextual_templates = {
            "open_youtube": [
                "Opening YouTube for you, sir. Emitting browser portal.",
                "Accessing YouTube databases, sir. Launching player.",
                "Opening YouTube. Enjoy your video stream, sir."
            ],
            "open_google": [
                "Launching Google Search gateway, sir.",
                "Opening Google main page. Ready for queries.",
                "Accessing the Google index. Browser portal loaded."
            ],
            "open_spotify": [
                "Initializing Spotify, sir. Directing audio stream.",
                "Launching Spotify. Preparing sound system, sir.",
                "Accessing Spotify archives. Let there be music."
            ],
            "open_vscode": [
                "Launching Visual Studio Code. Initializing developmental workspace, sir.",
                "Booting Visual Studio Code, sir. Preparing compile modules.",
                "Accessing VS Code workspaces, sir. Happy coding."
            ],
            "open_chrome": [
                "Opening Google Chrome browser, sir.",
                "Launching Google Chrome portal. Standing by.",
                "Initializing Chrome navigation layer."
            ],
            "open_folder": [
                "Opening folder directories, sir. Accessing explorer pathways.",
                "Launching system explorer, sir. Opening directory.",
                "Folder access granted. Emitting window."
            ],
            "search_google": [
                "Searching Google for '{query}', sir.",
                "Querying Google index. Fetching responses for '{query}'.",
                "Searching the web for '{query}', sir."
            ],
            "search_youtube": [
                "Searching YouTube database for '{query}', sir.",
                "Querying YouTube archives. Fetching video streams for '{query}'.",
                "Searching YouTube for your request, sir."
            ],
            "take_screenshot": [
                "Capturing screen buffers, sir. Image file saved.",
                "Taking system screenshot. Snapshot recorded in storage.",
                "Screenshot captured and stored successfully, sir."
            ],
            "create_note": [
                "Saving note to technical log files, sir.",
                "Recording notes in your local notes archive.",
                "Note documented successfully, sir."
            ],
            "volume_control": [
                "Adjusting system mixer levels, sir.",
                "Modifying audio margins, sir. Done.",
                "Volume level successfully configured, sir."
            ],
            "get_time": [
                "Current temporal coordinates are {time}, sir.",
                "It is exactly {time}, sir.",
                "The clock reads {time}, sir."
            ],
            "get_date": [
                "Today's calendar coordinate is {date}, sir.",
                "The date reads {date}, sir.",
                "Today is {date}, sir."
            ],
            "get_joke": [
                "Accessing joke logs, sir. Prepare for humor.",
                "A quick laugh, sir. Here it is.",
                "Retrieving humorous dialogue, sir."
            ],
            "system_shutdown": [
                "Initiating complete system shutdown sequence, sir. You have sixty seconds to abort.",
                "Powering off the terminal mainframe. System shutdown will execute in one minute, sir.",
                "Mainframe shutdown triggered. Standby for complete system termination in sixty seconds, sir."
            ],
            "system_restart": [
                "Initiating system reboot sequence. Restarting mainframe in sixty seconds, sir.",
                "Reboot sequence triggered. The terminal will restart in one minute, sir.",
                "System reboot initiated. Mainframe recycling in sixty seconds, sir."
            ],
            "abort_shutdown": [
                "Shutdown sequence aborted. All system power levels stabilized, sir.",
                "System termination sequence cancelled. Mains power active, sir.",
                "Reboot sequence successfully aborted, sir. Standing by."
            ],
            "launch_app": [
                "Launching application '{app_name}' for you, sir.",
                "Starting process for '{app_name}', sir.",
                "Accessing '{app_name}' executable pathways."
            ],
            "open_generic_website": [
                "Loading webpage URL for '{site_name}', sir.",
                "Opening the browser gateway to '{site_name}', sir.",
                "Accessing site '{site_name}'."
            ]
        }

        # 3. Intelligent fallback templates when Gemini AI is offline
        self.fallback_templates = [
            "My online synapses are offline, sir. However, I believe that relates to a web search topic.",
            "I could not formulate an advanced AI response offline, sir. Please configure Gemini API key to expand my intellect.",
            "I have recorded your request. However, to provide a highly conversational explanation, a Gemini API link is recommended, sir."
        ]

    def get_greeting(self, command_text: str) -> str:
        """Determines if the command is a greeting and returns a professional variation."""
        cmd = command_text.lower().strip()
        if "good morning" in cmd:
            return random.choice(self.conversational_templates["good_morning"])
        if "good afternoon" in cmd:
            return random.choice(self.conversational_templates["good_afternoon"])
        if "good evening" in cmd:
            return random.choice(self.conversational_templates["good_evening"])
        if any(w in cmd for w in ["hello", "greetings", "hi", "hey"]):
            return random.choice(self.conversational_templates["hello"])
        if "how are you" in cmd or "status check" in cmd:
            return random.choice(self.conversational_templates["how_are_you"])
        if any(w in cmd for w in ["thank you", "thanks", "appreciate"]):
            return random.choice(self.conversational_templates["thank_you"])
        if any(w == cmd for w in ["exit", "quit", "close", "goodbye", "terminate"]):
            return random.choice(self.conversational_templates["goodbye"])
        return ""

    def get_contextual_response(self, context_key: str, **kwargs) -> str:
        """Fetches a randomized response based on the contextual key, formatting with arguments if present."""
        if context_key not in self.contextual_templates:
            return "Task completed, sir."
        template = random.choice(self.contextual_templates[context_key])
        try:
            return template.format(**kwargs)
        except Exception:
            return template
            
    def get_fallback(self) -> str:
        """Fetches a random intelligent offline fallback explanation."""
        return random.choice(self.fallback_templates)
