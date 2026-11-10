#!/usr/bin/env python3
"""한샘 신이천대리점 인스타 캐러셀(4:5, 1080x1350) 생성기.

양식 (cheongu / seongyeong 과 동일)
  01 표지      : 아이보리 배경, 제목 + 사진 타일(라벨 pill)
  02~ 공간     : 전면 사진 + 하단 그라데이션 + "NN · 공간" / 제목 / 부제 2줄
  마지막-1     : MATERIAL GUIDE (공간별 핵심 자재)
  마지막       : 상담 안내 (다크 배경, 고정 문구)

사용법: python3 make_carousel.py site.json
site.json 예시는 sites/dusan.json 참고. 사진 경로는 json 기준 상대경로.
"""
import json, sys, os
from PIL import Image, ImageDraw, ImageFont, ImageOps

W, H = 1080, 1350
IVORY = (243, 239, 231)
INK = (47, 43, 38)
TAUPE = (140, 125, 105)
SUB = (96, 87, 76)
LINE = (214, 207, 195)
BAR = (205, 196, 182)
DARK = (47, 43, 38)
WHITE = (255, 255, 255)

FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-{}.ttc"
KR_INDEX = 1  # Noto Sans CJK KR


def font(weight, size):
    return ImageFont.truetype(FONT.format(weight), size, index=KR_INDEX)


def tw(d, s, f):
    b = d.textbbox((0, 0), s, font=f)
    return b[2] - b[0]


def spaced(d, xy, s, f, fill, sp):
    x, y = xy
    for ch in s:
        d.text((x, y), ch, font=f, fill=fill)
        x += tw(d, ch, f) + sp if ch != " " else sp * 3


def cover_crop(im, ratio, fx=0.5, fy=0.5):
    w, h = im.size
    if w / h > ratio:
        nw = int(h * ratio); x = int((w - nw) * fx); return im.crop((x, 0, x + nw, h))
    nh = int(w / ratio); y = int((h - nh) * fy); return im.crop((0, y, w, y + nh))


