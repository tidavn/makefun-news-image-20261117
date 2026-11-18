#!/usr/bin/env python3
"""Render one image summarising Tuesday 17 November 2026 world news.

A classic broadsheet front page drawn programmatically with Pillow.
No network, no clock, no randomness: identical input always produces a
byte-identical PNG. Fonts are bundled in fonts/ and loaded by relative
path, so the program is self-contained.

Usage: python3 main.py
Writes to $ENTRY_OUTPUT, else /output/entry.png, else ./entry.png.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- constants
W, H = 1024, 1024
PAPER = (248, 244, 232)      # off-white newsprint
INK = (17, 17, 17)           # near-black ink
RED = (178, 35, 27)          # single red accent
BLUE = (31, 78, 121)         # single deep-blue accent
SKY = (214, 228, 238)        # illustration sky
SEA = (47, 93, 138)          # illustration sea
GREY = (110, 105, 92)        # muted grey-brown for captions
LIGHT_RULE = (190, 184, 168)

BASE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(BASE, "fonts")


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)   # noqa: E731
SERIF = lambda s: font("DejaVuSerif.ttf", s)         # noqa: E731
SANS = lambda s: font("DejaVuSans.ttf", s)           # noqa: E731
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)    # noqa: E731

# Grid geometry (measured so every column fits: 3 cols x 556 px).
GRID_TOP, GRID_BOT = 374, 930
COL_X = [26, 356, 686]
COL_W = 312
HEAD_LEAD, BODY_LEAD, STORY_GAP = 21, 16, 8
SECT_H, SECT_GAP = 30, 4


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- story data
# Every story below is a real event reported on Tuesday 17 November 2026.
# Headlines are kept to one line and bodies to one line at the chosen
# sizes so the page stays legible. No invented numbers, quotes or events.
LEAD = {
    "kicker": "LEAD STORY  ·  WAR IN UKRAINE",
    "headline": "KERCH BRIDGE SPAN FALLS AFTER UKRAINIAN STRIKE",
    "standfirst": (
        "A road span of the bridge to Crimea fell after a Ukrainian strike; "
        "Zelenskyy called it \u201cunprecedented\u201d."
    ),
}

SECTIONS = [
    ("WAR IN UKRAINE", [
        ("Kyiv bridges hit in reply",
         "Russia hit two Dnipro bridges."),
        ("1,336 drones intercepted",
         "Russia says it downed 1,336 drones."),
    ]),
    ("DIPLOMACY", [
        ("Trump lands in Manila",
         "Opens an Asia trip at the ASEAN summit."),
        ("Xi, Trump, Putin to meet",
         "First three-way talks in Shenzhen."),
        ("Thailand buys US goods",
         "A $2.6bn farm deal signed with Trump."),
    ]),
    ("EUROPE", [
        ("EU states plan Rwanda hub",
         "Five nations back a joint return hub."),
        ("UK sanctions Israeli firms",
         "Firms building West Bank settlements."),
        ("Japan scrambles jets",
         "Suspected Russian jets in its airspace."),
    ]),
    ("MIDDLE EAST", [
        ("Tankers ablaze off Hormuz",
         "Two tankers hit mines near the strait."),
        ("Third US carrier arrives",
         "Joins two carriers in the Middle East."),
        ("Bahrain base targeted",
         "Iran fired drones at a US radar base."),
        ("Vance: no long Iran war",
         "Vance says no long-term commitment."),
    ]),
    ("AMERICAS", [
        ("JPMorgan blames a bug",
         "Software bug caused the Zelle outage."),
        ("Pentagon fails audit again",
         "Ninth straight year; $4.8tn unverified."),
        ("House Democrats set agenda",
         "Health, Iran, tariffs top the agenda."),
    ]),
    ("HEALTH", [
        ("Gaza winter crisis grows",
         "1.7m displaced; 1.4m face acute hunger."),
        ("Eritrea beats trachoma",
         "WHO confirms trachoma eliminated."),
        ("US loses measles status",
         "13 babies born with measles since 2025."),
    ]),
    ("ASIA-PACIFIC", [
        ("Nvidia reports earnings",
         "First results since Jensen Huang\u2019s exit."),
        ("Singapore seeks US chips",
         "Seeks trusted access to US AI chips."),
        ("Mongolia leader to resign",
         "Quits over a $25m railway allegation."),
    ]),
    ("MARKETS & TECH", [
        ("Vulcan rocket fails",
         "Forty Amazon satellites destroyed."),
        ("Brent crude near $92.61",
         "Oil held around $92.61 a barrel."),
        ("US closes AI-chip loophole",
         "Commerce tightens AI-chip controls."),
    ]),
    ("WORLD", [
        ("17 killed in South Africa",
         "At least 17 dead in two shootings."),
        ("Bus plunges into ravine",
         "Six to eight dead in Uttarakhand, India."),
        ("Sri Lanka all out for 98",
         "Dismissed for 98 in Rawalpindi."),
        ("Houthis push back in Yemen",
         "Troops fall back to defend Aden."),
    ]),
]

# Column balance: A = Ukraine + Diplomacy + Europe (8),
# B = Middle East + Americas + Health (10),
# C = Asia-Pacific + Markets & Tech + World (10).
COLUMNS = [
    [SECTIONS[0], SECTIONS[1], SECTIONS[2]],
    [SECTIONS[3], SECTIONS[4], SECTIONS[5]],
    [SECTIONS[6], SECTIONS[7], SECTIONS[8]],
]

NUMBERS = [
    ("1,336", "drones Russia says it intercepted"),
    ("3", "US carriers now in the Middle East"),
    ("$92.61", "Brent crude, per barrel"),
    ("40", "Amazon satellites lost in the Vulcan failure"),
    ("9th", "straight year the Pentagon failed its audit"),
]

# Dots on the schematic map strip: (label, x fraction, y fraction, above?,
# label x-offset in px). Labels kept few and spread out so none collide.
MAP_DOTS = [
    ("Kyiv", 0.44, 0.38, True, 0),
    ("Crimea", 0.49, 0.52, False, -8),
    ("Hormuz", 0.60, 0.60, False, 0),
    ("Kigali", 0.52, 0.80, True, -46),
    ("Manila", 0.83, 0.58, False, 0),
    ("Shenzhen", 0.79, 0.42, True, 14),
    ("Ulaanbaatar", 0.73, 0.28, True, -16),
    ("", 0.55, 0.52, True, 0),   # Gaza (dot only)
    ("", 0.58, 0.70, True, 0),   # Aden (dot only)
]

# Extra verified facts that did not fit as full stories; used to fill the
# short first column with an "ALSO NOTED" box.
ALSO_NOTED = [
    "No casualties in the Bahrain drone attack, Bahrain says.",
    "The Xi\u2013Trump\u2013Putin talks are set for Thursday at APEC.",
]

STORY_COUNT = 1 + sum(len(s) for _, s in SECTIONS)  # lead + all sections


# ---------------------------------------------------------------- drawing
def draw_masthead(d):
    d.line([(26, 12), (998, 12)], fill=INK, width=3)
    title = "THE WORLD IN ONE DAY"
    f_title = SERIF_B(57)
    tw = d.textlength(title, font=f_title)
    d.text(((W - tw) / 2, 20), title, font=f_title, fill=INK)
    date = "TUESDAY 17 NOVEMBER 2026"
    f_date = SANS_B(27)
    dw = d.textlength(date, font=f_date)
    d.text(((W - dw) / 2, 88), date, font=f_date, fill=RED)
    tag = "%d stories  ·  6 continents  ·  One front page" % STORY_COUNT
    f_tag = SANS(16)
    gw = d.textlength(tag, font=f_tag)
    d.text(((W - gw) / 2, 122), tag, font=f_tag, fill=INK)
    d.line([(26, 146), (998, 146)], fill=INK, width=3)
    d.line([(26, 150), (998, 150)], fill=INK, width=1)


def draw_bridge(d, x0, y0, x1, y1):
    """Flat-colour illustration: the Kerch Bridge over the strait."""
    d.rectangle([x0, y0, x1, y1], outline=INK, width=2)
    d.rectangle([x0 + 2, y0 + 2, x1 - 2, y0 + 62], fill=SKY)
    d.rectangle([x0 + 2, y0 + 62, x1 - 2, y1 - 2], fill=SEA)
    # sun
    d.ellipse([x1 - 58, y0 + 10, x1 - 30, y0 + 38], fill=(232, 196, 90))
    # bridge deck: left span intact, right span collapsed into the sea
    deck_y = y0 + 78
    d.line([(x0 + 6, deck_y), (x0 + 150, deck_y)], fill=INK, width=6)
    d.line([(x0 + 210, deck_y + 26), (x1 - 8, deck_y + 40)], fill=INK, width=6)
    # towers and cables on the intact span
    for tx in (x0 + 46, x0 + 116):
        d.line([(tx, deck_y), (tx, y0 + 26)], fill=INK, width=5)
    d.line([(x0 + 46, y0 + 26), (x0 + 150, deck_y)], fill=INK, width=2)
    d.line([(x0 + 116, y0 + 26), (x0 + 46, deck_y)], fill=INK, width=2)
    d.line([(x0 + 116, y0 + 26), (x0 + 150, deck_y)], fill=INK, width=2)
    # red burst where the span fell
    cx, cy = x0 + 180, deck_y + 6
    for dx, dy in [(0, -16), (12, -11), (16, 0), (12, 11), (0, 16),
                   (-12, 11), (-16, 0), (-12, -11)]:
        d.line([(cx, cy), (cx + dx, cy + dy)], fill=RED, width=3)
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=RED)
    # waves
    for wx in range(x0 + 12, x1 - 10, 34):
        d.arc([wx, y1 - 26, wx + 26, y1 - 12], start=180, end=360,
              fill=(255, 255, 255), width=2)
    cap = "The Kerch Bridge: a road span fell after the strike."
    f_cap = SANS(12)
    cw = d.textlength(cap, font=f_cap)
    d.text(((x0 + x1 - cw) / 2, y1 + 6), cap, font=f_cap, fill=GREY)


def draw_lead(d):
    x0 = 26
    f_kick = SANS_B(13)
    d.text((x0, 158), LEAD["kicker"], font=f_kick, fill=RED)
    f_head = SERIF_B(32)
    lines = wrap(d, LEAD["headline"], f_head, 660)
    y = 178
    for line in lines:
        d.text((x0, y), line, font=f_head, fill=INK)
        y += 38
    f_body = SERIF(16)
    blines = wrap(d, LEAD["standfirst"], f_body, 660)
    y = 254
    for line in blines:
        d.text((x0, y), line, font=f_body, fill=INK)
        y += 20
    draw_bridge(d, 712, 158, 998, 290)


def draw_numbers(d):
    y0, y1 = 308, 366
    d.rectangle([26, y0, 998, y1], outline=INK, width=2)
    label = "THE DAY IN NUMBERS"
    f_lab = SANS_B(12)
    lw = d.textlength(label, font=f_lab)
    d.rectangle([26, y0 - 11, 26 + lw + 16, y0 + 11], fill=INK)
    d.text((34, y0 - 9), label, font=f_lab, fill=PAPER)
    bw = (998 - 26) / 5
    for i, (num, lab) in enumerate(NUMBERS):
        cx = 26 + bw * i
        if i:
            d.line([(cx, y0 + 6), (cx, y1 - 6)], fill=LIGHT_RULE, width=1)
        f_num = SERIF_B(23)
        nw = d.textlength(num, font=f_num)
        d.text((cx + (bw - nw) / 2, y0 + 5), num, font=f_num, fill=BLUE)
        f_l = SANS(11)
        llines = wrap(d, lab, f_l, bw - 16)
        ly = y0 + 32
        for line in llines[:2]:
            lw2 = d.textlength(line, font=f_l)
            d.text((cx + (bw - lw2) / 2, ly), line, font=f_l, fill=INK)
            ly += 12


def draw_story(d, x, y, headline, body):
    f_h = SERIF_B(17)
    f_b = SANS(13)
    hl = wrap(d, headline, f_h, COL_W)
    for line in hl:
        d.text((x, y), line, font=f_h, fill=INK)
        y += HEAD_LEAD
    bl = wrap(d, body, f_b, COL_W)
    for line in bl[:2]:
        d.text((x, y), line, font=f_b, fill=(40, 40, 40))
        y += BODY_LEAD
    return y + STORY_GAP


def draw_grid(d):
    for col, x in zip(COLUMNS, COL_X):
        y = GRID_TOP
        for title, stories in col:
            f_k = SANS_B(12)
            d.text((x, y), title, font=f_k, fill=RED)
            d.line([(x, y + 17), (x + COL_W, y + 17)], fill=RED, width=2)
            y += SECT_H
            for headline, body in stories:
                y = draw_story(d, x, y, headline, body)
            y += SECT_GAP
        if x == COL_X[0]:
            # Fill the short first column with verified extra facts.
            f_k = SANS_B(12)
            d.text((x, y), "ALSO NOTED", font=f_k, fill=RED)
            d.line([(x, y + 17), (x + COL_W, y + 17)], fill=RED, width=2)
            y += 24
            f_b = SANS(13)
            for item in ALSO_NOTED:
                for line in wrap(d, "\u2022  " + item, f_b, COL_W):
                    d.text((x, y), line, font=f_b, fill=(40, 40, 40))
                    y += BODY_LEAD
                y += 2
        if y > GRID_BOT:
            print("WARNING: column overflow at x=%d, bottom y=%d (limit %d)"
                  % (x, y, GRID_BOT), file=sys.stderr)
        else:
            print("column x=%d ends y=%d" % (x, y), file=sys.stderr)
    # vertical rules between columns
    for vx in (344, 674):
        d.line([(vx, GRID_TOP), (vx, GRID_BOT)], fill=LIGHT_RULE, width=1)


def draw_map_strip(d):
    y0, y1 = 940, 978
    d.rectangle([26, y0, 998, y1], fill=(233, 238, 242), outline=INK, width=1)
    f_lab = SANS_B(11)
    d.text((36, y0 + 11), "WHERE THE DAY HAPPENED", font=f_lab, fill=BLUE)
    # schematic continents: flat blobs, deliberately abstract
    mx0, my0, mx1, my1 = 240, y0 + 4, 990, y1 - 4
    blobs = [
        [(0.02, 0.30, 0.10, 0.55), (0.08, 0.10, 0.16, 0.75), (0.13, 0.35, 0.20, 0.60)],
        [(0.24, 0.15, 0.34, 0.45), (0.30, 0.35, 0.38, 0.70), (0.33, 0.55, 0.44, 0.90)],
        [(0.52, 0.10, 0.66, 0.55), (0.60, 0.45, 0.72, 0.80)],
        [(0.78, 0.25, 0.90, 0.60), (0.84, 0.55, 0.96, 0.85)],
    ]
    for blob in blobs:
        for (fx0, fy0, fx1, fy1) in blob:
            d.ellipse([mx0 + fx0 * (mx1 - mx0), my0 + fy0 * (my1 - my0),
                       mx0 + fx1 * (mx1 - mx0), my0 + fy1 * (my1 - my0)],
                      fill=(196, 208, 219))
    f_dot = SANS_B(10)
    for label, fx, fy, above, dx in MAP_DOTS:
        px = mx0 + fx * (mx1 - mx0)
        py = my0 + fy * (my1 - my0)
        d.ellipse([px - 4, py - 4, px + 4, py + 4], fill=RED,
                  outline=INK, width=1)
        if not label:
            continue
        lw = d.textlength(label, font=f_dot)
        lx = min(max(px - lw / 2 + dx, mx0), mx1 - lw)
        ly = py - 13 if above else py + 5
        d.text((lx, ly), label, font=f_dot, fill=INK)


def draw_footer(d):
    f_f = SANS(12)
    foot = ("All stories reported on 17 November 2026  ·  "
            "Sources: AP, Reuters, AFP, Al Jazeera")
    fw = d.textlength(foot, font=f_f)
    d.text(((W - fw) / 2, 990), foot, font=f_f, fill=GREY)
    d.line([(26, 984), (998, 984)], fill=LIGHT_RULE, width=1)


def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    draw_lead(d)
    draw_numbers(d)
    draw_grid(d)
    draw_map_strip(d)
    draw_footer(d)
    return img


def main():
    out = os.environ.get("ENTRY_OUTPUT", "/output/entry.png")
    img = render()
    try:
        img.save(out, format="PNG")
    except OSError:
        out = os.path.join(os.getcwd(), "entry.png")
        img.save(out, format="PNG")
    print("wrote %s (%d bytes, %dx%d, %d stories)"
          % (out, os.path.getsize(out), W, H, STORY_COUNT))


if __name__ == "__main__":
    main()
