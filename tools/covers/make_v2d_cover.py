"""Render the V2D social cover (1200x627) from the Tier 3 ep11 review sheet.

Usage: python -I make_v2d_cover.py <review dir> <out.png>
Sheet layout: 8 rows x 3 columns of 360x360 cells with a 26px label strip; columns are
0 = exo video frame (with mask outline), 1 = delivered reconstruction, 2 = ROT_DEG 5 variant.
The cover uses columns 0 and 1 (the delivered submission). Frames were picked by the delivered IoU printed
in each cell header, skipping frames that show a face: ep11 f116 (IoU 0.98) and ep25 f251 (IoU 0.89; f745 scored 0.96 but shows
only the bottle base end-on, which reads poorly).
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

CW, RH, LAB = 360, 360, 26
PICKS = [("ep11_light_blue_book_rot5_tex.png", 0), ("ep25_cyan_water_bottle_rot5_tex.png", 2)]
COLS = [0, 1]
sheets = {f: Image.open(os.path.join(sys.argv[1], f)).convert("RGB") for f, _ in PICKS}


def tile_of(sheet, row, col, tile):
    c = sheets[sheet].crop((col * CW, row * RH + LAB, (col + 1) * CW, (row + 1) * RH))
    s = tile / min(c.size)
    c = c.resize((round(c.width * s), round(c.height * s)), Image.LANCZOS)
    l, t = (c.width - tile) // 2, (c.height - tile) // 2
    return c.crop((l, t, l + tile, t + tile))


def font(sz, bold=False):
    cands = (["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf",
             "/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/Library/Fonts/Arial Bold.ttf"] if bold
             else ["C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf",
             "/System/Library/Fonts/Supplemental/Arial.ttf", "/Library/Fonts/Arial.ttf"])
    for f in cands:
        if os.path.exists(f):
            return ImageFont.truetype(f, sz)
    raise FileNotFoundError("no font")


W, H = 1200, 627
img = Image.new("RGB", (W, H), "#FFFFFF")
d = ImageDraw.Draw(img)
tile, gap = 250, 10
x0, y0 = W - 2 * tile - gap - 40, 66
for i, (sh, r) in enumerate(PICKS):
    for j, c in enumerate(COLS):
        img.paste(tile_of(sh, r, c, tile), (x0 + j * (tile + gap), y0 + i * (tile + gap)))
d.text((x0, y0 - 30), "video + object mask", fill="#8A8A8A", font=font(18))
d.text((x0 + tile + gap, y0 - 30), "reconstructed object pose", fill="#8A8A8A", font=font(18))
d.text((x0, y0 + 2 * tile + gap + 10), "Frames: NVIDIA Video-to-Data Challenge dataset, CC BY 4.0.", fill="#8A8A8A", font=font(13))
d.text((x0, y0 + 2 * tile + gap + 28), "Cropped, with reconstruction overlay.", fill="#8A8A8A", font=font(13))
lx = 48
d.text((lx, 150), "Turning one video into", fill="#222222", font=font(44, True))
d.text((lx, 204), "robot training data", fill="#222222", font=font(44, True))
d.text((lx, 290), "4D human-object reconstruction from", fill="#484848", font=font(24))
d.text((lx, 322), "single-view video, no clean ground truth", fill="#484848", font=font(24))
d.rectangle((lx, 390, lx + 6, 452), fill="#0C6DBD")
d.text((lx + 22, 386), "Team placed 3rd of 19", fill="#0C6DBD", font=font(36, True))
d.text((lx + 22, 432), "Tier 3 success rate, NVIDIA V2D Challenge, Track 2", fill="#484848", font=font(18))
img.save(sys.argv[2], optimize=True)
print("picks", PICKS, "cols", COLS, img.size)
