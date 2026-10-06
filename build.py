import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))

# Reuse the nav / snap-scroll / counter / dropdown styles and scripts of the project_fin landing.
tpl = open(os.path.join(BASE, '..', 'project_fin', 'index.html'), encoding='utf-8').read()
CSS = re.search(r'<style>(.*?)</style>', tpl, re.S).group(1)
JS = re.search(r'<script>(.*?)</script>', tpl, re.S).group(1)

N_PAGES = 250
LOGO_ONLY = {3, 28, 55, 85, 107, 126, 157, 197, 218}

# (divider page, last page, client, [(target, label), ...])  target: int = deck page, 'desc' = description slide
PROJECTS = [
    (2, 26, 'MyMuse', [('desc', 'Описание проекта'), (6, 'Ситуация и задача'), (14, 'Анализ аудитории'),
                       (19, 'Анализ конкурентов'), (24, 'Гипотезы позиционирования')]),
    (27, 53, 'Рыбшеф', [('desc', 'Описание проекта'), (30, 'Список конкурентов'),
                        (32, 'Анализ коммуникации конкурентов'), (35, 'Выводы'), (43, 'Анализ трендов'),
                        (51, 'Анализ целевой аудитории'), (53, 'Стратегия бренда (NDA)')]),
    (54, 83, 'Сушивёсла', [('desc', 'Описание проекта'), (56, 'О бренде'), (60, 'О рынке'), (68, 'О людях'),
                           (73, 'Общие выводы'), (79, 'Идея позиционирования')]),
    (84, 105, 'Апельсин', [('desc', 'Описание проекта'), (89, 'Резюме брифа'),
                           (96, 'Международные практики и аудитория'), (98, 'Конкурентное окружение'),
                           (104, 'Гипотезы позиционирования')]),
    (106, 124, 'Пятёрочка', [('desc', 'Описание проекта'), (110, 'Как формируется доверие'),
                             (120, 'Направление 1 — доверие к человеку'), (121, 'Направление 2 — другое доверие'),
                             (122, 'Направление 3 — искренность'), (123, 'Направление 4 — свежесть'),
                             (124, 'Summary')]),
    (125, 155, 'М.Видео', [('desc', 'Описание проекта'), (127, 'Задачи'), (131, 'Аудитория и потребности'),
                           (139, 'Конкуренты'), (144, 'Тренды в retail'), (148, 'Идея и манифест бренда'),
                           (151, 'Платформа и принципы')]),
    (156, 195, 'Askona', [('desc', 'Описание проекта'), (158, 'Задачи'), (160, 'Аудит бренда'),
                          (170, 'Целевая аудитория'), (172, 'Тренды'), (174, 'Конкурентное окружение'),
                          (186, 'Мировые практики'), (192, 'Платформа')]),
    (196, 216, 'Иви', [('desc', 'Описание проекта'), (198, 'Цели'), (204, 'Тренды'), (205, 'Выводы'),
                       (209, 'Гипотезы ценностного предложения'), (214, 'Резюме')]),
    (217, 249, 'Bereke Bank', [('desc', 'Описание проекта'), (220, 'Ситуация и продукт'),
                                (226, 'Аудитория и тенденции'), (232, 'Конкурентный контекст'),
                                (239, 'Идея позиционирования')]),
]


def project_of(page):
    for k, (start, end, _, _) in enumerate(PROJECTS):
        if start <= page <= end:
            return k
    return -1


sections = []
for p in range(1, N_PAGES + 1):
    if p in LOGO_ONLY:
        continue
    k = project_of(p)
    ch = 0 if k >= 0 else -1
    sections.append(
        f'    <section class="slide" id="page-{p}" data-page="{p}" data-chapter="{ch}">\n'
        f'      <img src="img/page-{p:03d}.jpg" alt="Слайд {p}" loading="lazy" draggable="false">\n'
        f'    </section>')
    # the description slide follows the numbered divider of each project
    if k >= 0 and p == PROJECTS[k][0]:
        sections.append(
            f'    <section class="slide" id="desc-{k + 1:02d}" data-page="desc-{k + 1:02d}" data-chapter="0">\n'
            f'      <img src="img/desc-{k + 1:02d}.jpg" alt="Описание проекта {PROJECTS[k][2]}" loading="lazy" draggable="false">\n'
            f'    </section>')


def target_id(k, t):
    return f'desc-{k + 1:02d}' if t == 'desc' else f'page-{t}'


subs = '\n          '.join(
    f'<a href="#page-{start}" class="chapter-sub-link"><span class="chapter-sub-client">{k + 1:02d}</span> {client}</a>'
    for k, (start, _, client, _) in enumerate(PROJECTS))
nav = [f'''<div class="chapter-item">
      <a href="#page-{PROJECTS[0][0]}" class="chapter-link" data-chapter-idx="0">Бренд-платформа</a>
      <div class="chapter-dropdown">
        <div class="chapter-dropdown-inner">
          {subs}
        </div>
      </div>
    </div>''']

total = len(sections)
html = f'''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>Бренд-стратегия — Тутков/Будков</title>
<meta name="description" content="Портфолио агентства Тутков/Будков по бренд-стратегиям.">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow, noarchive">
<link rel="icon" href="data:,">
<style>{CSS}
  .chapternav {{ gap: 4px 22px; }}
  .chapter-sub-link {{ white-space: normal; max-width: 340px; }}
</style>
</head>
<body>

<div class="topbar"><div class="topbar-fill" id="topbarFill"></div></div>

<nav class="chapternav">
  <span class="brand">ТУТКОВБУДКОВ</span>
  {chr(10).join("  " + n for n in nav).lstrip()}
</nav>

<div class="scroller">
<div class="deck">
{chr(10).join(sections)}
</div>
</div>

<div class="slidenav" id="slidenav">
  <button id="prevSlide" aria-label="Предыдущий слайд">&#8249;</button>
  <span class="slide-counter" id="slideCounter">1 / {total}</span>
  <button id="nextSlide" aria-label="Следующий слайд">&#8250;</button>
</div>

<script>{JS}</script>

</body>
</html>
'''
open(os.path.join(BASE, 'index.html'), 'w', encoding='utf-8').write(html)
open(os.path.join(BASE, 'robots.txt'), 'w').write('User-agent: *\nDisallow: /\n')
print('wrote index.html:', total, 'slides,', len(html), 'bytes')
