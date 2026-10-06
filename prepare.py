import os, pymupdf as fitz
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, '..', 'brand_strat_fin.pdf')
LOGO_ONLY = {3, 28, 55, 85, 107, 126, 157, 197, 218}  # replaced by the description slides

doc = fitz.open(SRC)
z = 1920 / 1440
for i, page in enumerate(doc):
    n = i + 1
    if n in LOGO_ONLY:
        continue
    page.get_pixmap(matrix=fitz.Matrix(z, z), alpha=False).save(
        os.path.join(BASE, 'img', 'page-%03d.jpg' % n), jpg_quality=88)
print('rendered pages')

for k in range(1, 10):
    src = os.path.join(BASE, '..', 'bs_slides', 'png', 'slide-%02d.png' % k)
    Image.open(src).convert('RGB').save(os.path.join(BASE, 'img', 'desc-%02d.jpg' % k), quality=93)
print('copied descriptions')

# about the agency (about_team.pdf pages 2-9) and the team (pages 11-17); page 1 is a Rondell cover, page 10 a "06" divider
ABOUT = list(range(2, 10))
TEAM = list(range(11, 18))
adoc = fitz.open(os.path.join(BASE, '..', 'about_team.pdf'))
for n in ABOUT + TEAM:
    adoc[n - 1].get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False).save(
        os.path.join(BASE, 'img', 'about-%02d.jpg' % n), jpg_quality=90)
print('rendered about/team')
