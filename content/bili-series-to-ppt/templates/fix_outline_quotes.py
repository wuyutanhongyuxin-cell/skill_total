"""Fix unescaped ASCII double quotes inside JSON string values for outlines/p*.json.

The outline JSONs were written by a sub-agent. Some Chinese-language string values
embed ASCII " " around inner phrases (e.g. "做题时按"X→Y"顺序"), which produces
invalid JSON. This script replaces the inner ASCII double-quotes in any pure-string
array item / scalar value line with full-width corner brackets 「」 so the file
parses cleanly while preserving the visual quoting style.

Strategy: process file line-by-line. Treat as candidate any line that matches
`^\s*"(.*)"(\s*[,\]]?\s*)$` AND does NOT contain `:` between the opening and
first inner `"` (i.e. is not an object key/value line). For such lines, replace
inner unescaped `"` pairs with 「」.

Idempotent: files that already parse via json.loads are skipped.
"""
from __future__ import annotations
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "outlines"


def fix_text(text: str) -> str:
    lines = text.splitlines()
    fixed_lines = []
    for line in lines:
        new = try_fix_line(line)
        fixed_lines.append(new)
    return "\n".join(fixed_lines) + ("\n" if text.endswith("\n") else "")


def try_fix_line(line: str) -> str:
    # Match a string scalar line: optional indent, "..." content, optional comma/bracket
    m = re.match(r'^(\s*)"(.*)"(\s*[,\]]?\s*)$', line)
    if not m:
        return line
    ws, content, tail = m.groups()
    # If no inner ASCII quotes, fine
    if '"' not in content:
        return line
    # Skip object-key-with-string-value lines like "key": "value"
    # Heuristic: if content contains `": "` pattern, that's an object key→value
    # being read as one string via greedy matching. We won't touch these lines
    # because re-quoting them would corrupt structure.
    if re.search(r'":\s*"', content):
        return line
    # Replace inner unescaped " pairs with 「 / 」 alternately
    out = []
    open_left = True
    for ch in content:
        if ch == '"':
            out.append('「' if open_left else '」')
            open_left = not open_left
        else:
            out.append(ch)
    fixed = ''.join(out)
    return f'{ws}"{fixed}"{tail}'


def main() -> int:
    failures = []
    for p in sorted(OUT.glob("p*.json")):
        text = p.read_text(encoding="utf-8")
        try:
            json.loads(text)
            continue  # already valid
        except json.JSONDecodeError:
            pass
        new = fix_text(text)
        try:
            json.loads(new)
        except json.JSONDecodeError as e:
            failures.append((p.name, str(e)))
            continue
        p.write_text(new, encoding="utf-8")
        print(f"[fixed] {p.name}")
    if failures:
        print("=== STILL INVALID ===")
        for name, err in failures:
            print(f"  {name}: {err}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
