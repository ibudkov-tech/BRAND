"""Build the password-protected copy of the landing into ../project_brand_protected/.

Usage:  LANDING_PASSWORD='...' python3 protect.py
The password is only used to derive the key; it is never written to any file.
Every slide image and the whole deck markup are encrypted (AES-256-GCM, PBKDF2-SHA256 key).
"""
import base64
import hashlib
import hmac
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

# The salt is not secret, but it is kept between builds so that unchanged slides encrypt to identical files.
SALT_FILE = os.path.join(BASE, 'protect.salt')
if os.path.exists(SALT_FILE):
    salt = base64.b64decode(open(SALT_FILE).read().strip())
else:
    salt = os.urandom(16)
    open(SALT_FILE, 'w').write(base64.b64encode(salt).decode())

# 64 bytes: the first 32 are the AES key (identical to what the browser derives with length 256),
# the next 32 are a MAC key used only to derive deterministic IVs.
okm = PBKDF2HMAC(algorithm=hashes.SHA256(), length=64, salt=salt, iterations=ITER).derive(password.encode('utf-8'))
key, mac_key = okm[:32], okm[32:]
aes = AESGCM(key)


def seal(data: bytes) -> bytes:
    # IV = HMAC(plaintext): same input -> same output (so git sees no change), different input -> different IV
    iv = hmac.new(mac_key, data, hashlib.sha256).digest()[:12]
    return iv + aes.encrypt(iv, data, None)  # iv | ciphertext | tag


def write_if_changed(path, data: bytes):
    if os.path.exists(path) and open(path, 'rb').read() == data:
        return False
    with open(path, 'wb') as f:
        f.write(data)
    return True


os.makedirs(os.path.join(OUT, 'enc'), exist_ok=True)  # never wipe OUT: it may hold a .git folder
fresh = set()
changed = 0

# images -> encrypted blobs drawn into <canvas> in the browser (no <img>, no file URLs)
def to_canvas(m):
    name = os.path.splitext(os.path.basename(m.group(1)))[0]
    with open(os.path.join(BASE, m.group(1)), 'rb') as f:
        data = f.read()
    global changed
    fresh.add(name + '.bin')
    changed += write_if_changed(os.path.join(OUT, 'enc', name + '.bin'), seal(data))
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
changed += write_if_changed(os.path.join(OUT, 'index.html'), shell.encode('utf-8'))
write_if_changed(os.path.join(OUT, 'robots.txt'), b'User-agent: *\nDisallow: /\n')
for f in os.listdir(os.path.join(OUT, 'enc')):  # drop slides that no longer exist
    if f not in fresh:
        os.remove(os.path.join(OUT, 'enc', f)); changed += 1
print('slides:', len(fresh), '| files changed this run:', changed, '->', os.path.abspath(OUT))
