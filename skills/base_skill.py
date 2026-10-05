"""
Z.O.E Capability Expansion Framework: Base Skill
==================================================

In software development, modular design means breaking a large project into
small, independent, and reusable pieces called 'skills' or 'plugins'.

Every capability you build for Z.O.E must inherit from this BaseSkill class.
This ensures Z.O.E knows:
1. What your capability is called (name).
2. What it does (description).
3. Which words or phrases activate it (triggers).
4. How to process the user's request and respond (execute).
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class BaseSkill(ABC):
    """
    Abstract Base Class for all Z.O.E Skills.
    
    Attributes:
        name (str): The human-readable name of your capability.
        description (str): A plain English explanation of what this skill does.
        triggers (List[str]): Keywords or key phrases that activate this skill.
        author (str): Student name or GitHub username.
        version (str): Semantic version of the skill (e.g. '1.0.0').
    """
    name: str = "Base Skill"
    description: str = "Abstract foundation for custom capabilities"
    triggers: List[str] = []
    author: str = "Student Developer"
    version: str = "1.0.0"

    def can_handle(self, message: str) -> bool:
        """
        Determines if this skill can handle the incoming user message.
        
        Default behavior: Checks if any keyword in `self.triggers` appears
        inside the user message (case-insensitive).
        
        Students can override this method if they want more complex matching
        (such as regular expressions or intent analysis).
        
        Args:
            message (str): The raw text message sent by the user.
            
        Returns:
            bool: True if this skill should respond, False otherwise.
        """
        if not message:
            return False
            
        msg_lower = message.lower().strip()
        for trigger in self.triggers:
            if trigger.lower() in msg_lower:
                return True
        return False

    @abstractmethod
    def execute(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Executes the skill's logic and returns Z.O.E's response.
        
        Args:
            message (str): The full message sent by the user.
            context (dict, optional): Extra information provided by Z.O.E,
                                     such as recognized face name or chat history.
                                     
        Returns:
            str: A natural, friendly response string that Z.O.E will speak
                 aloud and display in the chat window.
        """
        pass
