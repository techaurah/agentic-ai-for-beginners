# Lesson 00: Course setup

**Time:** about 20 minutes · **Difficulty:** Beginner · **Prerequisites:** none, this is the front door

Most people lose their first evening with a new course to setup: the wrong Python, a missing account, a paid tier they did not expect. This lesson exists so that never happens here. By the end of it your machine will be verified, you will know how this repo is organised, and you will know the one rule that makes every lesson in the course runnable: nothing here needs your money or your API keys to work.

## What do you actually need?

Three things: Python 3.11 or newer, a terminal, and a text editor you are comfortable in. That is the whole list. There is nothing to pip install for the core course, because the code is written against the Python standard library on purpose. If you already write code, your existing setup is almost certainly fine.

You do not need an API key. Lessons that would normally call a model run against a small fake client instead: a stand-in that behaves like a real API (messages in, text and usage counts out) with fixed, predictable replies. Every fake is labelled SIMULATION in the code, and every lesson shows you exactly where a real provider would plug in. If you later want to experiment with real keys, OpenAI, Anthropic, and Google all publish their own setup docs, and Google's Gemini API has a free tier. Do that after the foundations, not before.

## How is this course organised?

The course has 37 lessons, numbered 00 to 36, grouped into modules that run from foundations to a deployed business assistant. Each lesson folder holds the same four things: this README (the lesson itself), runnable code, an `exercise.md`, and a `solution/` folder with the worked solution. The numbering is the order: lessons assume the ones before them.

Work like this. Fork the repo so your copy is yours. Take the lessons in order. Run every code file yourself, do not just read it, because the output is where several lessons hide their point. Do the exercise before opening the solution; the solution is a worked answer to compare against, not a shortcut. Tick lessons off in `PROGRESS.md` as you finish them. If you want the community effect that makes people finish courses, post your progress publicly as you go. It costs nothing and it works.

## The worked example: prove your machine is ready

The file `check_environment.py` verifies the three things that matter: your Python version, the standard library modules the course uses (`json`, `re`, `sqlite3`, `dataclasses`, `urllib.request`), and, for information only, whether any common API keys happen to be set. Read the failure path too: a check that cannot fail is not a check, so the script returns a non-zero exit code when something is wrong, which is the same contract your own scripts should keep.

Run it:

```bash
cd 00-course-setup
python3 check_environment.py
```

Expected output (your Python version will differ, the shape will not):

```text
Agentic AI for Beginners - environment check
============================================
[OK] Python version: Python 3.12.3 (course needs 3.11 or newer)
[OK] Standard library: Standard library ready: json, re, sqlite3, dataclasses, urllib.request
[INFO] API keys: No API keys found. That is fine: every lesson runs offline with a fake client, and shows you where a real key would go.

Result: READY. You can start Lesson 01.
```

## Why this matters in production

Environment drift is the quiet killer of agent projects. The demo worked on your laptop, the deployment has an older Python, a missing environment variable, a folder the process cannot write to, and the failure surfaces three steps later as a mysterious model error. Professional teams fight this with exactly what you just ran: a small, explicit environment check that runs first and fails loudly. When we reach deployment (Lesson 27) and observability (Lesson 28), this script grows up into health checks and startup probes. The habit starts here, when it is cheap.

## Common failures

- **`python` works but `python3` does not, or the reverse.** On many Windows setups the command is `python`; on most Mac and Linux setups it is `python3`. Use whichever reports 3.11 or newer, consistently.
- **An old preinstalled Python.** Some systems ship Python 3.9 or older and it sits first on the path. The check catches this; install a current Python from python.org and rerun.
- **Stalling on API keys.** Learners regularly lose a week here. You need no key for this course. Move on.
- **Running later lessons from the wrong folder.** Several lessons read and write files relative to their own folder. Run each lesson's code from inside that lesson's folder, as the instructions show.

## Recap checklist

- [ ] I can state the three things the course needs, and the one thing it does not (an API key)
- [ ] `check_environment.py` prints READY on my machine
- [ ] I know the four parts of every lesson folder and how PROGRESS.md works
- [ ] I understand what the fake client is and why it exists

## Resources

- [Python downloads](https://www.python.org/downloads/): the current Python for your system
- [The Python Tutorial](https://docs.python.org/3/tutorial/): the official refresher if your Python is rusty
- [Visual Studio Code](https://code.visualstudio.com/): a free editor that handles this whole course comfortably
- [Google AI Studio](https://aistudio.google.com/): where the Gemini free tier lives, for later experiments
- [OpenAI Platform documentation](https://platform.openai.com/docs): the API documentation hub, bookmarked for Lesson 04
- [Anthropic documentation](https://docs.anthropic.com/): the Claude documentation hub, also for Lesson 04

**Next:** Lesson 01, what an AI agent actually is.
