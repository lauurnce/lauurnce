"""Generate the character-density ASCII portrait used in README.md from a GitHub avatar image."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SRC = os.path.join(REPO, "assets", "avatar-source.png")
OUT = os.path.join(REPO, "assets", "ascii-portrait.png")
FONT = "/System/Library/Fonts/SFNSMono.ttf"

RAMP = " .:-=+*#%@$"
CELL_W = 7
CELL_H = 13
COLS = 90
CROP_BOX = (15, 45, 205, 345)  # tight head-and-shoulders crop of the source avatar


def make_ascii_png(src=SRC, out_path=OUT, invert=True, tint_dark="#4a5058", tint_light="#f5f5f5",
                    crop_box=CROP_BOX, blur=1.0, contrast_cutoff=2):
    img = Image.open(src).convert("L")
    if crop_box:
        img = img.crop(crop_box)
    if blur:
        img = img.filter(ImageFilter.GaussianBlur(blur))

    w, h = img.size
    aspect = h / w
    cols = COLS
    rows = int(cols * aspect * (CELL_W / CELL_H))

    # Resize with a margin then crop it away - avoids Lanczos ringing at hard image borders
    margin = 3
    img = img.resize((cols + 2 * margin, rows + 2 * margin), Image.LANCZOS)
    img = img.crop((margin, margin, margin + cols, margin + rows))

    if contrast_cutoff:
        img = ImageOps.autocontrast(img, cutoff=contrast_cutoff)

    px = img.load()
    out_w, out_h = cols * CELL_W, rows * CELL_H
    canvas = Image.new("RGBA", (out_w, out_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype(FONT, CELL_H)

    dark = tuple(int(tint_dark.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    light = tuple(int(tint_light.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    n = len(RAMP) - 1

    for y in range(rows):
        for x in range(cols):
            v = px[x, y] / 255.0
            if invert:
                v = 1 - v
            ch = RAMP[int(v * n)]
            if ch == " ":
                continue
            color = tuple(int(dark[i] + (light[i] - dark[i]) * v) for i in range(3))
            draw.text((x * CELL_W, y * CELL_H), ch, font=font, fill=color + (255,))

    canvas.save(out_path)
    print(f"saved {out_path} size={canvas.size}")


if __name__ == "__main__":
    make_ascii_png()
