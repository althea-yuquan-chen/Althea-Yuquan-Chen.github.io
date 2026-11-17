"""Render the realdelta social cover (1200x627) from the pre-registered real-model run.

Usage: python -I make_realdelta_cover.py <run_20261116 dir> <out.png>
Arms A1 and A2 share the same prompt and model (an A/A pair). Each cell is one task; its shade is the
number of passing trials out of 5. Tasks whose pass count differs between the two runs are outlined.
"""
import collections
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

RUN, OUT = sys.argv[1], sys.argv[2]


def load(name):
    d = collections.defaultdict(int)
    t = collections.defaultdict(int)
    for line in open(os.path.join(RUN, name), encoding="utf-8"):
        if line.strip():
            r = json.loads(line)
            d[r["case_id"]] += bool(r["passed"])
            t[r["case_id"]] += 1
    return d, t


a1, t1 = load("a1.jsonl")
a2, t2 = load("a2.jsonl")
cases = sorted(t1)
assert sorted(t2) == cases and all(t1[c] == 5 and t2[c] == 5 for c in cases) and len(cases) == 40
p1, p2 = sum(a1.values()) / 200, sum(a2.values()) / 200
changed = [c for c in cases if a1[c] != a2[c]]

S = 2
W, H = 1200, 627
img = Image.new("RGB", (W * S, H * S), "#FFFFFF")
d = ImageDraw.Draw(img)


def font(sz, bold=False):
    cands = (["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf",
             "/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/Library/Fonts/Arial Bold.ttf"] if bold
             else ["C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf",
             "/System/Library/Fonts/Supplemental/Arial.ttf", "/Library/Fonts/Arial.ttf"])
    for f in cands:
        if os.path.exists(f):
            return ImageFont.truetype(f, sz * S)
    raise FileNotFoundError("no font")


def text(x, y, s, **k):
    d.text((x * S, y * S), s, **k)


def rect(x0, y0, x1, y1, **k):
    if "width" in k:
        k["width"] *= S
    d.rectangle((x0 * S, y0 * S, x1 * S, y1 * S), **k)


NAVY, INK, SLATE, LIGHT, AMBER = "#0C6DBD", "#222222", "#484848", "#8A8A8A", "#E8A317"
SHADES = ["#F1F4F8", "#D6E5F4", "#B3CFEB", "#86B3DE", "#4F8FCB", "#0C6DBD"]  # 0..5 passes


def grid(x0, y0, scores, title, rate):
    cell, gap, cols = 40, 7, 5
    text(x0, y0 - 66, title, fill=SLATE, font=font(18))
    text(x0, y0 - 44, f"{rate:.1%}", fill=INK, font=font(30, True))
    for i, c in enumerate(cases):
        r, q = divmod(i, cols)
        x, y = x0 + q * (cell + gap), y0 + r * (cell + gap)
        rect(x, y, x + cell, y + cell, fill=SHADES[scores[c]])
        if c in changed:
            rect(x - 3, y - 3, x + cell + 3, y + cell + 3, outline=AMBER, width=3)
    return cols * (cell + gap) - gap


gx = 650
gw = grid(gx, 150, a1, "Run 1", p1)
grid(gx + gw + 46, 150, a2, "Run 2", p2)

# legend
ly = 150 + 8 * 47 + 14
text(gx, ly, "each square: one task, shaded by trials passed (0-5 of 5)", fill=LIGHT, font=font(13))
rect(gx, ly + 26, gx + 14, ly + 40, outline=AMBER, width=2)
text(gx + 22, ly + 23, "scored differently in the two runs", fill=LIGHT, font=font(13))

lx = 48
text(lx, 116, "Same model. Same prompt.", fill=SLATE, font=font(26))
text(lx, 150, "Same 40 tasks, run twice.", fill=SLATE, font=font(26))
for k, s in enumerate([f"{len(changed)} of 40 tasks", "scored differently.", "Nothing was changed."]):
    text(lx, 222 + 54 * k, s, fill=NAVY if k < 2 else INK, font=font(44, True))
text(lx, 410, "Is that change in your agent eval real, or noise?", fill=SLATE, font=font(20))
text(lx, 440, "realdelta: open-source intervals for repeated trials.", fill=SLATE, font=font(20))
text(lx, 512, "Pre-registered run on GPT-5.6 Luna (Azure OpenAI), 5 trials per task;", fill=LIGHT, font=font(13))
text(lx, 530, "runs 1 and 2 are arms A1 and A2, which share one prompt.", fill=LIGHT, font=font(13))

img.resize((W, H), Image.LANCZOS).save(OUT, optimize=True)
print("tasks", len(cases), "run1", sum(a1.values()), "run2", sum(a2.values()), "changed", len(changed))
