#!/usr/bin/env python3
"""ISKCON agent uniformity + copy-forward audit.

Usage:
  python3 -I agent_audit.py BASELINE.json OTHER1.json [OTHER2.json ...]

For each OTHER file it prints every leaf field whose value differs from BASELINE
(IDs/timestamps ignored), then scans every string in every file for copy-forward
markers and spoken ALL-CAPS tokens. Review C1 fields (see AGENT_QA_CHECKLIST.md)
by hand: any difference there fails unless the change log explains it.
"""
import json
import re
import sys

IGNORE_KEYS = re.compile(r"(^|_)(id|_id|uuid|createdAt|updatedAt|created_at|updated_at|version_id|organizationId|projectId)$", re.I)

FORBIDDEN = [
    r"diwali", r"deepavali", r"दीपावली", r"दिवाली", r"deep\s*daan", r"दीपदान",
    r"pitru", r"paksha", r"पितृ", r"janmashtami", r"जन्माष्टमी", r"ganesh",
    r"bal\s*gopal", r"tulsi", r"mahaprasad", r"प्रसादम्", r"-pp26", r"-diwali",
    r"hare\s+krishna",  # should be written हरे कृष्ण
]
CAPS = re.compile(r"\b[A-Z]{3,}\b")
CAPS_ALLOW = {"API", "JSON", "URL", "SMS", "RCS", "LLM", "TTS", "STT", "AMD", "IST", "UPI", "DND", "ROAS"}


def flatten(obj, prefix=""):
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            if IGNORE_KEYS.search(str(k)):
                continue
            out.update(flatten(v, f"{prefix}.{k}" if prefix else str(k)))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.update(flatten(v, f"{prefix}[{i}]"))
    else:
        out[prefix] = obj
    return out


def short(v, n=80):
    s = json.dumps(v, ensure_ascii=False)
    return s if len(s) <= n else s[: n - 3] + "..."


def scan(name, flat):
    hits = []
    for path, val in flat.items():
        if not isinstance(val, str):
            continue
        for pat in FORBIDDEN:
            for m in re.finditer(pat, val, re.I):
                hits.append((path, f"forbidden '{m.group(0)}'"))
        for m in CAPS.finditer(val):
            if m.group(0) not in CAPS_ALLOW:
                hits.append((path, f"ALL-CAPS '{m.group(0)}'"))
    print(f"\n## Copy-forward / casing scan: {name}")
    if not hits:
        print("  clean")
    for path, msg in hits:
        print(f"  {msg:30s} at {path}")


def main(paths):
    if len(paths) < 2:
        sys.exit(__doc__)
    loaded = {p: flatten(json.load(open(p, encoding="utf-8"))) for p in paths}
    base_path = paths[0]
    base = loaded[base_path]
    for p in paths[1:]:
        other = loaded[p]
        print(f"\n## Diff vs baseline: {p}  (baseline {base_path})")
        keys = sorted(set(base) | set(other))
        n = 0
        for k in keys:
            a, b = base.get(k, "<missing>"), other.get(k, "<missing>")
            if a != b:
                n += 1
                print(f"  {k}\n     base : {short(a)}\n     other: {short(b)}")
        print(f"  -> {n} differing fields")
    for p in paths:
        scan(p, loaded[p])


if __name__ == "__main__":
    main(sys.argv[1:])
