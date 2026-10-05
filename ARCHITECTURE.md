# Z.O.E. Architecture & Capabilities Guide

Welcome to the Z.O.E. underlying architecture guide. This document explains how the different parts of Z.O.E. fit together and provides a starter guide on how you can expand her capabilities.

## System Architecture Overview

Z.O.E. is designed to be a simple, modular, and extremely fast local AI assistant, optimized for student development and execution within a local WSL environment.

The system is broken down into three main components:

### 1. The Core Server (`zoe_server.py`)
This is the brain of the operation. It is a lightweight Python web server (using Flask) that:
- Connects to the local **Ollama** instance to process LLM (Large Language Model) inference.
- Manages Z.O.E.'s persistent system prompt (her core identity).
- Hosts a dynamic **Skill Registry** that loads independent modular Python scripts from the `skills/` folder.
- Pre-warms the AI model into memory upon startup to ensure blisteringly fast first-token response times.

### 2. The Skills Module (`skills/` directory)
Instead of putting all the logic into one giant file, Z.O.E. uses a modular **Skill System**.
- Each Python file in the `skills/` directory (e.g., `weather_skill.py`) inherits from a `BaseSkill` class.
- The server dynamically discovers these skills at startup.
- When the user asks a question, the server can route the request to a specific skill to fetch real-world data, perform actions, or augment the response.

### 3. The User Interface (`zoe_ui/index.html`)
The front-end is designed to be a native web app running locally:
- **WebRTC Neural Avatar Engine**: Seamlessly streams a photorealistic 3D avatar and real-time lip-synced audio from the `avtr-1` streaming server.
- **JSON-POST endpoints**: Communicates with the core server over simple HTTP APIs (`/chat`, `/api/skills`, `/register_face`).

---

## Expanding Z.O.E.'s Capabilities

A major part of this project involves creating new "Skills" for Z.O.E.

### How to Create a New Skill

1. Navigate to the `skills/` folder.
2. Create a new Python file (e.g., `store_locator_skill.py`).
3. Inherit from the `BaseSkill` class.

Here is a starter template for a new skill:

```python
from base_skill import BaseSkill

class StoreLocatorSkill(BaseSkill):
    def __init__(self):
        # Define the skill's name and description so Z.O.E. knows when to use it
        super().__init__(
            name="StoreLocator",
            description="Finds the nearest retail store locations based on a given city or postcode."
        )

    def execute(self, user_input, context):
        # 1. Parse the user_input to find the location
        location = self.extract_location(user_input)
        
        if not location:
            return "I need a city or postcode to find a store for you."
            
        # 2. Fetch the data (e.g., call a mock database or an external API)
        store_data = self.mock_database_lookup(location)
        
        # 3. Return the response to be spoken by Z.O.E.
        if store_data:
            return f"I found a store in {location} at {store_data['address']}."
        else:
            return f"I'm sorry, I couldn't find any stores near {location}."
            
    def extract_location(self, text):
        # Simple placeholder for extracting a location from text
        return "London" # Replace with real logic
        
    def mock_database_lookup(self, location):
        # Simple placeholder for a database lookup
        stores = {"London": {"address": "123 Oxford Street"}}
        return stores.get(location)
```

### Registering Your Skill

You don't need to manually register the skill! Once you save your file in the `skills/` directory and restart `zoe_server.py`, the system will automatically parse and load it into the Skill Registry.

## Developer Workflow (GitFlow)

Remember to follow the GitFlow methodology when adding new skills:
1. Ensure you are on the `develop` branch.
2. Create a new feature branch for your skill: `git checkout -b feature/store-locator`
3. Write, test, and commit your skill code.
4. Merge your feature branch back into `develop` once completed.
