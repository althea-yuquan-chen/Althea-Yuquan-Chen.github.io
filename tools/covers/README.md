# Cover images

Scripts that render the 1200x627 social covers in `assets/og/`. The home-page card images in
`assets/cards/` are crops of the right half of each cover. Requires Python 3 and Pillow.

| Script | Output | Input |
|---|---|---|
| `make_v2d_cover.py` | `assets/og/v2d.png` | Folder of Tier 3 review sheets (`ep11_light_blue_book_rot5_tex.png`, `ep25_cyan_water_bottle_rot5_tex.png`) from the V2D reconstruction work. Frames come from the NVIDIA Video-to-Data Challenge dataset (CC BY 4.0); keep the credit line. |
| `make_dfum_cover.py` | `assets/og/dfum.png` | `results/qini_auuc_summary.csv` from the Decision-Focused-Uplift-Modeling repository. |
| `make_realdelta_cover.py` | `assets/og/realdelta.png` | `examples/real_model/run_20261116/` from the realdelta repository (arms `a1.jsonl` and `a2.jsonl`). |

```bash
python make_dfum_cover.py ../Decision-Focused-Uplift-Modeling/results/qini_auuc_summary.csv ../../assets/og/dfum.png
```

Card crops (pixel boxes on the 1200x627 cover, then resized to 560 px wide): V2D `(640, 30, 1170, 586)` saved as JPEG,
DFUM `(636, 38, 1172, 530)`, realdelta `(636, 80, 1172, 590)`.

After replacing an image, bump the `?v=` query on its `<img>` and `og:image` URLs so browsers and LinkedIn fetch it again,
and run the page through LinkedIn's Post Inspector if a shared link still shows the old preview.
