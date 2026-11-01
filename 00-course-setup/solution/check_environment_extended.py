"""
Lesson 00 - Exercise solution: the extended environment check.

Adds two checks to the original script:
1. The folder you run the course from is writable (later lessons save
   files: memory stores, eval reports, workflow exports).
2. Your system can encode and decode UTF-8 text (agent traffic is full
   of names, currencies, and punctuation from many languages).

Run it with:

    python3 check_environment_extended.py
"""

import os
import sys

MINIMUM = (3, 11)
TITLE = "Agentic AI for Beginners - extended environment check"


def check_python_version():
    version = sys.version_info
    label = f"{version.major}.{version.minor}.{version.micro}"
    ok = (version.major, version.minor) >= MINIMUM
    return ok, f"Python {label} (course needs 3.11 or newer)"


def check_stdlib():
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


def check_writable_folder():
    """Write a small test file into the current folder, then remove it."""
    probe = ".course_setup_probe.tmp"
    try:
        with open(probe, "w", encoding="utf-8") as handle:
            handle.write("ok")
        os.remove(probe)
        return True, "Current folder is writable (later lessons save files here)"
    except OSError as error:
        return False, f"Current folder is not writable: {error}"


def check_utf8():
    """Round-trip a string with accents, currency, and a check mark."""
    sample = "Café Müller – 50 € – done ✓"
    try:
        return sample.encode("utf-8").decode("utf-8") == sample, \
            "UTF-8 encode/decode round-trip works"
    except UnicodeError as error:
        return False, f"UTF-8 round-trip failed: {error}"


def check_api_keys():
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
        ("Writable folder", check_writable_folder),
        ("UTF-8 text", check_utf8),
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
