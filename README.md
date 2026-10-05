# Z.O.E – Student Edition

Z.O.E (say "Zoe") is a friendly AI assistant that runs **entirely on your own computer**.
She can chat, speak out loud, recognise your face through your webcam, and answer questions
using small add-ons called **skills**.

**Your project is to give Z.O.E new skills.** You will build each skill on its own Git branch
using **GitFlow**, so your tutor can follow your progress on GitHub.

---

## What you need

| Thing | What it is | Why you need it |
|---|---|---|
| **Windows 10/11** | Your operating system | The setup below is written for Windows |
| **WSL** (Windows Subsystem for Linux) | A way to run Linux (Ubuntu) inside Windows | Z.O.E's install and start scripts are Linux scripts |
| **Git** | A tool that saves snapshots ("commits") of your code and shares them | You use it to send your work to GitHub |
| **GitHub account** | A website that stores Git projects online | Your tutor reviews your branches and Pull Requests here |
| **Ollama** | A free program that runs AI models on your own computer | It runs Z.O.E's "brain" – the install script sets it up for you |
| **Chrome or Edge** | Web browser | Z.O.E's screen is a web page; these browsers support the microphone and voice |

About 8 GB of RAM and 6 GB of free disk space is recommended. A dedicated graphics card is **highly recommended** (or required) for running the local AI model smoothly.

---

## Step 1 – Install WSL (one time only)

1. Click Start, type **PowerShell**, right-click it and choose **Run as administrator**.
2. Type this and press Enter:
   ```powershell
   wsl --install -d Ubuntu
   ```
3. **Restart your computer** when asked.
4. After the restart an **Ubuntu** window opens. Choose a username and password
   (the password does not show as you type – that is normal). Remember it.

From now on, every command in this guide is typed into the **Ubuntu** window
(open it from the Start menu by typing "Ubuntu").

## Step 2 – Get your own copy of the project

Your tutor will give you the link to the Z.O.E repository ("repo" = a project folder stored by Git).

1. On GitHub, click **Fork** (top right) to make your own copy under your account.
2. In your fork, go to **Settings → Collaborators → Add people** and add your tutor's GitHub username,
   so they can see and comment on your work.
3. In the Ubuntu window, tell Git who you are (one time only):
   ```bash
   git config --global user.name "Your Full Name"
   git config --global user.email "the-email-you-use-on-github@example.com"
   ```
4. Download ("clone") your fork. Replace `YOUR-USERNAME` with your GitHub username:
   ```bash
   cd ~
   git clone https://github.com/YOUR-USERNAME/zoe-ai.git
   cd zoe-ai
   git checkout develop
   ```

## Step 3 – Install Z.O.E (one time only)

```bash
bash install.sh
```

This script:
1. installs Python and other basic tools,
2. installs **Ollama** and downloads Z.O.E's small, fast AI model (a few GB – be patient),
3. creates a **virtual environment** (`.venv`) – a private folder of Python libraries just for this project,
4. runs the automated tests to check everything works.

You should finish with `OK` from the tests and **"All done!"**.

## Step 4 – Start Z.O.E

```bash
bash start.sh
```

Then open **http://localhost:5001** in Chrome or Edge on Windows.

- Type a message, or hold the 🎤 button and speak.
- Allow camera and microphone access when the browser asks.
- Click **👤 Register Face** so Z.O.E recognises you next time.
- Click **⚡ Skills** to see every skill Z.O.E has loaded – yours will appear here.

Press **Ctrl + C** in the Ubuntu window to stop Z.O.E.

Try these to see the built-in skills working:
- `what is 12 * 7?`
- `convert 20 celsius to fahrenheit`
- `track order ORIS-1002`
- `what is the weather in Cardiff?`

---

## How Z.O.E works (the short version)

```
You type/speak ──► zoe_server.py ──► SkillManager checks every skill in skills/
                                        │
                     a skill matches? ──┤── yes ─► the skill answers
                                        │
                                        └── no ──► the local AI model (Ollama) answers
                                                   ▼
                              reply shown in chat + spoken aloud (Edge-TTS)
```

| File / folder | What it does |
|---|---|
| `zoe_server.py` | The web server ("Flask" – a Python library for building websites). Receives your messages and sends replies. |
| `skill_manager.py` | Finds every skill in `skills/` automatically and picks the right one for each message. |
| `skills/` | **Where your work goes.** One Python file per skill. |
| `skills/base_skill.py` | The pattern every skill must follow. Do not change this file. |
| `skills/student_template_skill.py` | A ready-made starting point – copy it to make a new skill. |
| `test_skills.py` | Automated tests. Run them before every commit. |
| `zoe_ui/` | The web page you see in the browser. |
| `data/` | Face-recognition files. Your registered face is stored here and is **never** uploaded to GitHub. |

**Edge-TTS** is a free text-to-speech library that turns Z.O.E's replies into a natural voice.
**OpenCV** is a computer-vision library used to find and recognise faces in the webcam picture.

---

## Your project

1. Read **[GITFLOW_GUIDE.md](GITFLOW_GUIDE.md)** – how to use branches so your tutor can see your progress.
2. Read **[CONTRIBUTING.md](CONTRIBUTING.md)** – how to write and test a new skill.

## Common problems

| Problem | Fix |
|---|---|
| `Local Ollama is not running` | Run `ollama serve &` in Ubuntu, then try again. |
| `ollama: command not found` | Run `bash install.sh` again. |
| Z.O.E does not speak | Click anywhere on the page once (browsers block sound until you click), and check 🔊 Voice is on. |
| Camera not showing | Allow camera access in the browser's address bar. Close other apps using the camera (Teams, Zoom). |
| My new skill does not appear | Check the file is in `skills/`, ends in `.py`, and the class inherits from `BaseSkill`. Click **⚡ Skills → 🔄 Hot Reload**. |
| `bash: install.sh: No such file` | You are in the wrong folder. Run `cd ~/zoe-ai`. |
| See which model is loaded | Run `ollama ps` – it lists models currently held in memory. |
