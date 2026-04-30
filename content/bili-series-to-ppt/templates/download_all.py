"""Download m4a audio via curl (with retry+resume); validate duration via ffprobe.

Reads `audio_urls.json` at the project root. Each entry is:
  {"p": <int>, "t": <title>, "d": <duration_seconds>, "u": <primary_url>, "b": <backup_url>}

Skips files that already exist and pass duration check (allows resume after crash).
Run from any working dir; uses script's parents[1] as project root.
"""
from __future__ import annotations
import json, subprocess, pathlib, time

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "audio_urls.json").read_text(encoding="utf-8"))
AUDIO_DIR = ROOT / "audio"
AUDIO_DIR.mkdir(exist_ok=True)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"


def probe_duration(path: pathlib.Path) -> float | None:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True,
    )
    try:
        return float(r.stdout.strip())
    except Exception:
        return None


def download_one(url: str, out: pathlib.Path, expected_seconds: int) -> bool:
    out.unlink(missing_ok=True)
    cmd = [
        "curl", "-L", "--silent", "--show-error",
        "--retry", "5", "--retry-delay", "2", "--retry-all-errors",
        "--connect-timeout", "20", "--max-time", "600",
        "-A", UA,
        "-H", "Referer: https://www.bilibili.com/",
        "-o", str(out), url,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"        curl exit={r.returncode}: {r.stderr.strip()[:200]}", flush=True)
        return False
    if not out.exists() or out.stat().st_size < 1_000_000:
        print(f"        downloaded size too small: {out.stat().st_size if out.exists() else 0}", flush=True)
        return False
    dur = probe_duration(out)
    if dur is None or abs(dur - expected_seconds) > 5:
        print(f"        duration mismatch (got {dur}, expected {expected_seconds})", flush=True)
        return False
    print(f"        OK {out.stat().st_size//1024}KB  dur={dur:.0f}s", flush=True)
    return True


def main() -> None:
    failed = []
    for p in DATA:
        out = AUDIO_DIR / f"p{p['p']:02d}.m4a"
        if out.exists() and out.stat().st_size > 1_000_000:
            dur = probe_duration(out)
            if dur is not None and abs(dur - p["d"]) <= 5:
                print(f"[skip] P{p['p']:02d} already valid", flush=True)
                continue
        print(f"[dl  ] P{p['p']:02d} ({p['d']}s) {p['t'][:50]}", flush=True)
        success = False
        for attempt in range(1, 4):
            for key, label in (("u", "primary"), ("b", "backup")):
                url = p.get(key)
                if not url:
                    continue
                print(f"        attempt {attempt} via {label} mirror", flush=True)
                if download_one(url, out, p["d"]):
                    success = True
                    break
            if success:
                break
            time.sleep(1)
        if not success:
            print(f"        !! P{p['p']:02d} FAILED after retries", flush=True)
            failed.append(p["p"])
        time.sleep(0.4)
    if failed:
        print(f"DOWNLOAD DONE WITH FAILURES: {failed}", flush=True)
    else:
        print("DOWNLOAD ALL DONE", flush=True)


if __name__ == "__main__":
    main()
