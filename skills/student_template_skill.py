"""
Student Skill Template for Z.O.E.
==================================

STUDENT INSTRUCTIONS:
--------------------
1. Create your feature branch using GitFlow:
      git checkout -b feature/<your-name>-<capability-name> develop
      (Example: git checkout -b feature/alex-todo-manager develop)

2. Copy this template file to a new file in the skills/ folder:
      cp skills/student_template_skill.py skills/my_new_skill.py

3. Rename the class (e.g. MyNewSkill), fill in your metadata:
      - name: A descriptive title for your capability
      - description: What your skill does in plain English
      - triggers: Keywords that activate your skill
      - author: Your full name or Student ID
      - version: '1.0.0'

4. Implement your logic in can_handle() and execute().

5. Test your new skill by running:
      python3 test_skills.py

6. Commit your changes, push to GitHub, and open a Pull Request into develop!
"""

from typing import Dict, Any, Optional
from .base_skill import BaseSkill


class StudentTemplateSkill(BaseSkill):
    """
    Example template skill. Replace this docstring with a description
    of what your capability accomplishes.
    """
    name = "Student Template Capability"
    description = "Demonstration template showing how students create new capabilities for Z.O.E."
    triggers = [
        "template", "sample capability", "test skill"
    ]
    author = "Student Name (ID: 12345678)"
    version = "1.0.0"

    def can_handle(self, message: str) -> bool:
        """
        Check if the incoming user message should be answered by this skill.
        You can customize this logic, or keep the default trigger check.
        """
        msg = message.lower().strip()
        return any(trigger in msg for trigger in self.triggers)

    def execute(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Process the user message and return Z.O.E's voice response.
        
        Args:
            message (str): The raw text from the user.
            context (dict): Optional context provided by Z.O.E (e.g. user name).
            
        Returns:
            str: The message Z.O.E will speak and display.
        """
        user_name = context.get("user_name") if context else None
        greeting = f"Hi {user_name}! " if user_name else "Hi there! "

        # Your custom logic goes here:
        # e.g. query a database, perform calculations, look up data, etc.
        return (
            f"{greeting}This is a demonstration response from the Student Template Skill. "
            f"You successfully invoked this capability with your query: '{message}'."
        )
