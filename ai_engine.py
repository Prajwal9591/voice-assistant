import os
import re
import logging
import random
import wikipedia
import dotenv

# Load .env file securely on start
dotenv.load_dotenv(dotenv_path=r"c:\Users\Prajwal HY\Voice_assistant\.env")

# Try to import modern Google GenAI SDK
try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False
    logger = logging.getLogger("Jarvis.AIEngine")
    logger.warning("google.genai package is not available. Falling back to offline conversational engine.")

from conversation_memory import ConversationMemory
from rag_system import RAGSystem
from personality_manager import PersonalityManager
from agent.local_knowledge import LocalKnowledge

logger = logging.getLogger("Jarvis.AIEngine")

class AIEngine:
    """
    Upgraded J.A.R.V.I.S. Brain. Migrated to google.genai SDK.
    Integrates RAG vector retrieval, local persistent profile memory, 
    and Personality Guidelines.
    """
    def __init__(self):
        # Initialize sub-components
        self.memory = ConversationMemory()
        self.rag = RAGSystem()
        self.personality = PersonalityManager()
        self.local_knowledge = LocalKnowledge()
        
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.use_gemini = HAS_GENAI and self.api_key is not None
        self.client = None
        
        if self.use_gemini:
            self._configure_genai()
        else:
            logger.warning("GEMINI_API_KEY not found or GenAI package not available. Running in Offline Conversational mode.")

    def _configure_genai(self):
        try:
            # Modern google-genai initialization
            self.client = genai.Client(api_key=self.api_key)
            logger.info("Modern Google GenAI client successfully configured.")
        except Exception as e:
            logger.error(f"Failed to configure GenAI client: {e}. Defaulting to offline conversational engine.")
            self.use_gemini = False

    def harvest_facts(self, prompt: str):
        """
        Parses user query and dynamically harvests facts, notes, reminders,
        and interest declarations, persisting them in ConversationMemory and RAG.
        """
        prompt_clean = prompt.lower().strip()
        user_name = self.memory.get_user_name()
        
        # 1. Harvest User Name
        name_match = re.search(r"\bmy name is ([a-zA-Z0-9_\s]+)\b", prompt_clean)
        if name_match:
            new_name = name_match.group(1).title().strip()
            self.memory.set_user_name(new_name)
            self.rag.add_memory(f"User's name is {new_name}.", "profile")
            return
            
        # 2. Harvest Favorites/Preferences
        fav_match = re.search(r"\bmy favorite (app|website|color|movie|language|interest|game) is (.+)\b", prompt_clean)
        if fav_match:
            fav_type = fav_match.group(1).strip()
            fav_val = fav_match.group(2).strip()
            fact_text = f"User mentioned their favorite {fav_type} is {fav_val}."
            self.memory.add_fact(fact_text)
            self.rag.add_memory(fact_text, "preference")
            
            # Categorize specific lists
            if fav_type == "app":
                self.memory.add_favorite_app(fav_val)
            elif fav_type == "interest":
                self.memory.add_interest(fav_val)
            return

        # 3. Harvest General Declarative facts (Remember that X)
        remember_match = re.search(r"\bremember that (.+)\b", prompt_clean)
        if remember_match:
            fact = remember_match.group(1).strip()
            fact_text = f"User noted: {fact}"
            self.memory.add_fact(fact_text)
            self.rag.add_memory(fact_text, "fact")
            return
            
        # 4. Note recording
        note_match = re.search(r"\b(create note saying|write note saying|note down) (.+)\b", prompt_clean)
        if note_match:
            note = note_match.group(2).strip()
            self.rag.add_memory(f"Saved note: {note}", "note")
            return
            
        # 5. Reminders
        reminder_match = re.search(r"\bremind me to (.+)\b", prompt_clean)
        if reminder_match:
            reminder = reminder_match.group(1).strip()
            self.rag.add_memory(f"Reminder alert: {reminder}", "reminder")

    def generate_response(self, prompt: str, conversation_history: list = None, active_app: str = None, active_web: str = None) -> str:
        """
        Generates a conversational response utilizing Local Knowledge,
        semantic RAG memory, session history, and modern Google Gemini SDK.
        """
        logger.info(f"Generating modern conversational response for: '{prompt}'")
        
        prompt_clean = prompt.strip()
        if not prompt_clean:
            return "Always operational, sir. How can I assist?"
            
        # 1. Harvest any important declarative details dynamically
        self.harvest_facts(prompt_clean)
        
        # 2. Local Knowledge Base matching (Fast smalltalk bypass)
        user_name = self.memory.get_user_name()
        lk_match = self.local_knowledge.match(prompt_clean, user_name)
        if lk_match:
            logger.info("Local Knowledge matched conversational banter.")
            return lk_match

        # 3. RAG Semantic Retrieval
        retrieved_memories = self.rag.retrieve(prompt_clean, top_n=3)
        
        # 4. MODERN ONLINE GENERATION (GOOGLE GENAI CLIENT)
        if self.use_gemini and self.client is not None:
            try:
                # Compile prompt context
                rag_context = "\n".join([f"- {item}" for item in retrieved_memories])
                profile_context = self.memory.get_profile_context()
                
                history_context = ""
                if conversation_history:
                    for turn in conversation_history[-6:]:
                        history_context += f"User: {turn.get('user')}\nJARVIS: {turn.get('assistant')}\n"
                
                system_instruction = self.personality.get_system_prompt(user_name)
                
                full_prompt = f"""
System Focus:
Active Application Context: '{active_app or "None"}'
Active Website Context: '{active_web or "None"}'

User Profile & Identity Context:
{profile_context}

Relevant Memories Retained from RAG:
{rag_context or "- None"}

Recent Dialogue Turns:
{history_context or "None."}
User: {prompt_clean}
JARVIS:"""
                
                # Execute Modern GenAI Call
                response = self.client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=full_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        max_output_tokens=180,
                        temperature=0.75
                    )
                )
                return response.text.strip()
            except Exception as e:
                logger.error(f"GenAI call failed: {e}. Defaulting to local conversational RAG.")
                # Fall through to offline conversational logic

        # 5. OFFLINE CONVERSATIONAL RAG & EMULATOR (Zero robotic warnings!)
        # If RAG returned facts and the user query is probing facts
        if retrieved_memories and any(w in prompt_clean.lower() for w in ["what", "who", "remember", "note", "reminder", "preference", "like"]):
            best_memory = retrieved_memories[0]
            # Strip tags for conversational layout
            best_memory_clean = best_memory.replace("User noted: ", "").replace("Saved note: ", "").replace("Reminder alert: ", "")
            
            witty_offline_statements = [
                f"Scanning memory bank, sir. I recall that {best_memory_clean.lower()}.",
                f"If my cognitive registers are correct, {best_memory_clean.lower()}, sir.",
                f"Ah, yes. According to our log history, {best_memory_clean.lower()}.",
                f"Local databases state that {best_memory_clean.lower()}, sir."
            ]
            return random.choice(witty_offline_statements)
            
        # Standard Wikipedia lookups offline
        if any(w in prompt_clean.lower() for w in ["who is", "what is", "where is", "tell me about"]):
            search_query = prompt_clean
            for word in ["who is", "what is", "where is", "tell me about", "wikipedia", "search"]:
                search_query = re.sub(rf"\b{word}\b", "", search_query, flags=re.IGNORECASE)
            search_query = search_query.strip()
            try:
                summary = wikipedia.summary(search_query, sentences=2)
                return f"According to online archives, sir: {summary}"
            except Exception:
                pass
                
        # Emulated calm conversation
        return self.personality.get_natural_fallback()
