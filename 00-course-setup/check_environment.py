"""
Lesson 00 - Course setup: check your environment.

Run it with:

    python3 check_environment.py

The whole course uses only the Python standard library, so if this
check passes, your machine can run every lesson. No API key is needed:
lessons that would normally call a model run offline against a small
fake client instead, and show you exactly where a real key would go.
"""

import os
import sys

MINIMUM = (3, 11)
TITLE = "Agentic AI for Beginners - environment check"


def check_python_version():
    """The course needs Python 3.11 or newer."""
    version = sys.version_info
    label = f"{version.major}.{version.minor}.{version.micro}"
    ok = (version.major, version.minor) >= MINIMUM
    return ok, f"Python {label} (course needs 3.11 or newer)"


def check_stdlib():
    """Every module the course relies on ships with Python itself."""
    modules = ["json", "re", "sqlite3", "dataclasses", "urllib.request"]
    missing = []
    for name in modules:
        try:
            __import__(name)
        except ImportError:
            missing.append(name)
    if missing:
        return False, "Missing standard library modules: " + ", ".join(missing)
    return True, "Standard library ready: " + ", ".join(modules)


def check_api_keys():
    """Keys are optional in this course. This only reports what exists."""
    keys = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY"]
    found = [name for name in keys if os.environ.get(name)]
    if found:
        return "Found API keys: " + ", ".join(found)
    return (
        "No API keys found. That is fine: every lesson runs offline "
        "with a fake client, and shows you where a real key would go."
    )


def main():
    print(TITLE)
    print("=" * len(TITLE))
    all_ok = True
    checks = [
        ("Python version", check_python_version),
        ("Standard library", check_stdlib),
    ]
    for label, check in checks:
        ok, detail = check()
        all_ok = all_ok and ok
        print(f"[{'OK' if ok else 'FAIL'}] {label}: {detail}")
    print(f"[INFO] API keys: {check_api_keys()}")
    print()
    if all_ok:
        print("Result: READY. You can start Lesson 01.")
        return 0
    print("Result: NOT READY. Fix the FAIL lines above, then run this check again.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
