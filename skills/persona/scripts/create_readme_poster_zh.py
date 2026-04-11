#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
OUT = ASSETS / "persona_skill_poster_clean_zh.png"

W = 1242
H = 1660

BG = "#F4EEE5"
PANEL = "#FBF7F2"
INK = "#1E1816"
MUTED = "#6C625C"
RED = "#C94E3F"
DEEP_RED = "#A33A2E"
GOLD = "#D7B787"
LINE = "#E7D9C8"
GREEN = "#95A87B"


def font(size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/PrivateFrameworks/FontServices.framework/Resources/Reserved/PingFangUI.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    ]
    for item in candidates:
        path = Path(item)
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    raise FileNotFoundError("No suitable Chinese font found on this machine.")


FONT_H1 = font(82)
FONT_H2 = font(38)
FONT_H3 = font(30)
FONT_BODY = font(24)
FONT_SMALL = font(20)
FONT_CODE = font(23)
FONT_CHIP = font(22)


def rounded_box(draw: ImageDraw.ImageDraw, xy, radius: int, fill: str, outline: str | None = None, width: int = 1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def shadowed_panel(base: Image.Image, xy, radius: int = 28, shadow_offset=(0, 14), shadow_blur=28):
    x1, y1, x2, y2 = xy
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sx1 = x1 + shadow_offset[0]
    sy1 = y1 + shadow_offset[1]
    sx2 = x2 + shadow_offset[0]
    sy2 = y2 + shadow_offset[1]
    sd.rounded_rectangle((sx1, sy1, sx2, sy2), radius=radius, fill=(66, 41, 27, 28))
    shadow = shadow.filter(ImageFilter.GaussianBlur(shadow_blur))
    base.alpha_composite(shadow)
    d = ImageDraw.Draw(base)
    d.rounded_rectangle(xy, radius=radius, fill=PANEL, outline=LINE, width=2)


def fit_text(draw: ImageDraw.ImageDraw, text: str, box_width: int, text_font, fill: str, x: int, y: int, line_gap: int = 10):
    lines = []
    current = ""
    for char in text:
        test = current + char
        if draw.textbbox((0, 0), test, font=text_font)[2] <= box_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = char
    if current:
        lines.append(current)
    cy = y
    for line in lines:
        draw.text((x, cy), line, font=text_font, fill=fill)
        cy += text_font.size + line_gap
    return cy


def chip(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, fill: str = "#EFE5D8", text_fill: str = INK):
    bbox = draw.textbbox((0, 0), text, font=FONT_CHIP)
    w = bbox[2] - bbox[0] + 30
    h = bbox[3] - bbox[1] + 18
    draw.rounded_rectangle((x, y, x + w, y + h), radius=18, fill=fill, outline=LINE, width=1)
    draw.text((x + 15, y + 9), text, font=FONT_CHIP, fill=text_fill)
    return x + w


def load_avatar(path: Path, size: int) -> Image.Image:
    img = Image.open(path).convert("RGB")
    side = min(img.size)
    left = (img.width - side) // 2
    top = (img.height - side) // 2
    img = img.crop((left, top, left + side, top + side)).resize((size, size))
    mask = Image.new("L", (size, size), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse((0, 0, size - 1, size - 1), fill=255)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(img, (0, 0))
    out.putalpha(mask)
    return out


def card(draw: ImageDraw.ImageDraw, base: Image.Image, x: int, y: int, w: int, h: int, title: str, subtitle: str, accent: str, avatar: Image.Image | None = None):
    shadowed_panel(base, (x, y, x + w, y + h), radius=26, shadow_offset=(0, 10), shadow_blur=18)
    draw = ImageDraw.Draw(base)
    draw.rounded_rectangle((x + 18, y + 18, x + 90, y + 26), radius=4, fill=accent)
    if avatar:
        base.alpha_composite(avatar, (x + 26, y + 42))
        tx = x + 130
    else:
        tx = x + 28
    draw.text((tx, y + 48), title, font=FONT_H3, fill=INK)
    fit_text(draw, subtitle, w - (tx - x) - 28, FONT_BODY, MUTED, tx, y + 92, line_gap=7)


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)

    base = Image.new("RGBA", (W, H), BG)
    draw = ImageDraw.Draw(base)

    # soft background shapes
    draw.ellipse((-140, -120, 360, 360), fill="#EADFD1")
    draw.ellipse((900, -60, 1390, 430), fill="#E7D7C6")
    draw.rounded_rectangle((72, 78, W - 72, H - 78), radius=42, outline="#EADCCB", width=3)

    # top badge
    draw.rounded_rectangle((92, 88, 228, 144), radius=20, fill=RED)
    draw.text((120, 102), "模块化 Persona", font=FONT_CHIP, fill="white")

    # title
    draw.text((92, 188), "Persona Skill", font=FONT_H1, fill=INK)
    draw.text((92, 286), "把人物蒸馏成可切换、可融合、可持续扮演的模块化 persona", font=FONT_H2, fill=DEEP_RED)
    fit_text(
        draw,
        "不是几条标签，不是临时 prompt，而是一套带证据、场景、模块和命令系统的工程化人格 skill。",
        W - 184,
        FONT_BODY,
        MUTED,
        92,
        340,
        line_gap=8,
    )

    # chips
    x = 92
    y = 434
    for text, fill in [
        ("通用人格建模", "#F0E4D5"),
        ("证据化蒸馏", "#F7E7DE"),
        ("模块加载", "#E6EFE3"),
        ("角色切换", "#EFE2D9"),
        ("语言切换", "#EEE7D5"),
        ("Fuse 融合", "#F5E1DD"),
    ]:
        x = chip(draw, x, y, text, fill=fill) + 14

    # command block
    shadowed_panel(base, (92, 520, 1150, 760), radius=32, shadow_offset=(0, 12), shadow_blur=20)
    draw = ImageDraw.Draw(base)
    draw.text((124, 558), "一套命令，覆盖完整流程", font=FONT_H3, fill=INK)
    draw.text((124, 606), "/persona distill  从资料目录一步蒸馏出完整 persona", font=FONT_CODE, fill=INK)
    draw.text((124, 644), "/persona <name>    进入角色并持续扮演直到 exit", font=FONT_CODE, fill=INK)
    draw.text((124, 682), "/persona fuse      把 2~3 个 final persona 融合成新角色", font=FONT_CODE, fill=INK)
    draw.text((124, 720), "/persona language  切换回答语言，但不丢角色风格", font=FONT_CODE, fill=INK)

    # question
    draw.rounded_rectangle((92, 800, 1150, 878), radius=28, fill="#241D1A")
    draw.text((128, 822), "同一个问题：佛法自然还是道法自然？", font=FONT_H3, fill="white")

    laozi_avatar = load_avatar(ASSETS / "laozi.png", 78)
    fozu_avatar = load_avatar(ASSETS / "fozu.jpg", 78)

    # persona comparison cards
    card(
        draw,
        base,
        92,
        916,
        336,
        264,
        "佛祖",
        "佛家多说缘起，不以“自然”立宗。回答会自然偏向缘起、空、执著、解脱。",
        RED,
        avatar=fozu_avatar,
    )
    card(
        draw,
        base,
        453,
        916,
        336,
        264,
        "老子",
        "道法自然，不必混名。回答更短、更收，重点回到妄作、强为、名与自然。",
        GOLD,
        avatar=laozi_avatar,
    )

    # fused card with dual avatars
    shadowed_panel(base, (814, 916, 1150, 1180), radius=26, shadow_offset=(0, 10), shadow_blur=18)
    draw = ImageDraw.Draw(base)
    draw.rounded_rectangle((832, 934, 904, 942), radius=4, fill=GREEN)
    base.alpha_composite(fozu_avatar.resize((66, 66)), (840, 958))
    base.alpha_composite(laozi_avatar.resize((66, 66)), (884, 958))
    draw.text((970, 964), "老佛爷", font=FONT_H3, fill=INK)
    fit_text(
        draw,
        "融合后不是机械拼接，而是形成稳定混合立场：道家说自然，佛家说缘起。",
        1150 - 842,
        FONT_BODY,
        MUTED,
        842,
        1044,
        line_gap=7,
    )

    # bottom grid
    shadowed_panel(base, (92, 1222, 1150, 1520), radius=32, shadow_offset=(0, 12), shadow_blur=20)
    draw = ImageDraw.Draw(base)
    draw.text((124, 1260), "最终产物不是 prompt，而是完整 artifact", font=FONT_H3, fill=INK)

    left_x = 124
    right_x = 650
    bullet_y = 1320
    bullets_left = [
        "source_index / evidence_index",
        "17 维 persona 建模",
        "voice_model / scenario_library",
    ]
    bullets_right = [
        "modules / load_profiles",
        "router-ready 角色切换",
        "进入后持续扮演直到 /persona exit",
    ]
    for text in bullets_left:
        draw.rounded_rectangle((left_x, bullet_y + 8, left_x + 14, bullet_y + 22), radius=7, fill=RED)
        draw.text((left_x + 28, bullet_y), text, font=FONT_BODY, fill=INK)
        bullet_y += 58
    bullet_y = 1320
    for text in bullets_right:
        draw.rounded_rectangle((right_x, bullet_y + 8, right_x + 14, bullet_y + 22), radius=7, fill=GOLD)
        draw.text((right_x + 28, bullet_y), text, font=FONT_BODY, fill=INK)
        bullet_y += 58

    # bottom footer
    draw.text((92, 1568), "通用人格建模 · 证据蒸馏 · 角色切换 · 融合扮演", font=FONT_SMALL, fill=MUTED)

    base.convert("RGB").save(OUT, quality=95)
    print(OUT)


if __name__ == "__main__":
    main()
