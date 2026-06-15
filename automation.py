import os
import sys
import logging
import random
import datetime
import webbrowser
import subprocess

from response_manager import ResponseManager

logger = logging.getLogger("Jarvis.Automation")

# ── Optional dependency guards ────────────────────────────────────────────────
try:
    import pywhatkit
    HAS_PYWHATKIT = True
except ImportError:
    HAS_PYWHATKIT = False
    logger.warning("pywhatkit not installed. YouTube play will use direct browser links.")

try:
    import pyjokes
    HAS_PYJOKES = True
except ImportError:
    HAS_PYJOKES = False
    logger.warning("pyjokes not installed. Using offline joke archive instead.")

try:
    from PIL import ImageGrab
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    logger.warning("Pillow not installed. Screenshot command unavailable.")


class AutomationManager:
    def __init__(self):
        self.rm = ResponseManager()

        # Offline joke archive (fallback when pyjokes is unavailable)
        self.offline_jokes = [
            "Why do programmers wear glasses? Because they can't C sharp.",
            "There are only 10 types of people: those who understand binary, and those who don't.",
            "How many programmers does it take to change a light bulb? None — that is a hardware problem.",
            "A SQL query walks into a bar, walks up to two tables and asks: Can I join you?",
            "Why did the programmer quit his job? Because he did not get arrays.",
            "Debugging is like being the detective in a crime movie where you are also the murderer.",
        ]

    # ── TIME & DATE ───────────────────────────────────────────────────────────

    def get_time(self) -> str:
        """Returns the current system time with personality phrasing."""
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        return self.rm.get_contextual_response("get_time", time=current_time)

    def get_date(self) -> str:
        """Returns today's date with personality phrasing."""
        current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
        return self.rm.get_contextual_response("get_date", date=current_date)

    # ── HUMOR ─────────────────────────────────────────────────────────────────

    def get_joke(self) -> str:
        """Returns a joke from pyjokes or the offline cache."""
        intro = self.rm.get_contextual_response("get_joke")
        if HAS_PYJOKES:
            try:
                joke = pyjokes.get_joke()
            except Exception as e:
                logger.error(f"pyjokes fetch failed: {e}")
                joke = random.choice(self.offline_jokes)
        else:
            joke = random.choice(self.offline_jokes)
        return f"{intro} {joke}"

    # ── YOUTUBE ───────────────────────────────────────────────────────────────

    def play_youtube(self, query: str) -> str:
        """Plays a video on YouTube."""
        clean_query = re.sub(r"\bplay\b", "", query.lower()).strip()
        logger.info(f"Playing '{clean_query}' on YouTube.")

        if HAS_PYWHATKIT:
            try:
                pywhatkit.playonyt(clean_query)
                return self.rm.get_contextual_response("search_youtube", query=clean_query)
            except Exception as e:
                logger.error(f"pywhatkit play failed: {e}. Falling back.")

        url = f"https://www.youtube.com/results?search_query={clean_query.replace(' ', '+')}"
        webbrowser.open(url)
        return self.rm.get_contextual_response("search_youtube", query=clean_query)

    def search_youtube(self, query: str) -> str:
        """Searches YouTube in the default browser."""
        clean_query = query.lower()
        for term in ["search youtube for", "search youtube", "youtube search",
                     "search on youtube", "look up on youtube", "find on youtube"]:
            clean_query = clean_query.replace(term, "").strip()

        url = f"https://www.youtube.com/results?search_query={clean_query.replace(' ', '+')}"
        webbrowser.open(url)
        logger.info(f"Searched YouTube for: '{clean_query}'")
        return self.rm.get_contextual_response("search_youtube", query=clean_query)

    # ── WEBSITES & SEARCH ─────────────────────────────────────────────────────

    def open_website(self, name: str) -> str:
        """Opens common websites or any URL in the default browser."""
        site_map = {
            "youtube":       ("https://youtube.com",       "open_youtube"),
            "google":        ("https://google.com",        "open_google"),
            "github":        ("https://github.com",        "open_generic_website"),
            "stackoverflow": ("https://stackoverflow.com", "open_generic_website"),
            "reddit":        ("https://reddit.com",        "open_generic_website"),
            "wikipedia":     ("https://wikipedia.org",     "open_generic_website"),
            "spotify":       ("https://open.spotify.com",  "open_spotify"),
        }

        name_lower = name.lower().strip()
        for key, (url, ctx_key) in site_map.items():
            if key in name_lower:
                webbrowser.open(url)
                logger.info(f"Opened website: {url}")
                return self.rm.get_contextual_response(ctx_key, site_name=key.capitalize())

        # Raw domain (e.g. "open example.com")
        if "." in name_lower:
            url = f"https://{name_lower}" if not name_lower.startswith("http") else name_lower
            webbrowser.open(url)
            return self.rm.get_contextual_response("open_generic_website", site_name=name_lower)

        # Fall through to Google search
        return self.search_google(name)

    def search_google(self, query: str) -> str:
        """Submits a Google search in the default browser."""
        clean_query = query.lower()
        for word in ["search google for", "search google", "google search",
                     "search for", "google", "search"]:
            clean_query = clean_query.replace(word, "").strip()

        url = f"https://google.com/search?q={clean_query.replace(' ', '+')}"
        webbrowser.open(url)
        logger.info(f"Searching Google for: '{clean_query}'")
        return self.rm.get_contextual_response("search_google", query=clean_query)

    # ── APPLICATIONS ─────────────────────────────────────────────────────────

    def open_chrome(self) -> str:
        """Launches Google Chrome."""
        logger.info("Triggering open Chrome automation.")
        paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]
        for path in paths:
            if os.path.exists(path):
                try:
                    subprocess.Popen(path)
                    return self.rm.get_contextual_response("open_chrome")
                except Exception as e:
                    logger.error(f"Chrome path launch failed: {e}")

        try:
            subprocess.Popen("start chrome", shell=True)
            return self.rm.get_contextual_response("open_chrome")
        except Exception as e:
            logger.error(f"Chrome shell fallback failed: {e}")
            webbrowser.open("https://google.com")
            return "I could not locate a Chrome installation, sir. I have opened Google in your default browser."

    def open_spotify(self) -> str:
        """Launches the Spotify desktop app or falls back to web player."""
        logger.info("Triggering open Spotify automation.")
        try:
            subprocess.Popen("start spotify:", shell=True)
            return self.rm.get_contextual_response("open_spotify")
        except Exception as e:
            logger.warning(f"Spotify URI failed: {e}. Checking absolute paths.")

        paths = [
            os.path.expandvars(r"%APPDATA%\Spotify\Spotify.exe"),
            os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WindowsApps\Spotify.exe"),
        ]
        for path in paths:
            if os.path.exists(path):
                try:
                    subprocess.Popen(path)
                    return self.rm.get_contextual_response("open_spotify")
                except Exception as ex:
                    logger.error(f"Spotify absolute path failed: {ex}")

        webbrowser.open("https://open.spotify.com")
        return "I could not find a local Spotify installation, sir. Opening Spotify Web Player."

    def open_vscode(self) -> str:
        """Launches Visual Studio Code."""
        logger.info("Triggering open VS Code automation.")
        paths = [
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe"),
            r"C:\Program Files\Microsoft VS Code\Code.exe",
        ]
        for path in paths:
            if os.path.exists(path):
                try:
                    subprocess.Popen(path)
                    return self.rm.get_contextual_response("open_vscode")
                except Exception as e:
                    logger.error(f"VS Code path launch failed: {e}")

        try:
            subprocess.Popen("code", shell=True)
            return self.rm.get_contextual_response("open_vscode")
        except Exception as e:
            logger.error(f"VS Code shell fallback failed: {e}")
            return "I was unable to locate Visual Studio Code on your system, sir."

    def launch_app(self, app_name: str) -> str:
        """Launches a pre-configured local Windows application."""
        app_map = {
            "notepad":        "notepad.exe",
            "calculator":     "calc.exe",
            "cmd":            "cmd.exe",
            "command prompt": "cmd.exe",
            "explorer":       "explorer.exe",
            "file explorer":  "explorer.exe",
            "task manager":   "taskmgr.exe",
            "paint":          "mspaint.exe",
            "wordpad":        "wordpad.exe",
        }

        app_lower = app_name.lower()
        for key, binary in app_map.items():
            if key in app_lower:
                try:
                    subprocess.Popen(binary)
                    logger.info(f"Launched: {key}")
                    return self.rm.get_contextual_response("launch_app", app_name=key.capitalize())
                except Exception as e:
                    logger.error(f"Failed to launch {binary}: {e}")
                    return f"I encountered an error launching {key}, sir."

        return f"I have no configuration to launch '{app_name}', sir. Should I search for it?"

    # ── SYSTEM CONTROLS ───────────────────────────────────────────────────────

    def control_volume(self, action: str) -> str:
        """Adjusts system volume using PowerShell WScript.Shell SendKeys."""
        action_lower = action.lower()
        logger.info(f"Volume command: {action_lower}")

        try:
            if any(w in action_lower for w in ["up", "louder", "increase"]):
                cmd = "$wsh = New-Object -ComObject Wscript.Shell; $wsh.SendKeys([char]175)"
                for _ in range(5):
                    subprocess.run(["powershell", "-Command", cmd], capture_output=True)
                return self.rm.get_contextual_response("volume_control")

            elif any(w in action_lower for w in ["down", "quieter", "decrease", "lower"]):
                cmd = "$wsh = New-Object -ComObject Wscript.Shell; $wsh.SendKeys([char]174)"
                for _ in range(5):
                    subprocess.run(["powershell", "-Command", cmd], capture_output=True)
                return self.rm.get_contextual_response("volume_control")

            elif any(w in action_lower for w in ["mute", "unmute", "silence"]):
                cmd = "$wsh = New-Object -ComObject Wscript.Shell; $wsh.SendKeys([char]173)"
                subprocess.run(["powershell", "-Command", cmd], capture_output=True)
                return self.rm.get_contextual_response("volume_control")

        except Exception as e:
            logger.error(f"Volume control failed: {e}")

        return "I could not adjust the system audio levels, sir."

    def take_screenshot(self) -> str:
        """Captures a screenshot and saves it to the screenshots directory."""
        if not HAS_PIL:
            return "Screen capture module is unavailable, sir. Please install Pillow to enable this feature."

        try:
            save_dir = os.path.join(os.getcwd(), "screenshots")
            os.makedirs(save_dir, exist_ok=True)

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filepath = os.path.join(save_dir, f"screenshot_{timestamp}.png")

            screenshot = ImageGrab.grab()
            screenshot.save(filepath)
            logger.info(f"Screenshot saved to: {filepath}")
            os.system(f'start "" "{filepath}"')
            return self.rm.get_contextual_response("take_screenshot")
        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            return "I failed to capture the screenshot, sir. A system error occurred."

    def shutdown_system(self) -> str:
        """Initiates a 60-second safe shutdown with abort window."""
        try:
            subprocess.run(["shutdown", "/s", "/t", "60"])
            logger.warning("System shutdown initiated by voice command.")
            return self.rm.get_contextual_response("system_shutdown")
        except Exception as e:
            logger.error(f"Shutdown failed: {e}")
            return "I failed to initiate the shutdown sequence, sir. Administrative privilege may be required."

    def restart_system(self) -> str:
        """Initiates a 60-second safe restart with abort window."""
        try:
            subprocess.run(["shutdown", "/r", "/t", "60"])
            logger.warning("System restart initiated by voice command.")
            return self.rm.get_contextual_response("system_restart")
        except Exception as e:
            logger.error(f"Restart failed: {e}")
            return "I failed to initiate the restart sequence, sir. Administrative privilege may be required."

    def abort_shutdown(self) -> str:
        """Cancels any pending system shutdown or restart."""
        try:
            subprocess.run(["shutdown", "/a"])
            logger.info("Shutdown/restart aborted by user voice command.")
            return self.rm.get_contextual_response("abort_shutdown")
        except Exception as e:
            logger.error(f"Abort shutdown failed: {e}")
            return "I failed to abort the shutdown, sir. There may be no pending sequence active."

    # ── NOTES & FOLDERS ───────────────────────────────────────────────────────

    def create_note(self, content: str) -> str:
        """Appends a timestamped note to notes/notes.txt."""
        note_content = content.lower()
        for phrase in ["create note saying", "create a note saying", "create note",
                       "create a note", "write note", "make note", "note down", "save note"]:
            note_content = note_content.replace(phrase, "").strip()

        if not note_content:
            return "What would you like me to note down, sir?"

        try:
            notes_dir = os.path.join(os.getcwd(), "notes")
            os.makedirs(notes_dir, exist_ok=True)

            filepath = os.path.join(notes_dir, "notes.txt")
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(filepath, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {note_content}\n")

            logger.info(f"Note recorded: '{note_content}'")
            return self.rm.get_contextual_response("create_note")
        except Exception as e:
            logger.error(f"Note write failed: {e}")
            return "I encountered a write error trying to record your note, sir."

    def open_folder(self, folder_name: str) -> str:
        """Opens a named Windows user folder in Explorer."""
        folder_lower = folder_name.lower()
        paths = {
            "downloads":  os.path.expandvars(r"%USERPROFILE%\Downloads"),
            "documents":  os.path.expandvars(r"%USERPROFILE%\Documents"),
            "desktop":    os.path.expandvars(r"%USERPROFILE%\Desktop"),
            "pictures":   os.path.expandvars(r"%USERPROFILE%\Pictures"),
            "music":      os.path.expandvars(r"%USERPROFILE%\Music"),
            "videos":     os.path.expandvars(r"%USERPROFILE%\Videos"),
            "project":    os.getcwd(),
            "workspace":  os.getcwd(),
        }

        target_path = matched_key = None
        for key, path in paths.items():
            if key in folder_lower:
                target_path, matched_key = path, key
                break

        if not target_path:
            target_path = os.path.expandvars(r"%USERPROFILE%")
            matched_key = "user profile"

        try:
            if os.path.exists(target_path):
                os.system(f'explorer "{target_path}"')
                logger.info(f"Opened folder: {target_path}")
                return self.rm.get_contextual_response("open_folder")
            else:
                return f"I could not locate the {matched_key} directory on your system, sir."
        except Exception as e:
            logger.error(f"Explorer launch failed for {target_path}: {e}")
            return "I encountered an error launching Windows Explorer, sir."


# ── Module-level import fix for play_youtube (regex needed in method) ─────────
import re
