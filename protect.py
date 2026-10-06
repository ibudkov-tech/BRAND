"""Build the password-protected copy of the landing into ../project_brand_protected/.

Usage:  LANDING_PASSWORD='...' python3 protect.py
The password is only used to derive the key; it is never written to any file.
Every slide image and the whole deck markup are encrypted (AES-256-GCM, PBKDF2-SHA256 key).
"""
import base64
import json
import os
import re
import shutil
import sys

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, '..', 'project_brand_protected')
ITER = 600_000

password = os.environ.get('LANDING_PASSWORD')
if not password:
    sys.exit('Set LANDING_PASSWORD in the environment')

src = open(os.path.join(BASE, 'index.html'), encoding='utf-8').read()
css = re.search(r'<style>(.*?)</style>', src, re.S).group(1)
js = re.search(r'<script>(.*?)</script>', src, re.S).group(1)
body = src[src.index('<body>') + 6: src.index('<script>')].strip()
title = re.search(r'<title>(.*?)</title>', src).group(1)

salt = os.urandom(16)
key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER).derive(password.encode('utf-8'))
aes = AESGCM(key)


def seal(data: bytes) -> bytes:
    iv = os.urandom(12)
    return iv + aes.encrypt(iv, data, None)  # iv | ciphertext | tag


if os.path.isdir(OUT):
    shutil.rmtree(OUT)
os.makedirs(os.path.join(OUT, 'enc'))

# images -> encrypted blobs drawn into <canvas> in the browser (no <img>, no file URLs)
def to_canvas(m):
    name = os.path.splitext(os.path.basename(m.group(1)))[0]
    with open(os.path.join(BASE, m.group(1)), 'rb') as f:
        data = f.read()
    with open(os.path.join(OUT, 'enc', name + '.bin'), 'wb') as f:
        f.write(seal(data))
    return (f'<canvas class="slide-canvas" width="1920" height="1080" data-src="enc/{name}.bin" '
            f'role="img" aria-label="{m.group(2)}"></canvas>')


body = re.sub(r'<img src="([^"]+)" alt="([^"]*)" loading="lazy" draggable="false">', to_canvas, body)
assert '<img' not in body
payload = base64.b64encode(seal(body.encode('utf-8'))).decode()

shell = open(os.path.join(BASE, 'shell_template.html'), encoding='utf-8').read()
shell = (shell.replace('%%TITLE%%', title)
         .replace('%%CSS%%', css)
         .replace('%%APPJS%%', js)
         .replace('%%SALT%%', base64.b64encode(salt).decode())
         .replace('%%ITER%%', str(ITER))
         .replace('%%PAYLOAD%%', payload))
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(shell)
open(os.path.join(OUT, 'robots.txt'), 'w').write('User-agent: *\nDisallow: /\n')
print('encrypted', len(os.listdir(os.path.join(OUT, 'enc'))), 'images ->', os.path.abspath(OUT))