def pill(d, xy, s, f, bg, fg, px=18, py=8):
    x, y = xy
    w = tw(d, s, f) + px * 2
    h = f.size + py * 2 + 4
    d.rounded_rectangle((x, y, x + w, y + h), radius=h // 2, fill=bg)
    d.text((x + px, y + py - 2), s, font=f, fill=fg)


def load(base, p):
    return ImageOps.exif_transpose(Image.open(os.path.join(base, p))).convert("RGB")


def make_cover(cfg, base, out):
    c = Image.new("RGB", (W, H), IVORY); d = ImageDraw.Draw(c)
    left = 56
    spaced(d, (left, 46), "한샘 신이천대리점 · 시공사례", font("Medium", 27), TAUPE, 4)
    r = font("Medium", 25); s = "시공 후기 넘겨보기 →"
    d.text((W - left - tw(d, s, r), 48), s, font=r, fill=TAUPE)
    d.text((left, 88), cfg["title"], font=font("Bold", 92), fill=INK)
    d.text((left, 196), cfg["subtitle"], font=font("Bold", 58), fill=INK)
    d.text((left, 274), cfg["tagline"], font=font("Regular", 29), fill=SUB)
    gx, gy, gap = 40, 336, 16
    tiles = cfg["tiles"]
    areas = []
    full_w, full_h = W - gx * 2, H - gy - 34
    if len(tiles) == 4:
        w2 = (full_w - gap) // 2; h2 = (full_h - gap) // 2
        areas = [(gx + (i % 2) * (w2 + gap), gy + (i // 2) * (h2 + gap), w2, h2) for i in range(4)]
    else:  # 3 tiles: left tall + right two stacked
        w2 = (full_w - gap) // 2; h2 = (full_h - gap) // 2
        areas = [(gx, gy, w2, full_h), (gx + w2 + gap, gy, w2, h2), (gx + w2 + gap, gy + h2 + gap, w2, h2)]
    for t, (x, y, w, h) in zip(tiles, areas):
        im = cover_crop(load(base, t["photo"]), w / h, t.get("fx", .5), t.get("fy", .5)).resize((w, h), Image.LANCZOS)
        c.paste(im, (x, y)); d = ImageDraw.Draw(c)
        pill(d, (x + 16, y + h - 62), t["label"], font("Bold", 26), (47, 43, 38), WHITE)
    c.save(out, quality=93, subsampling=0)


def make_photo(slide, base, out):
    im = cover_crop(load(base, slide["photo"]), W / H, slide.get("fx", .5), slide.get("fy", .5)).resize((W, H), Image.LANCZOS)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    top = 930
    for y in range(top, H):
        a = int(215 * ((y - top) / (H - top)) ** 1.15)
        od.line((0, y, W, y), fill=(30, 27, 24, a))
    im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
    d = ImageDraw.Draw(im); x = 58
    spaced(d, (x, 1070), slide["tag"], font("Medium", 27), (226, 218, 205), 4)
    d.text((x, 1112), slide["title"], font=font("Bold", 58), fill=WHITE)
    for i, ln in enumerate(slide["lines"]):
        d.text((x, 1204 + i * 50), ln, font=font("Regular", 31), fill=(232, 226, 216))
    im.save(out, quality=93, subsampling=0)


def make_summary(cfg, out):
    c = Image.new("RGB", (W, H), IVORY); d = ImageDraw.Draw(c); left = 64
    spaced(d, (left, 78), "MATERIAL GUIDE", font("Medium", 26), TAUPE, 6)
    d.text((left, 122), "공간별 핵심 자재", font=font("Bold", 68), fill=INK)
    d.text((left, 214), cfg["summary_sub"], font=font("Regular", 31), fill=SUB)
    d.rounded_rectangle((left, 266, W - left, 288), radius=11, fill=BAR)
    secs = cfg["summary"]
    y = 330; avail = 1255 - y
    units = sum(2 + len(s["lines"]) * 0.9 for s in secs)  # 섹션 높이를 줄 수에 비례
    for s in secs:
        step = int(avail * (2 + len(s["lines"]) * 0.9) / units)
        d.line((left, y, W - left, y), fill=LINE, width=2)
        d.text((left, y + 28), s["name"], font=font("Bold", 46), fill=INK)
        for j, ln in enumerate(s["lines"]):
            d.text((left, y + 96 + j * 46), ln, font=font("Regular", 30), fill=SUB)
        y += step
    d.line((left, y, W - left, y), fill=LINE, width=2)
    d.text((left, 1292), "※ 세부 사양과 전체 시공 후기는 블로그에서 확인하세요", font=font("Regular", 25), fill=TAUPE)
    c.save(out, quality=93, subsampling=0)


def make_contact(out):
    c = Image.new("RGB", (W, H), DARK); d = ImageDraw.Draw(c); x = 72
    d.rectangle((x, 250, x + 90, 258), fill=BAR)
    spaced(d, (x, 300), "한샘  신이천대리점", font("Medium", 33), (214, 206, 192), 3)
    d.text((x, 390), "우리 집 구조에 맞는", font=font("Bold", 72), fill=WHITE)
    d.text((x, 482), "정확한 판단이 필요하다면", font=font("Bold", 72), fill=WHITE)
    d.text((x, 596), "설계부터 감리까지 RD가 직접,", font=font("Regular", 36), fill=(232, 226, 216))
    d.text((x, 654), "1997년부터 이어온 현장 경험으로 상담해 드려요.", font=font("Regular", 36), fill=(232, 226, 216))
    d.rounded_rectangle((72, 790, 1008, 1090), radius=34, outline=BAR, width=3)
    d.text((116, 826), "상담 문의", font=font("Bold", 40), fill=WHITE)
    for i, ln in enumerate(["DM 으로 편하게 남겨주세요", "전체 시공 후기 · 자재 상세는", "프로필 링크의 네이버 블로그에서"]):
        d.text((116, 906 + i * 58 - (10 if i else 0)), ln, font=font("Regular", 35), fill=(232, 226, 216))
    d.text((72, 1232), "RD 김기수가 직접 시공 · 작성한 자사 시공사례입니다.", font=font("Regular", 27), fill=(150, 140, 126))
    c.save(out, quality=93, subsampling=0)


def main(path):
    cfg = json.load(open(path, encoding="utf-8"))
    base = os.path.dirname(os.path.abspath(path))
    outdir = os.path.join(base, cfg["out_dir"]); os.makedirs(outdir, exist_ok=True)
    names = []
    n = 1
    f = f"{n:02d}_cover.jpg"; make_cover(cfg, base, os.path.join(outdir, f)); names.append(f)
    for s in cfg["slides"]:
        n += 1; f = f"{n:02d}_{s['key']}.jpg"; make_photo(s, base, os.path.join(outdir, f)); names.append(f)
    n += 1; f = f"{n:02d}_materials.jpg"; make_summary(cfg, os.path.join(outdir, f)); names.append(f)
    n += 1; f = f"{n:02d}_contact.jpg"; make_contact(os.path.join(outdir, f)); names.append(f)
    print("\n".join(names))


if __name__ == "__main__":
    main(sys.argv[1])
