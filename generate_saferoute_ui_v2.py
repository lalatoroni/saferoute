#!/usr/bin/env python3
"""SafeRoute UI Mockup v2 — Notzeiger Design Philosophy"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, os

FONTS = "/Users/sk/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin/f068c39a-40db-4704-874e-a48245c0809b/f3a0a4df-c9d3-4af1-8242-90e7b5f9ac1a/skills/canvas-design/canvas-fonts"

def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)

W, H = 828, 1792

# ── Palette ───────────────────────────────────────────────────────────────────
BG      = "#0C0F18"
BG2     = "#0F1320"
MAP_BG  = "#0E1220"
GRID    = "#161C2A"
ROAD_MJ = "#242E40"
ROAD_MN = "#1A2234"
BLOCK   = "#131826"
WATER   = "#0A1020"
TEAL    = "#00CFA8"
TEAL_D  = "#007A65"
TEAL_F  = "#003028"
SLATE   = "#3A4A5C"
T_MAIN  = "#E4EAF6"
T_MID   = "#7A8CA0"
T_DIM   = "#3E4E60"
ORANGE  = "#FF6B35"
ORG_F   = "#2A1008"

# ── Canvas ────────────────────────────────────────────────────────────────────
img = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(img)

FRAME_R   = 88
STATUS_H  = 96
HEADER_H  = 88
MAP_TOP   = STATUS_H + HEADER_H
MAP_BOT   = 1090
PANEL_BOT = H - 70

# ── Map fill ──────────────────────────────────────────────────────────────────
draw.rectangle([0, MAP_TOP, W, MAP_BOT], fill=MAP_BG)

# Fine grid
for x in range(0, W, 44):
    draw.line([(x, MAP_TOP), (x, MAP_BOT)], fill=GRID, width=1)
for y in range(MAP_TOP, MAP_BOT, 44):
    draw.line([(0, y), (W, y)], fill=GRID, width=1)

# Water body (river / lake — bottom-right quad)
river_pts = [(540, MAP_BOT), (580, 900), (620, 820), (660, 750),
             (700, 700), (750, 650), (W, 610), (W, MAP_BOT)]
draw.polygon(river_pts, fill=WATER)
# Subtle water lines
for i in range(3):
    y_off = 30 + i * 28
    draw.line([(580, 900 - y_off), (W, 610 - y_off*0.6)],
              fill="#0D1628", width=2)

# ── Road network ──────────────────────────────────────────────────────────────
def road(pts, w, c):
    draw.line(pts, fill=c, width=w, joint="curve")

# Motorways / major roads
road([(0, 580), (W, 555)], 12, ROAD_MJ)
road([(0, 760), (W, 740)], 10, ROAD_MJ)
road([(160, MAP_TOP), (140, MAP_BOT)], 12, ROAD_MJ)
road([(380, MAP_TOP), (400, MAP_BOT)], 10, ROAD_MJ)
road([(590, MAP_TOP), (610, MAP_BOT)], 12, ROAD_MJ)
# Secondary roads
road([(0, 480), (400, 500)], 6, ROAD_MN)
road([(0, 660), (W, 645)], 6, ROAD_MN)
road([(0, 870), (560, 850)], 6, ROAD_MN)
road([(0, 970), (400, 960)], 5, ROAD_MN)
road([(260, MAP_TOP), (255, 700)], 5, ROAD_MN)
road([(490, MAP_TOP), (505, 650)], 5, ROAD_MN)
road([(700, MAP_TOP), (715, 720)], 5, ROAD_MN)
road([(50, 530), (160, 500)], 4, ROAD_MN)

# ── City blocks ───────────────────────────────────────────────────────────────
blocks = [
    # col1
    [20, 450, 118, 530], [20, 550, 118, 620], [20, 640, 118, 720],
    [20, 790, 118, 845], [20, 890, 118, 950],
    # col2
    [175, 420, 248, 510], [175, 535, 248, 620], [175, 640, 248, 720],
    [175, 780, 248, 840], [175, 890, 248, 960],
    # col3
    [285, 420, 355, 530], [285, 545, 350, 625], [285, 640, 352, 730],
    [285, 790, 356, 845], [285, 880, 356, 950],
    # col4
    [420, 420, 500, 515], [420, 540, 500, 625], [420, 645, 495, 710],
    # col5 (left of river)
    [620, 420, 690, 515], [620, 540, 688, 625],
    [620, 645, 688, 705],
]
for b in blocks:
    draw.rectangle(b, fill=BLOCK)
    # subtle edge highlight
    draw.rectangle([b[0], b[1], b[2], b[1]+2], fill=ROAD_MN)

# ── Danger zone ───────────────────────────────────────────────────────────────
dz = [(430, 630), (530, 610), (570, 680), (555, 770), (480, 800), (410, 760)]
dz_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
dz_d = ImageDraw.Draw(dz_overlay)
dz_d.polygon(dz, fill=(255, 107, 53, 30))
for thick, alpha in [(10, 10), (4, 60), (2, 140)]:
    dz_d.polygon(dz, outline=(255, 107, 53, alpha), width=thick)
img = Image.alpha_composite(img.convert("RGBA"), dz_overlay).convert("RGB")
draw = ImageDraw.Draw(img)

# Warning label
draw.text((444, 700), "SPERRZONE", font=font("GeistMono-Regular.ttf", 22),
          fill=ORANGE)

# ── Lat markers ───────────────────────────────────────────────────────────────
for lat, y in [("48°N", MAP_TOP + 60), ("47°N", MAP_TOP + 310),
               ("46°N", MAP_TOP + 560)]:
    draw.text((W - 78, y), lat,
              font=font("GeistMono-Regular.ttf", 20), fill=T_DIM)

# ── Active route ─────────────────────────────────────────────────────────────
route = [
    (380, 1010),
    (368, 940), (350, 880), (332, 820), (314, 760),
    (296, 700), (278, 640), (264, 575),
    (248, 510), (234, 445), (218, 375),
    (206, 310), (196, 248), (188, MAP_TOP + 18),
]

# Multi-layer glow
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
for w_px, a in [(36, 8), (24, 16), (14, 32), (8, 55)]:
    gd.line(route, fill=(0, 207, 168, a), width=w_px, joint="curve")
img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
draw = ImageDraw.Draw(img)

# Core line
draw.line(route, fill=TEAL, width=5, joint="curve")

# ── Direction arrows ─────────────────────────────────────────────────────────
for i in range(2, len(route) - 1, 3):
    x0, y0 = route[i-1]
    x1, y1 = route[i]
    dx, dy = x1-x0, y1-y0
    ln = math.sqrt(dx*dx + dy*dy)
    if ln < 1: continue
    nx, ny = dx/ln, dy/ln
    px, py = -ny, nx
    mx, my = (x0+x1)/2, (y0+y1)/2
    s = 9
    p1 = (int(mx - nx*s), int(my - ny*s))
    p2 = (int(mx + px*s*0.55 + nx*s), int(my + py*s*0.55 + ny*s))
    p3 = (int(mx - px*s*0.55 + nx*s), int(my - py*s*0.55 + ny*s))
    draw.polygon([p1, p2, p3], fill=TEAL_D)

# ── User dot ─────────────────────────────────────────────────────────────────
ux, uy = 380, 1010
pulse = Image.new("RGBA", (W, H), (0, 0, 0, 0))
pd = ImageDraw.Draw(pulse)
for r, a in [(52, 10), (36, 22), (22, 40)]:
    pd.ellipse([ux-r, uy-r, ux+r, uy+r], outline=(0, 207, 168, a), width=2)
img = Image.alpha_composite(img.convert("RGBA"), pulse).convert("RGB")
draw = ImageDraw.Draw(img)
draw.ellipse([ux-14, uy-14, ux+14, uy+14], fill="#FFFFFF")
draw.ellipse([ux-9,  uy-9,  ux+9,  uy+9],  fill=TEAL)

# ── Border marker ─────────────────────────────────────────────────────────────
bx, by = 188, MAP_TOP + 18
draw.ellipse([bx-16, by-16, bx+16, by+16], fill=TEAL, outline="#FFFFFF", width=2)
draw.text((bx+26, by-14), "CH  Grenzübergang",
          font=font("GeistMono-Regular.ttf", 24), fill=T_MID)

# ── Compass ──────────────────────────────────────────────────────────────────
cx, cy, cr = W - 90, MAP_BOT - 110, 52
# Outer ring
compass_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
cl = ImageDraw.Draw(compass_layer)
cl.ellipse([cx-cr, cy-cr, cx+cr, cy+cr], fill=(12, 15, 24, 210))
cl.ellipse([cx-cr, cy-cr, cx+cr, cy+cr], outline=(58, 74, 92, 200), width=2)
# N needle (teal, pointing up)
n_tip  = (cx, cy - int(cr * 0.72))
n_bl   = (cx - 10, cy + 6)
n_br   = (cx + 10, cy + 6)
n_mid  = (cx, cy - 4)
cl.polygon([n_tip, n_bl, n_mid], fill=(0, 207, 168, 230))
cl.polygon([n_tip, n_br, n_mid], fill=(0, 157, 128, 230))
# S needle (slate)
s_tip  = (cx, cy + int(cr * 0.72))
s_bl   = (cx - 10, cy - 6)
s_br   = (cx + 10, cy - 6)
s_mid  = (cx, cy + 4)
cl.polygon([s_tip, s_bl, s_mid], fill=(42, 51, 64, 230))
cl.polygon([s_tip, s_br, s_mid], fill=(58, 74, 92, 230))
# Center dot
cl.ellipse([cx-5, cy-5, cx+5, cy+5], fill=(200, 210, 220, 255))
# N label
compass_fnt = font("GeistMono-Bold.ttf", 22)
cl.text((cx - 8, cy - cr - 26), "N", font=compass_fnt, fill=(0, 207, 168, 220))
img = Image.alpha_composite(img.convert("RGBA"), compass_layer).convert("RGB")
draw = ImageDraw.Draw(img)

# ── Map fade (top + bottom) ───────────────────────────────────────────────────
for y_start, y_end, direction in [
    (MAP_TOP, MAP_TOP+80, "down"),
    (MAP_BOT-80, MAP_BOT, "up")
]:
    fade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fade)
    steps = 80
    for i in range(steps):
        alpha = int(200 * (1 - i/steps)) if direction == "down" else int(200 * i/steps)
        y = y_start + i if direction == "down" else y_end - steps + i
        fd.rectangle([0, y, W, y+1], fill=(12, 15, 24, alpha))
    img = Image.alpha_composite(img.convert("RGBA"), fade).convert("RGB")
    draw = ImageDraw.Draw(img)

# ── Status bar ────────────────────────────────────────────────────────────────
draw.rectangle([0, 0, W, STATUS_H], fill=BG)
draw.text((62, 30), "09:41", font=font("GeistMono-Bold.ttf", 38), fill=T_MAIN)
# Signal bars
bx_sig = W - 190
for i, h in enumerate([10, 14, 18, 22]):
    bx_s = bx_sig + i * 20
    filled = i < 3
    draw.rectangle([bx_s, 44+(22-h), bx_s+12, 66], fill=T_MAIN if filled else SLATE)
# Battery
bat = W - 74
draw.rounded_rectangle([bat, 38, bat+48, 58], radius=5, outline=T_MID, width=2)
draw.rectangle([bat+3, 41, bat+36, 55], fill=TEAL)
draw.rounded_rectangle([bat+49, 44, bat+54, 52], radius=2, fill=T_MID)

# ── Header bar ────────────────────────────────────────────────────────────────
hy = STATUS_H
draw.rectangle([0, hy, W, hy+HEADER_H], fill=BG)
# Bottom hairline
draw.line([(44, hy+HEADER_H-1), (W-44, hy+HEADER_H-1)], fill=ROAD_MN, width=1)

draw.text((62, hy+16), "SAFE", font=font("BigShoulders-Bold.ttf", 56), fill=T_MAIN)
draw.text((62+144, hy+16), "ROUTE", font=font("BigShoulders-Bold.ttf", 56), fill=TEAL)

# Sync status — right side
sx = W - 300
sy = hy + 30
draw.ellipse([sx, sy+2, sx+14, sy+16], fill=TEAL)
draw.text((sx+22, sy), "vor 3 Min.", font=font("GeistMono-Regular.ttf", 28),
          fill=T_MID)

# ── Bottom panel ─────────────────────────────────────────────────────────────
draw.rectangle([0, MAP_BOT, W, PANEL_BOT], fill=BG2)
# Teal top accent
draw.line([(0, MAP_BOT), (W, MAP_BOT)], fill=TEAL, width=3)

# Destination name
draw.text((62, MAP_BOT + 38), "SCHWEIZ",
          font=font("BigShoulders-Bold.ttf", 102), fill=T_MAIN)

draw.text((62, MAP_BOT + 148),
          "Nächste sichere Grenze  —  automatisch",
          font=font("WorkSans-Regular.ttf", 30), fill=T_MID)
draw.text((62, MAP_BOT + 184), "ermittelt aus deinem Standort",
          font=font("WorkSans-Regular.ttf", 30), fill=T_DIM)

# Divider
div_y = MAP_BOT + 230
draw.line([(62, div_y), (W-62, div_y)], fill=ROAD_MJ, width=1)

# Stats: distance | ETA
stats_y = div_y + 28
mid = W // 2

# Distance
draw.text((62, stats_y), "247",
          font=font("GeistMono-Bold.ttf", 80), fill=T_MAIN)
draw.text((62+180, stats_y+42), "KM",
          font=font("GeistMono-Regular.ttf", 28), fill=T_MID)
draw.text((62, stats_y+88), "Distanz",
          font=font("WorkSans-Regular.ttf", 28), fill=T_DIM)

# Vertical separator
draw.line([(mid, stats_y+8), (mid, stats_y+108)], fill=ROAD_MJ, width=1)

# ETA
draw.text((mid+40, stats_y), "3h 20",
          font=font("GeistMono-Bold.ttf", 80), fill=T_MAIN)
draw.text((mid+236, stats_y+42), "MIN",
          font=font("GeistMono-Regular.ttf", 28), fill=T_MID)
draw.text((mid+40, stats_y+88), "Fahrzeit",
          font=font("WorkSans-Regular.ttf", 28), fill=T_DIM)

# Divider
div2_y = stats_y + 126
draw.line([(62, div2_y), (W-62, div2_y)], fill=ROAD_MJ, width=1)

# Route update notice
update_y = div2_y + 24
draw.text((62, update_y), "Route aktualisiert.",
          font=font("WorkSans-Regular.ttf", 30), fill=T_DIM)

# Next waypoint hint
draw.text((W-62-260, update_y), "via A3 · A1",
          font=font("GeistMono-Regular.ttf", 28), fill=T_DIM)

# ── Home indicator ────────────────────────────────────────────────────────────
draw.rectangle([0, PANEL_BOT, W, H], fill=BG)
hw = 130
hx = (W - hw) // 2
draw.rounded_rectangle([hx, PANEL_BOT+22, hx+hw, PANEL_BOT+34], radius=6, fill=SLATE)

# ── Phone frame ───────────────────────────────────────────────────────────────
draw.rounded_rectangle([0, 0, W-1, H-1], radius=FRAME_R, outline="#2A3444", width=3)

# ── Final mask ────────────────────────────────────────────────────────────────
mask = Image.new("L", (W, H), 0)
mask_d = ImageDraw.Draw(mask)
mask_d.rounded_rectangle([0, 0, W-1, H-1], radius=FRAME_R, fill=255)
img.putalpha(mask)

out_img = Image.new("RGB", (W, H), BG)
out_img.paste(img, mask=img.split()[3])
out_img.save("/Users/sk/Downloads/saferoute_ui_mockup.png", "PNG", dpi=(144, 144))
print("Saved: /Users/sk/Downloads/saferoute_ui_mockup.png")
