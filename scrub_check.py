"""Pre-commit guard: fail if any tracked file contains a blocked term or an email/phone pattern.

Put your own blocked terms (employer name, vendor names, product names) one per line in
.blocklist.local, which is gitignored so the terms themselves never get published.
Run:  python scrub_check.py
"""
import pathlib
import re
import sys

root = pathlib.Path(__file__).parent
terms = []
bl = root / ".blocklist.local"
if bl.exists():
    terms = [t.strip().lower() for t in bl.read_text().splitlines() if t.strip()]
else:
    print("warning: no .blocklist.local found, only pattern checks will run")
patterns = {"email": re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"), "phone": re.compile(r"\+?\d[\d\s().-]{9,}\d")}
bad = 0
for p in root.rglob("*"):
    if not p.is_file() or ".git" in p.parts or p.name in {".blocklist.local", "scrub_check.py"} or p.suffix in {".png", ".zip"}:
        continue
    text = p.read_text(errors="ignore")
    low = text.lower()
    for t in terms:
        if t in low:
            print(f"BLOCKED TERM '{t}' in {p.relative_to(root)}"); bad += 1
    if p.suffix != ".csv":
        for name, rx in patterns.items():
            if rx.search(text):
                print(f"{name} pattern in {p.relative_to(root)}"); bad += 1
print("clean" if not bad else f"{bad} problem(s) found")
sys.exit(1 if bad else 0)
