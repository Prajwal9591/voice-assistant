# 🤖 J.A.R.V.I.S. — AI Voice Assistant

> **Just A Rather Very Intelligent System** — A modular, conversational AI voice assistant built in Python, powered by Google Gemini 2.5 Flash, with persistent memory, RAG-based recall, and full Windows automation.

---

## ✨ Features

### 🧠 Conversational Intelligence
- **Google Gemini 2.5 Flash** — LLM-powered natural language responses with personality
- **RAG Memory System** — Semantic retrieval of past facts, notes, reminders, and user preferences
- **Persistent User Profile** — Remembers your name, favorite apps, interests, and key facts across sessions
- **Multi-turn Dialogue** — Maintains conversation context across multiple exchanges
- **Offline Fallback** — Wikipedia lookups and local knowledge base when Gemini is unavailable

### 🎙️ Voice Interface
- **Continuous Voice Recognition** — Always-on microphone loop via `SpeechRecognition`
- **Natural TTS Output** — Text-to-speech playback using `pyttsx3` with adjustable rate, volume, and voice gender
- **Interruption Protection** — Microphone pauses while JARVIS is speaking to prevent feedback loops

### ⚙️ Windows Automation
| Category | Commands |
|---|---|
| **Web** | Google Search, YouTube search/play, open websites (YouTube, GitHub, Spotify, Reddit, etc.) |
| **Apps** | Launch Chrome, Spotify, VS Code, Notepad, Calculator, File Explorer, Task Manager |
| **System** | Volume up/down/mute, screenshot, shutdown, restart, abort shutdown |
| **Files** | Create timestamped notes, open user folders (Downloads, Desktop, Documents, etc.) |
| **Info** | Current time, today's date, jokes |

### 🖥️ GUI
- **CustomTkinter UI** — Premium dark-themed desktop interface
- **Live Dialogue Feed** — Real-time display of user commands and JARVIS responses
- **Live Log Panel** — Shows system events and module activity
- **Settings Panel** — Adjust TTS voice, speech rate, and volume from the UI
- **Voice Toggle** — Enable/disable microphone from the interface

---

## 📁 Project Structure

```
Voice_assistant/
├── main.py                    # Entry point — wires all modules together
├── gui.py                     # CustomTkinter GUI
├── ai_engine.py               # Gemini AI + RAG + personality brain
├── speech_engine.py           # Voice recognition & TTS
├── automation.py              # Windows automation commands
├── command_handler.py         # Routes commands to agent or automation
├── conversation_manager.py    # Multi-turn dialogue manager
├── conversation_memory.py     # Persistent user profile & session memory
├── rag_system.py              # Semantic vector search (sentence-transformers)
├── personality_manager.py     # Personality prompts & fallback responses
├── response_manager.py        # Contextual response templates
│
├── agent/                     # Cognitive pipeline
│   ├── intent_detector.py     # Classifies user intent
│   ├── entity_extractor.py    # Extracts entities (app names, URLs, etc.)
│   ├── task_planner.py        # Plans multi-step action sequences
│   ├── action_executor.py     # Executes planned actions
│   ├── context_memory.py      # Short-term session context
│   ├── user_memory.py         # Long-term user profile persistence
│   ├── rag_memory.py          # RAG memory integration
│   ├── local_knowledge.py     # Offline knowledge base
│   ├── skill_system.py        # Skill routing layer
│   └── response_generator.py  # Formats final responses
│
├── skills/                    # Modular skill handlers
│   ├── web_skill.py           # Web search & browsing skills
│   ├── app_launcher_skill.py  # Application launch skills
│   ├── system_skill.py        # System control skills
│   └── communication_skill.py # Communication skills
│
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variable template
└── .gitignore                 # Git ignore rules
```

---

## 🚀 Getting Started

### Prerequisites
- Python **3.10+**
- Windows OS (automation commands are Windows-specific)
- A working microphone
- A [Google Gemini API Key](https://aistudio.google.com/app/apikey) (free tier available)

### 1. Clone the Repository

```bash
git clone https://github.com/Prajwal9591/voice-assistant.git
cd voice-assistant
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Your API Key

```bash
# Copy the example env file
copy .env.example .env
```

Then open `.env` and add your key:

```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

### 5. Run JARVIS

```bash
python main.py
```

The GUI will open and JARVIS will greet you within a second.

---

## 🗣️ Example Voice Commands

```
"What time is it?"
"Open YouTube"
"Play Blinding Lights on YouTube"
"Search Google for Python tutorials"
"Open VS Code"
"Open Spotify"
"Take a screenshot"
"Volume up"
"Mute the volume"
"Tell me a joke"
"My name is Prajwal"
"My favorite language is Python"
"Remember that I have a meeting at 5 PM"
"What do you remember about me?"
"Open my Downloads folder"
"Create a note saying buy groceries tomorrow"
"Shutdown the computer"
"What is machine learning?"
"Goodbye" / "Exit" / "Quit"
```

---

## ⚙️ Configuration

### TTS Settings
Adjust voice settings in `main.py` or through the GUI:

```python
self.speech = SpeechEngine(
    voice_gender="female",   # "male" or "female"
    speech_rate=175,         # Words per minute
    volume=1.0               # 0.0 to 1.0
)
```

### Offline Mode
JARVIS works without an API key — it falls back to:
- Local knowledge base for common queries
- Wikipedia for factual lookups
- RAG semantic memory for personal facts

---

## 🧩 Architecture Overview

```
Voice Input
    │
    ▼
SpeechEngine (listen)
    │
    ▼
CommandHandler
    ├── JarvisAgent (cognitive pipeline)
    │       ├── IntentDetector  →  classify intent
    │       ├── EntityExtractor →  extract params
    │       ├── TaskPlanner     →  build action plan
    │       └── ActionExecutor  →  run automation / skills
    │
    └── ConversationManager (fallback)
            └── AIEngine (Gemini 2.5 Flash + RAG)
                    ├── RAGSystem       →  semantic memory retrieval
                    ├── ConversationMemory →  user profile
                    └── PersonalityManager →  response style
    │
    ▼
SpeechEngine (speak) + GUI update
```

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `customtkinter` | Premium dark-theme GUI framework |
| `speechrecognition` | Microphone voice-to-text |
| `pyttsx3` | Text-to-speech engine |
| `google-genai` | Google Gemini 2.5 Flash API |
| `sentence-transformers` | Local semantic embeddings for RAG |
| `wikipedia` | Offline factual lookups |
| `pywhatkit` | YouTube playback automation |
| `pyjokes` | Joke generation |
| `pillow` | Screenshot capture |
| `python-dotenv` | Secure `.env` loading |

---

## 🔒 Security

- **Never commit your `.env` file** — it is listed in `.gitignore`
- Use `.env.example` as a template (contains only placeholder values)
- Rotate your API key immediately if it is ever accidentally exposed
- `memory_store/` and `vector_store/` are excluded from version control as they may contain personal data

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<p align="center">Built with ❤️ by <a href="https://github.com/Prajwal9591">Prajwal HY</a></p>
