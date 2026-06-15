import re
import logging

logger = logging.getLogger("Jarvis.ConversationManager")

class ConversationManager:
    """
    Coordinates session dialogue turns, analyzes user emotional state,
    and structures multi-turn contextual history.
    """
    def __init__(self, ai_engine):
        self.ai = ai_engine
        self.history = []  # List of {"user": "...", "assistant": "...", "emotion": "..."}
        self.max_history_turns = 12

    def analyze_emotional_state(self, prompt: str) -> str:
        """Lightweight offline rule-based sentiment/emotional analysis."""
        prompt_clean = prompt.lower().strip()
        
        emotional_indicators = {
            "tired": ["tired", "exhausted", "sleepy", "drained", "burn out"],
            "stressed": ["stressed", "anxious", "worried", "nervous", "overwhelmed"],
            "sad": ["sad", "depressed", "down", "unhappy", "lonely"],
            "happy": ["happy", "excited", "awesome", "great", "excellent", "glad"],
            "angry": ["angry", "mad", "frustrated", "annoyed", "pissed"]
        }
        
        for emotion, keywords in emotional_indicators.items():
            if any(kw in prompt_clean for kw in keywords):
                logger.info(f"Emotional context detected: '{emotion.upper()}'")
                return emotion
                
        return "neutral"

    def process_turn(self, query: str, active_app: str = None, active_web: str = None) -> str:
        """
        Processes a single conversational turn.
        Analyzes emotion, manages dialogue history, and fetches memory-augmented responses.
        """
        # 1. Emotional analysis
        emotion = self.analyze_emotional_state(query)
        
        # 2. Generate response from the advanced AI Engine
        response = self.ai.generate_response(
            query,
            conversation_history=self.history,
            active_app=active_app,
            active_web=active_web
        )
        
        # Proactive emotional dialogue augmentation if in offline/fallback state
        if emotion == "tired" and not self.ai.use_gemini:
            response = "You've been working exceptionally hard today, sir. " + response + " Might I suggest taking a brief break or listening to some relaxing music?"
        elif emotion == "stressed" and not self.ai.use_gemini:
            response = "Take a calm, deep breath, sir. " + response + " I am fully online to handle your system automations."
            
        # 3. Add to sliding dialog history
        self.history.append({
            "user": query,
            "assistant": response,
            "emotion": emotion
        })
        
        # Trim history to fit context limits
        if len(self.history) > self.max_history_turns:
            self.history.pop(0)
            
        return response
