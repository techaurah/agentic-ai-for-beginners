# Lesson 00: Solution notes

Run it:

```bash
python3 check_environment_extended.py
```

Expected output: the two original checks, then `[OK] Writable folder` and `[OK] UTF-8 text`, then the [INFO] line and a READY verdict.

**What changed and why.** The extended script keeps the original structure (a list of check functions, one loop, one verdict) and adds two functions in the same shape. `check_writable_folder` writes a file named `.course_setup_probe.tmp`, then deletes it in the same breath; a lesson that cannot save state should fail here, at setup, not in Lesson 15. `check_utf8` round-trips the string "Café Müller – 50 € – done ✓" through an encode and decode and compares, because silent character corruption is miserable to debug inside a model's reply three lessons later.

**What to notice.** Each check returns the same `(ok, detail)` pair, so the reporting loop never changed. That sameness is the design lesson: when every check has one shape, adding the fifth check is as easy as adding the second. The stretch goal (a git check) fits the same pattern as [INFO], like the API key report, present but never blocking.
