# GitFlow Guide for the Z.O.E Project

**GitFlow** is a simple set of rules for using Git **branches**.
A branch is a separate copy of the code where you can work safely without breaking anything else.
Following GitFlow means your tutor can open GitHub and see exactly what you built, when, and why.

---

## The branches

| Branch | What it is for | Who changes it |
|---|---|---|
| `main` | The finished, working version. Only tested releases go here. | Only via a **release** |
| `develop` | Where finished features are collected and tested together. | Only via a **Pull Request** |
| `feature/...` | One branch **per skill** you build. This is where you do your work. | You |
| `release/...` | Getting a version ready to go into `main`. | You (end of project) |
| `hotfix/...` | An urgent fix to something already in `main`. | You (only if needed) |

```
main     ●──────────────────────────────●  v1.1.0
          \                            /
develop    ●────●───────────●─────────●
                 \         / \       /
feature/...       ●──●──●─●   ●──●──●
```

**Golden rule: never commit directly to `main` or `develop`.** Always work on a `feature/` branch.

---

## Building a skill, step by step

Run all of these in the Ubuntu window, inside the `zoe-ai` folder.

### 1. Start from the latest `develop`
```bash
git checkout develop
git pull
```

### 2. Create your feature branch
Name it `feature/<your-first-name>-<what-the-skill-does>` – lower case, hyphens, no spaces.
```bash
git checkout -b feature/alex-joke-teller develop
```

### 3. Write your skill and commit often
A **commit** is a saved snapshot with a short message. Small, frequent commits show your tutor how your work developed.
```bash
cp skills/student_template_skill.py skills/joke_skill.py
# ...edit the file...
python3 test_skills.py          # tests must say OK
git add skills/joke_skill.py
git commit -m "Add joke skill with trigger words"
```

Good commit messages say **what** changed:
- ✅ `Add order cancellation to ORIS skill`
- ✅ `Fix crash when user types an empty number`
- ❌ `stuff`  ❌ `update`  ❌ `asdf`

### 4. Push your branch to GitHub
**Push** means upload your commits to GitHub.
```bash
git push -u origin feature/alex-joke-teller
```
(After the first time, `git push` is enough.)

### 5. Open a Pull Request into `develop`
A **Pull Request** (PR) asks for your branch to be merged into `develop`. It is where your tutor reviews and comments.

1. Go to your fork on GitHub – a yellow **Compare & pull request** button appears.
2. Set **base** to `develop` (not `main`!) and **compare** to your feature branch.
3. Fill in the template (what the skill does, how you tested it).
4. Click **Create pull request**.

GitHub will automatically run `test_skills.py` on your PR (this is called **GitHub Actions** – a free service that runs your tests in the cloud). A green ✔ means your tests passed.

### 6. Respond to feedback, then merge
If your tutor leaves comments, make the changes on the same branch, commit and push again – the PR updates by itself.
When approved, click **Merge pull request**, then tidy up:
```bash
git checkout develop
git pull
git branch -d feature/alex-joke-teller
```

Then start the next skill from step 1.

---

## Making a release (end of the project)

When `develop` has all your finished skills:
```bash
git checkout develop
git pull
git checkout -b release/1.1.0
# update version numbers / README if needed, commit
git push -u origin release/1.1.0
```
Open a PR from `release/1.1.0` into **`main`**. After it is merged:
```bash
git checkout main
git pull
git tag -a v1.1.0 -m "Release 1.1.0 - new skills: jokes, timers"
git push origin v1.1.0
```
Finally open a PR from `main` back into `develop` so both are the same.

## Hotfixes (only if something in `main` is broken)
```bash
git checkout -b hotfix/fix-weather-crash main
# fix, commit, push, open PR into main; then merge main back into develop
```

---

## What your tutor can see

| On GitHub | Shows |
|---|---|
| **Insights → Network** | A picture of all your branches and merges |
| **Branches** | Every `feature/` branch you created |
| **Pull requests** | Each skill, its description, test results and review comments |
| **Commits** | Every snapshot, its message and the date |

So: **branch per skill, commit often with clear messages, merge through Pull Requests.**

## Quick reference

| I want to... | Command |
|---|---|
| See which branch I'm on | `git status` |
| See all branches | `git branch -a` |
| Switch branch | `git checkout develop` |
| Start a new skill | `git checkout -b feature/name-skill develop` |
| Save my work | `git add .` then `git commit -m "message"` |
| Upload my work | `git push` |
| Get the latest develop | `git checkout develop` then `git pull` |
| See history as a graph | `git log --oneline --graph --all` |
