#!/usr/bin/env python3
import base64
import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path('/Users/dariusroo/landingpages')
ENV_PATH = ROOT / '.env'
API_URL = 'https://api.openai.com/v1/images/generations'
MODEL = 'gpt-image-1'
SIZE = '1536x1024'
QUALITY = 'high'
OUTPUT_FORMAT = 'jpeg'

PROMPTS = [
    (
        'photo-1.jpg',
        'Create a realistic commercial photo for an auto repair website hero section: a clean modern mechanic shop interior with a professional mechanic inspecting a late-model vehicle on a lift, bright natural and overhead lighting, polished concrete floors, organized tools, premium service atmosphere, trustworthy and upscale, shallow depth of field, documentary-style realism, no text, no watermark, photorealistic.'
    ),
    (
        'photo-2.jpg',
        'Create a realistic close-up commercial photo for an auto repair services website: a skilled mechanic using a diagnostic tablet while checking a vehicle in a spotless service bay, visible engine and professional equipment, crisp lighting, modern workshop, confident craftsmanship, premium brand feel, highly realistic photography, no text, no watermark, photorealistic.'
    ),
    (
        'photo-3.jpg',
        'Create a realistic commercial photo for an auto repair landing page: a welcoming, professional auto service team standing in a clean high-end garage with a polished vehicle in the foreground, modern lighting, organized workspace, trustworthy and friendly mood, premium automotive service branding style, highly realistic photography, no text, no watermark, photorealistic.'
    ),
]


def load_env(path: Path):
    if not path.exists():
        return
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        if k and k not in os.environ:
            os.environ[k] = v


def generate_image(prompt: str) -> bytes:
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        raise RuntimeError('OPENAI_API_KEY not found in environment or .env')

    payload = {
        'model': MODEL,
        'prompt': prompt,
        'size': SIZE,
        'quality': QUALITY,
        'output_format': OUTPUT_FORMAT,
    }

    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        },
        method='POST',
    )

    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            body = resp.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        detail = e.read().decode('utf-8', errors='ignore')
        raise RuntimeError(f'HTTP {e.code}: {detail}') from e

    data = json.loads(body)
    items = data.get('data') or []
    if not items:
        raise RuntimeError(f'Unexpected response: {body[:1000]}')

    item = items[0]
    if 'b64_json' in item:
        return base64.b64decode(item['b64_json'])
    raise RuntimeError(f'No b64_json in response: {body[:1000]}')


def main():
    load_env(ENV_PATH)
    ROOT.mkdir(parents=True, exist_ok=True)

    for filename, prompt in PROMPTS:
        print(f'Generating {filename}...')
        img = generate_image(prompt)
        out = ROOT / filename
        out.write_bytes(img)
        print(f'Saved {out}')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'ERROR: {e}', file=sys.stderr)
        sys.exit(1)
