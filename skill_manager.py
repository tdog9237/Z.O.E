"""
Z.O.E Skill Manager: Dynamic Plugin Loader and Router
======================================================
This manager automatically scans the 'skills/' folder, loads all
student-authored capabilities, and routes user questions to the right skill.
"""

import os
import sys
import inspect
import importlib
import importlib.util
import traceback
from typing import List, Dict, Any, Optional, Tuple
from skills.base_skill import BaseSkill


class SkillManager:
    """
    Manages the lifecycle, discovery, and execution of Z.O.E capabilities.
    """
    def __init__(self, skills_dir: Optional[str] = None):
        if skills_dir is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            skills_dir = os.path.join(base_dir, "skills")
            
        self.skills_dir = skills_dir
        self.skills: List[BaseSkill] = []
        self.load_skills()

    def load_skills(self) -> None:
        """
        Discovers and instantiates all BaseSkill subclasses in the skills directory.
        """
        self.skills = []
        if not os.path.exists(self.skills_dir):
            print(f"[SKILLS] Skills directory not found: {self.skills_dir}")
            return

        print(f"[SKILLS] Scanning for skills in: {self.skills_dir}")
        for item in sorted(os.listdir(self.skills_dir)):
            if item.endswith(".py") and not item.startswith("__") and item != "base_skill.py":
                module_name = item[:-3]
                file_path = os.path.join(self.skills_dir, item)
                self._load_module(module_name, file_path)

        print(f"[SKILLS] Total loaded capabilities: {len(self.skills)}")

    def _load_module(self, module_name: str, file_path: str) -> None:
        """
        Dynamically imports a single python file and registers any BaseSkill subclasses.
        """
        try:
            spec = importlib.util.spec_from_file_location(f"skills.{module_name}", file_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[f"skills.{module_name}"] = module
                spec.loader.exec_module(module)

                # Find classes inheriting from BaseSkill
                for _, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, BaseSkill) and obj is not BaseSkill:
                        try:
                            instance = obj()
                            self.skills.append(instance)
                            print(f"[SKILLS] Loaded capability: '{instance.name}' (v{instance.version}) by {instance.author}")
                        except Exception as e:
                            print(f"[SKILLS] Failed to instantiate skill class '{obj.__name__}': {e}")
        except Exception as e:
            print(f"[SKILLS] Error loading skill file '{file_path}': {e}")
            traceback.print_exc()

    def route_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> Optional[Tuple[BaseSkill, str]]:
        """
        Checks all registered skills to see if any skill can handle the message.
        If a matching skill is found, it executes the skill safely and returns (skill, reply).
        
        Args:
            message (str): The user's input.
            context (dict, optional): Optional context (e.g. user_name).
            
        Returns:
            Tuple[BaseSkill, str] or None: The handling skill and its generated response.
        """
        if not message:
            return None

        for skill in self.skills:
            try:
                if skill.can_handle(message):
                    print(f"[SKILLS] Routing message to capability: '{skill.name}'")
                    reply = skill.execute(message, context=context)
                    if reply and str(reply).strip():
                        return skill, str(reply).strip()
            except Exception as e:
                print(f"[SKILLS] Error executing capability '{skill.name}': {e}")
                traceback.print_exc()
                # Return a safe friendly message instead of crashing
                return skill, f"I attempted to execute '{skill.name}', but encountered an issue: {e}"

        return None

    def list_skills(self) -> List[Dict[str, Any]]:
        """
        Returns serializable metadata about all active skills.
        Useful for the UI and grading verification.
        """
        return [
            {
                "name": skill.name,
                "description": skill.description,
                "triggers": skill.triggers,
                "author": skill.author,
                "version": skill.version,
                "class_name": skill.__class__.__name__
            }
            for skill in self.skills
        ]

    def reload(self) -> None:
        """Hot-reloads all skills without restarting the application server."""
        self.load_skills()
