#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
OUT = ROOT / "renders"
BUTTONS = json.loads((ROOT / "scripts" / "buttons_en.json").read_text())


def run(cmd):
    print("+", " ".join(map(str, cmd)))
    subprocess.run(cmd, check=True)


def add_subtitle(in_mp4: Path, out_mp4: Path, phrase: str):
    srt = in_mp4.with_suffix(".srt")
    srt.write_text(
        "1\n00:00:00,600 --> 00:00:05,800\n" + phrase + "\n",
        encoding="utf-8",
    )
    run([
        "ffmpeg", "-y", "-i", str(in_mp4),
        "-vf", f"subtitles={srt}",
        "-c:v", "libx264", "-crf", "20", "-preset", "medium",
        "-c:a", "aac", "-b:a", "128k", str(out_mp4)
    ])


def main(limit=8):
    pick = BUTTONS[:limit]
    for gender in ["male", "female"]:
        base_dir = OUT / gender
        base_dir.mkdir(parents=True, exist_ok=True)
        for b in pick:
            phrase_slug = b['phrase'].lower().replace(' ', '_').replace('/', '_').replace("'", '')
            base = f"{b['id']}_{phrase_slug}"
            raw = base_dir / f"{base}_raw.mp4"
            final = base_dir / f"{base}.mp4"
            run([
                "blender", "-b", "-P", str(TOOLS / "render_cartoon_clip.py"), "--",
                "--phrase", b["phrase"],
                "--out", str(raw),
                "--gender", gender,
                "--action", "auto",
            ])
            add_subtitle(raw, final, b["phrase"])
            raw.unlink(missing_ok=True)
            srt = raw.with_suffix('.srt')
            srt.unlink(missing_ok=True)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=8)
    args = ap.parse_args()
    main(limit=args.limit)
