"""Render the DFUM social cover (1200x627) from results/qini_auuc_summary.csv.

Usage: python -I make_dfum_cover.py <qini_auuc_summary.csv> <out.png>
Only the DFUM alpha sweep and the S-/X-Learner baselines are plotted: all come from
the same summary file, so the cover shares one provenance with the write-up table.
"""
import csv
import os
import sys

from PIL import Image, ImageDraw, ImageFont

rows = {r["model"]: r for r in csv.DictReader(open(sys.argv[1]))}
dfum = [(a, float(rows[f"DFUM Top-K (alpha={a})"]["auuc_mean"]),
         float(rows[f"DFUM Top-K (alpha={a})"]["auuc_std"])) for a in ("0.0", "0.2", "0.4", "0.6")]
base = [("X-Learner", float(rows["X-Learner"]["auuc_mean"])),
        ("S-Learner", float(rows["S-Learner"]["auuc_mean"]))]

S = 2  # supersample, then downscale for smooth circles
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


def text(x, y_, s, **k):
    d.text((x * S, y_ * S), s, **k)


def line(x0, y0, x1, y1, width=1, **k):
    d.line((x0 * S, y0 * S, x1 * S, y1 * S), width=width * S, **k)


def tw(s, f):
    return d.textlength(s, font=f) / S


NAVY, INK, SLATE, LIGHT, GRID, SOFT = "#0C6DBD", "#222222", "#484848", "#8A8A8A", "#E3E3E3", "#7FAEDB"
cx0, cx1, cy0, cy1 = 700, 1068, 92, 480
lo, hi = 0.735, 0.90


def y(v):
    return cy1 - (v - lo) / (hi - lo) * (cy1 - cy0)


for t in (0.76, 0.80, 0.84, 0.88):
    line(cx0, y(t), cx1, y(t), fill=GRID)
    text(cx0 - 46, y(t) - 10, f"{t:.2f}", fill=LIGHT, font=font(15))
text(cx0 - 46, cy0 - 46, "Test AUUC", fill=LIGHT, font=font(16))

for name, v in base:  # dashed reference lines, labels just right of the plot area
    x = cx0
    while x < cx1:
        line(x, y(v), min(x + 9, cx1), y(v), fill=SLATE)
        x += 16
    text(cx1 + 8, y(v) - 10, f"{name} {v:.3f}", fill=SLATE, font=font(13))

slot = (cx1 - cx0) / len(dfum)
for i, (a, m, s) in enumerate(dfum):
    xc = cx0 + slot * (i + 0.5) + 30
    best = a == "0.6"
    col = NAVY if best else SOFT
    line(xc, y(m + s), xc, y(m - s), fill=col, width=2)
    for yy in (y(m + s), y(m - s)):
        line(xc - 7, yy, xc + 7, yy, fill=col, width=2)
    r = 9 if best else 7
    d.ellipse(((xc - r) * S, (y(m) - r) * S, (xc + r) * S, (y(m) + r) * S), fill=col)
    f = font(18, best)
    lab = f"{m:.3f}"
    # lowest point: label under its whisker so it never collides with the baseline labels
    ly = y(m - s) + 6 if i == 0 else y(m + s) - 30
    text(xc - tw(lab, f) / 2, ly, lab, fill=NAVY if best else SLATE, font=f)
    f2 = font(17)
    al = f"\u03b1 = {float(a):g}"
    text(xc - tw(al, f2) / 2, cy1 + 12, al, fill=SLATE, font=f2)
line(cx0, cy1, cx1, cy1, fill=SLATE)

for k, s in enumerate(["\u03b1 = weight on the decision loss (0 = off). Points: mean \u00b1 1 std.",
                       "Criteo Uplift v2, 4.19M-row test split; 10 runs per DFUM",
                       "setting, 20 per baseline."]):
    text(cx0 - 46, cy1 + 48 + 18 * k, s, fill=LIGHT, font=font(13))

lx = 48
for k, s in enumerate(["Training uplift models", "on the decision, not just", "the prediction"]):
    text(lx, 140 + 54 * k, s, fill=INK, font=font(44, True))
text(lx, 330, "Decision-focused learning for", fill=SLATE, font=font(24))
text(lx, 362, "budget-constrained top-K targeting", fill=SLATE, font=font(24))
d.rectangle((lx * S, 428 * S, (lx + 6) * S, 490 * S), fill=NAVY)
text(lx + 22, 424, f"AUUC {dfum[0][1]:.3f} \u2192 {dfum[-1][1]:.3f}", fill=NAVY, font=font(36, True))
text(lx + 22, 470, "as the decision loss gets more weight", fill=SLATE, font=font(18))

img.resize((W, H), Image.LANCZOS).save(sys.argv[2], optimize=True)
print("plotted:", [(a, round(m, 3), round(s, 3)) for a, m, s in dfum], [(n, round(v, 3)) for n, v in base])
