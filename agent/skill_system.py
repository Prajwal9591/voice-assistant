import os
import sys
import importlib.util
import logging

logger = logging.getLogger("Jarvis.Agent.SkillSystem")

class BaseSkill:
    """
    Base class for all Jarvis Skills.
    Skills define a set of intents they support, parameters expected, and execute actions.
    """
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        # Schema of supported intents:
        # {
        #    "INTENT_NAME": {
        #        "description": "What this intent does",
        #        "entities": {
        #            "EntityName": "Description of entity"
        #        },
        #        "examples": ["example phrase 1", "example phrase 2"]
        #    }
        # }
        self.intents = {}
        
    def execute(self, intent: str, entities: dict, memory, automation_manager) -> str:
        """
        Executes the specific intent with extracted entities.
        Returns a feedback string.
        """
        raise NotImplementedError("Skills must implement execute()")

class SkillSystem:
    def __init__(self, skills_dir=None):
        if skills_dir is None:
            skills_dir = os.path.join(os.getcwd(), "skills")
        self.skills_dir = skills_dir
        self.skills = {}
        self.intent_map = {}
        
        # Ensure directory exists
        os.makedirs(self.skills_dir, exist_ok=True)
        
    def load_skills(self):
        """Dynamically scans and loads all skill plugins from the skills/ directory."""
        logger.info(f"Scanning for voice capabilities under: '{self.skills_dir}'")
        self.skills.clear()
        self.intent_map.clear()
        
        # Search Python files
        for file in os.listdir(self.skills_dir):
            if file.endswith(".py") and not file.startswith("__"):
                skill_name = file[:-3]
                file_path = os.path.join(self.skills_dir, file)
                
                try:
                    # Python dynamic import
                    spec = importlib.util.spec_from_file_location(skill_name, file_path)
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[skill_name] = module
                    spec.loader.exec_module(module)
                    
                    # Find any subclass of BaseSkill
                    skill_class = None
                    for attribute_name in dir(module):
                        attribute = getattr(module, attribute_name)
                        if (isinstance(attribute, type) and 
                            issubclass(attribute, BaseSkill) and 
                            attribute is not BaseSkill):
                            skill_class = attribute
                            break
                            
                    if skill_class:
                        skill_instance = skill_class()
                        self.skills[skill_instance.name] = skill_instance
                        for intent in skill_instance.intents:
                            self.intent_map[intent] = skill_instance
                        logger.info(f"Plugin Loaded: '{skill_instance.name}' (supports {list(skill_instance.intents.keys())})")
                    else:
                        logger.warning(f"File {file} loaded but no subclass of BaseSkill found.")
                except Exception as e:
                    logger.error(f"Failed to load skill module '{file}': {e}", exc_info=True)
