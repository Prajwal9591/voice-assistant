import logging
import threading
import speech_recognition as sr
import pyttsx3

logger = logging.getLogger("Jarvis.SpeechEngine")

class SpeechEngine:
    def __init__(self, voice_gender="female", speech_rate=175, volume=1.0, on_state_change=None):
        """
        Initializes the Speech Engine with TTS and STT capabilities.
        
        :param voice_gender: "male" or "female"
        :param speech_rate: Speed of speech (default 175)
        :param volume: Volume level between 0.0 and 1.0
        :param on_state_change: Callback function(state_name) to report state transitions (e.g., "idle", "listening", "speaking")
        """
        self.voice_gender = voice_gender
        self.speech_rate = speech_rate
        self.volume = volume
        self.on_state_change = on_state_change
        self._tts_lock = threading.Lock()
        self.is_speaking = False
        
        # Initialize recognizer
        self.recognizer = sr.Recognizer()
        # Adjust recognizer settings for background noise
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.energy_threshold = 300
        
        # Initialize TTS Engine
        self.engine = None
        self._init_tts()

    def _init_tts(self):
        try:
            self.engine = pyttsx3.init()
            self.set_voice(self.voice_gender)
            self.set_rate(self.speech_rate)
            self.set_volume(self.volume)
            logger.info("Text-to-Speech engine initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize pyttsx3 TTS engine: {e}. Falling back to console-only mode.")
            self.engine = None

    def _update_state(self, state):
        """Helper to invoke GUI and logging updates when status changes."""
        logger.debug(f"State transition: {state}")
        if self.on_state_change:
            try:
                self.on_state_change(state)
            except Exception as e:
                logger.error(f"Error calling state change callback: {e}")

    def set_voice(self, gender):
        if not self.engine:
            return
        try:
            self.voice_gender = gender
            voices = self.engine.getProperty('voices')
            if not voices:
                logger.warning("No TTS voices found on the system.")
                return
            
            # Map simple "male"/"female" to available voice models
            selected_voice = voices[0]  # default fallback
            gender_lower = gender.lower()
            
            for voice in voices:
                # Check voice attributes
                if hasattr(voice, 'gender') and voice.gender:
                    if gender_lower in str(voice.gender).lower():
                        selected_voice = voice
                        break
                elif gender_lower == "female" and "zira" in voice.name.lower():
                    selected_voice = voice
                    break
                elif gender_lower == "male" and "david" in voice.name.lower():
                    selected_voice = voice
                    break
            
            self.engine.setProperty('voice', selected_voice.id)
            logger.info(f"TTS voice set to: {selected_voice.name}")
        except Exception as e:
            logger.error(f"Error setting TTS voice: {e}")

    def set_rate(self, rate):
        if not self.engine:
            return
        try:
            self.speech_rate = rate
            self.engine.setProperty('rate', rate)
            logger.info(f"TTS speech rate set to: {rate}")
        except Exception as e:
            logger.error(f"Error setting TTS speech rate: {e}")

    def set_volume(self, volume):
        if not self.engine:
            return
        try:
            self.volume = max(0.0, min(1.0, volume))
            self.engine.setProperty('volume', self.volume)
            logger.info(f"TTS volume set to: {self.volume}")
        except Exception as e:
            logger.error(f"Error setting TTS volume: {e}")

    def speak(self, text: str):
        """
        Converts text to speech synchronously, using locks to ensure thread safety.
        Automatically sets speaking flag to prevent microphone loops.
        """
        print(f"[Jarvis]: {text}")
        logger.info(f"Speaking: {text}")
        self._update_state("speaking")
        self.is_speaking = True
        
        if not self.engine:
            self.is_speaking = False
            self._update_state("idle")
            return
            
        with self._tts_lock:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                logger.error(f"TTS Error during playback: {e}")
                self._init_tts()
            finally:
                self.is_speaking = False
                self._update_state("idle")

    def listen(self, timeout=4, phrase_time_limit=7) -> str:
        """
        Listens to microphone input and converts it to text using Google Speech Recognition.
        Includes confidence filtering, ambient noise calibration, timeout optimization,
        and automated microphone recovery.
        """
        # Interruption protection: do not capture while assistant is actively speaking
        if self.is_speaking:
            logger.debug("Speech engine is currently speaking. Bypassing voice capture loop.")
            return ""
            
        self._update_state("listening")
        logger.info("Microphone is active, listening for commands...")
        
        microphone_acquired = False
        retry_count = 2
        
        while retry_count > 0 and not microphone_acquired:
            try:
                with sr.Microphone() as source:
                    microphone_acquired = True
                    # Ambient Noise Calibration (optimized calibration length for fast response)
                    logger.debug("Calibrating microphone for ambient noise...")
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    
                    # Listen to audio with optimal timeouts
                    audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                    
                    self._update_state("thinking")
                    logger.info("Processing voice input...")
                    
                    # Speech recognition with Google Speech API
                    query = self.recognizer.recognize_google(audio)
                    query = query.strip().lower()
                    
                    # Simple confidence filter: ignore extremely short/gibberish queries
                    if len(query) < 2:
                        self._update_state("idle")
                        return ""
                        
                    logger.info(f"Speech Recognized: '{query}'")
                    return query
                    
            except sr.WaitTimeoutError:
                logger.debug("Listening timed out. No speech detected.")
                self._update_state("idle")
                return ""
            except sr.UnknownValueError:
                logger.warning("Speech recognition engine could not understand the audio.")
                self._update_state("idle")
                return ""
            except sr.RequestError as e:
                logger.error(f"Speech recognition service request error: {e}")
                self._update_state("idle")
                return ""
            except OSError as e:
                logger.error(f"Microphone access error: {e}. Retrying recovery...")
                retry_count -= 1
                import time
                time.sleep(0.5)
            except Exception as e:
                logger.error(f"Unexpected error in speech input: {e}")
                self._update_state("idle")
                return ""
                
        self._update_state("idle")
        return ""
