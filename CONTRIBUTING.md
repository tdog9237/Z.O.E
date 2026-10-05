# How to Add a Skill to Z.O.E

A **skill** is one Python file in the `skills/` folder that teaches Z.O.E to do one new thing.
Z.O.E finds skills automatically – you never need to edit `zoe_server.py`.

## 1. Every skill has the same shape

```python
from typing import Dict, Any, Optional
from .base_skill import BaseSkill


class JokeSkill(BaseSkill):
    name = "Joke Teller"                       # shown in the ⚡ Skills list
    description = "Tells a short, clean joke."  # plain English
    triggers = ["tell me a joke", "joke"]       # words that switch the skill on
    author = "Alex Smith (12345678)"
    version = "1.0.0"

    def execute(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        return "Why did the computer go to the doctor? It had a virus!"
```

| Part | Meaning |
|---|---|
| `class JokeSkill(BaseSkill)` | Your skill "inherits" from `BaseSkill`, so Z.O.E knows how to use it. |
| `triggers` | If any of these words appear in the user's message, your skill answers. |
| `can_handle(message)` | *(optional)* Write your own rule for when the skill should answer. |
| `execute(message, context)` | Does the work and **returns the text Z.O.E will say**. |
| `context["user_name"]` | The name of the person Z.O.E recognised on camera (or `None`). |

## 2. Rules

1. One skill per file, saved in `skills/`, file name ending `_skill.py`.
2. Do **not** edit `base_skill.py`, `skill_manager.py` or `zoe_server.py` unless your tutor agrees.
3. Return short, friendly sentences with **no emojis** (they sound strange when spoken).
4. Never crash: if something might fail (internet, bad input), use `try` / `except` and return a helpful message.
5. Never put passwords or API keys in your code. Use a `.env` file (it is ignored by Git).
6. Add a docstring (a short description in `"""triple quotes"""`) to your class and methods.
7. Watch your trigger words – very common words like `"is"` will steal messages from other skills.

## 3. Add a test for your skill

Open `test_skills.py` and add a test method to the `TestZoeSkills` class:

```python
    def test_joke_skill(self):
        """Joke skill answers when asked for a joke."""
        result = self.manager.route_message("tell me a joke")
        self.assertIsNotNone(result)
        skill, reply = result
        self.assertEqual(skill.name, "Joke Teller")
        self.assertTrue(len(reply) > 0)
```

Run all tests:
```bash
python3 test_skills.py
```
Every test must pass (`OK`) before you open a Pull Request.

## 4. Try it live

1. `bash start.sh` and open http://localhost:5001
2. Click **⚡ Skills** – your skill should be listed. If you edited it while Z.O.E was running, click **🔄 Hot Reload**.
3. Type one of your trigger phrases. Under Z.O.E's reply it will say `Skill: <your skill name>`.

## 5. Ideas for skills

- Timer or reminder ("remind me in 5 minutes")
- Revision quiz on a topic from your course
- Unit converter for more units (kg ↔ lb, £ ↔ €)
- Extend Project ORIS: cancel an order, list products under a price, opening hours by day
- Dice roller / random name picker
- Daily motivational quote
- Word definitions or spelling checker

## 6. Before you open a Pull Request – checklist

- [ ] I am on my own `feature/...` branch (check with `git status`)
- [ ] `python3 test_skills.py` says `OK`
- [ ] I added at least one test for my skill
- [ ] My skill shows in **⚡ Skills** and answers in the browser
- [ ] My commit messages explain what I changed
- [ ] The Pull Request goes into **`develop`**
