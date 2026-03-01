#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
buttons = json.loads((ROOT / 'scripts' / 'buttons_en.json').read_text())

ACTION_MAP = {
    'Yes': 'Nod clearly and show thumbs-up.',
    'No': 'Shake head gently and open palm side-to-side.',
    'Thank you': 'Hand to chest, warm smile, slight nod.',
    'Please': 'Polite forward hand gesture, soft expression.',
    'Hello': 'Friendly wave toward camera.',
    'Goodbye': 'Wave while taking half step away.',
    'I need help': 'Raise hand and look toward helper.',
    'Stop': 'Clear stop-hand gesture, freeze motion.',
}

DEFAULT = 'Perform a clear, age-appropriate gesture that matches the phrase.'

lines = ['# Storyboard v1', '', 'Standard timing: 6s total (1s intro, 4s action, 1s hold)', '']
for b in buttons:
    phrase = b['phrase']
    action = ACTION_MAP.get(phrase, DEFAULT)
    lines += [
        f"## {b['id']} - {phrase}",
        f"- Category: {b['category']}",
        f"- Action: {action}",
        f"- Voice line: \"{phrase}\"",
        f"- Subtitle: {phrase}",
        ''
    ]

(ROOT / 'scripts' / 'storyboard_v1.md').write_text('\n'.join(lines))
print('wrote storyboard_v1.md')
