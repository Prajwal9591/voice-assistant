import os
import glob
import subprocess
import logging

logger = logging.getLogger("Jarvis.Agent.ActionExecutor")

class ActionExecutor:
    def __init__(self, skill_system, automation_manager):
        self.skills = skill_system
        self.automation = automation_manager
        
    def execute_plan(self, plan: list, memory) -> list:
        """
        Executes the generated task plan step-by-step.
        Returns a list of step execution results.
        """
        results = []
        for step in plan:
            skill_name = step.get("skill")
            action = step.get("action")
            params = step.get("params", {})
            
            logger.info(f"Executing plan step: Skill={skill_name}, Action={action}, Params={params}")
            
            if skill_name in self.skills.skills:
                skill = self.skills.skills[skill_name]
                try:
                    result = skill.execute(action, params, memory, self.automation)
                    results.append({
                        "step": step,
                        "success": True,
                        "result": result
                    })
                except Exception as e:
                    logger.error(f"Error executing step {step}: {e}", exc_info=True)
                    results.append({
                        "step": step,
                        "success": False,
                        "error": str(e)
                    })
            elif action == "CONVERSATIONAL":
                results.append({
                    "step": step,
                    "success": True,
                    "result": "CONVERSATIONAL"
                })
            elif action == "EXIT":
                results.append({
                    "step": step,
                    "success": True,
                    "result": "TERMINATE"
                })
            else:
                logger.error(f"Skill '{skill_name}' is not registered in the system.")
                results.append({
                    "step": step,
                    "success": False,
                    "error": f"Skill '{skill_name}' not found"
                })
                
        return results

    @staticmethod
    def discover_and_launch_app(app_name: str) -> bool:
        """
        Dynamic application discovery engine.
        Scans Windows Start Menu shortcuts and Program Files to resolve
        and launch any application by name, avoiding hardcoded paths.
        """
        app_name_lower = app_name.lower().strip()
        logger.info(f"Dynamic discovery starting for app: '{app_name}'")
        
        # 1. Scan Start Menu directories recursively
        start_menu_paths = [
            os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
            os.path.expandvars(r"%ALLUSERSPROFILE%\Microsoft\Windows\Start Menu\Programs")
        ]
        
        shortcuts = []
        for base_path in start_menu_paths:
            if os.path.exists(base_path):
                for root, dirs, files in os.walk(base_path):
                    for file in files:
                        if file.endswith(".lnk"):
                            shortcuts.append(os.path.join(root, file))
                            
        # Find matching shortcuts (case insensitive search)
        matched_shortcuts = []
        for shortcut in shortcuts:
            shortcut_name = os.path.basename(shortcut)[:-4].lower() # strip '.lnk'
            if app_name_lower in shortcut_name or shortcut_name in app_name_lower:
                matched_shortcuts.append((shortcut, len(shortcut_name)))
                
        if matched_shortcuts:
            # Sort by shortest shortcut name length to get closest match
            matched_shortcuts.sort(key=lambda x: x[1])
            best_shortcut = matched_shortcuts[0][0]
            logger.info(f"App discovered in Start Menu shortcuts: '{best_shortcut}'")
            try:
                os.startfile(best_shortcut)
                return True
            except Exception as e:
                logger.error(f"Failed to launch shortcut '{best_shortcut}': {e}")
                
        # 2. Check standard executable installation directories
        search_dirs = [
            os.path.expandvars(r"%ProgramFiles%"),
            os.path.expandvars(r"%ProgramFiles(x86)%"),
            os.path.expandvars(r"%LOCALAPPDATA%\Programs")
        ]
        
        matched_exes = []
        for search_dir in search_dirs:
            if os.path.exists(search_dir):
                # Search folders matching the app name
                for folder in os.listdir(search_dir):
                    if app_name_lower in folder.lower():
                        folder_path = os.path.join(search_dir, folder)
                        if os.path.isdir(folder_path):
                            for root, dirs, files in os.walk(folder_path):
                                for file in files:
                                    if file.endswith(".exe") and app_name_lower in file.lower():
                                        matched_exes.append(os.path.join(root, file))
                                        
        if matched_exes:
            best_exe = matched_exes[0]
            logger.info(f"App discovered in program installations: '{best_exe}'")
            try:
                subprocess.Popen(best_exe)
                return True
            except Exception as e:
                logger.error(f"Failed to launch discovered executable '{best_exe}': {e}")
                
        # 3. Check System32 system utility binaries
        system32_path = os.path.expandvars(r"%SystemRoot%\System32")
        if os.path.exists(system32_path):
            app_map = {
                "notepad": "notepad.exe",
                "calculator": "calc.exe",
                "calc": "calc.exe",
                "cmd": "cmd.exe",
                "command prompt": "cmd.exe",
                "explorer": "explorer.exe",
                "file explorer": "explorer.exe",
                "paint": "mspaint.exe",
                "mspaint": "mspaint.exe",
                "task manager": "taskmgr.exe",
                "taskmgr": "taskmgr.exe"
            }
            for key, binary in app_map.items():
                if app_name_lower == key or app_name_lower in key:
                    binary_path = os.path.join(system32_path, binary)
                    if os.path.exists(binary_path):
                        try:
                            subprocess.Popen(binary_path)
                            return True
                        except Exception as e:
                            logger.error(f"Failed to launch System32 utility '{binary_path}': {e}")
                            
        return False
