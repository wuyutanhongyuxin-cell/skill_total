"""Sequentially transcribe downloaded m4a files via bili2text (Whisper small CPU).

Usage:
    PYTHONIOENCODING=utf-8 python scripts/transcribe_all.py

Reads N from `audio_urls.json` (count of entries). Waits for each audio file to
appear (allows running concurrently with `download_all.py`). Writes per-file logs
to `logs/tx_pNN.log`.

PRECONDITION: bili2text/src/b2t/library.py:34 must be patched (see
templates/library_patch.diff). Without the patch, every transcript fails with
'NoneType' object has no attribute 'get' at the indexing step, even though
Whisper itself succeeds.
"""
from __future__ import annotations
import json, os, subprocess, pathlib, time

ROOT = pathlib.Path(__file__).resolve().parents[1]
AUDIO_DIR = ROOT / "audio"
LOGS_DIR = ROOT / "logs"
LOGS_DIR.mkdir(exist_ok=True)
B2T_PROJECT = ROOT / "bili2text"
DATA = json.loads((ROOT / "audio_urls.json").read_text(encoding="utf-8"))
TOTAL = len(DATA)


def wait_for_audio(p: int) -> pathlib.Path:
    f = AUDIO_DIR / f"p{p:02d}.m4a"
    while not (f.exists() and f.stat().st_size > 1_000_000):
        print(f"        ... waiting for {f.name}", flush=True)
        time.sleep(10)
    return f


def main() -> None:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    for i in range(1, TOTAL + 1):
        audio = wait_for_audio(i)
        log = LOGS_DIR / f"tx_p{i:02d}.log"
        print(f"[tx  ] P{i:02d} -> {audio.name}", flush=True)
        t0 = time.time()
        with log.open("w", encoding="utf-8") as f:
            r = subprocess.run(
                ["uv", "run", "--project", str(B2T_PROJECT),
                 "bili2text", "tx", str(audio.resolve())],
                cwd=str(B2T_PROJECT),
                stdout=f, stderr=subprocess.STDOUT, env=env,
            )
        dt = time.time() - t0
        status = "ok" if r.returncode == 0 else f"FAIL exit={r.returncode}"
        print(f"        -> P{i:02d} {status} in {dt:.1f}s (log: {log.name})", flush=True)
    print("TRANSCRIBE ALL DONE", flush=True)


if __name__ == "__main__":
    main()
