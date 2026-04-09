#!/usr/bin/env python3
"""SafeRoute UI Mockup Generator — Notzeiger Design Philosophy"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math
import os

FONTS = "/Users/sk/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin/f068c39a-40db-4704-874e-a48245c0809b/f3a0a4df-c9d3-4af1-8242-90e7b5f9ac1a/skills/canvas-design/canvas-fonts"

def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)

# Canvas: phone portrait at 2x density
W, H = 828, 1792
img = Image.new("RGB", (W, H), "#0B0D14")
draw = ImageDraw.Draw(img)

# ── Color palette ──────────────────────────────────────────────────────────────
BG         = "#0B0D14"
BG2        = "#10131C"
BG3        = "#151A26"
TEAL       = "#00CFA8"
TEAL_DIM   = "#00876F"
TEAL_FAINT = "#002E26"
SLATE      = "#3D4A5C"
SLATE2     = "#2A3340"
SLATE3     = "#1A2030"
TEXT_MAIN  = "#E2E8F4"
TEXT_DIM   = "#5C6B80"
TEXT_MID   = "#8B9BB4"
ORANGE     = "#FF6B35"
ORANGE_DIM = "#3D1A0A"
WHITE      = "#FFFFFF"

# ── Phone frame ───────────────────────────────────────────────────────────────
FRAME_R = 90
# Outer glow
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
for i in range(20, 0, -1):
    alpha = int(40 * (i / 20))
    gd.rounded_rectangle([-i, -i, W+i, H+i], radius=FRAME_R+i,
                         outline=(0, 207, 168, alpha), width=1)
img = img.convert("RGBA")
img = Image.alpha_composite(img, glow)
img = img.convert("RGB")
draw = ImageDraw.Draw(img)

# Frame border
draw.rounded_rectangle([0, 0, W-1, H-1], radius=FRAME_R,
                        outline=SLATE, width=2)

# Status bar area
STATUS_H = 90
draw.rectangle([0, 0, W, STATUS_H], fill=BG)

# ── Fonts ─────────────────────────────────────────────────────────────────────
f_logo       = font("BigShoulders-Bold.ttf", 52)
f_mono_sm    = font("GeistMono-Regular.ttf", 28)
f_mono_bold  = font("GeistMono-Bold.ttf", 32)
f_label      = font("WorkSans-Regular.ttf", 30)
f_label_bold = font("WorkSans-Bold.ttf", 36)
f_tiny       = font("WorkSans-Regular.ttf", 24)
f_dest       = font("BigShoulders-Bold.ttf", 96)
f_dest_sub   = font("WorkSans-Regular.ttf", 32)
f_update     = font("WorkSans-Regular.ttf", 30)
f_km         = font("GeistMono-Bold.ttf", 68)
f_km_unit    = font("GeistMono-Regular.ttf", 30)
f_heading    = font("BigShoulders-Bold.ttf", 36)

# ── Status bar ─────────────────────────────────────────────────────────────────
# Time
draw.text((60, 28), "09:41", font=f_mono_bold, fill=TEXT_MAIN)
# Signal dots (right side)
for i, filled in enumerate([True, True, True, True, False]):
    x = W - 180 + i * 26
    col = TEXT_MAIN if filled else SLATE
    draw.ellipse([x, 38, x+14, 52], fill=col)
# Battery
bx = W - 80
draw.rounded_rectangle([bx, 34, bx+52, 52], radius=5, outline=TEXT_MID, width=2)
draw.rectangle([bx+2, 36, bx+38, 50], fill=TEAL)
draw.rounded_rectangle([bx+53, 39, bx+58, 47], radius=2, fill=TEXT_MID)

# ── Map area ──────────────────────────────────────────────────────────────────
MAP_TOP = STATUS_H + 10
MAP_BOT = 1050

# Map base
draw.rectangle([0, MAP_TOP, W, MAP_BOT], fill=BG3)

# Grid lines (cartographic feel)
for x in range(0, W, 55):
    draw.line([(x, MAP_TOP), (x, MAP_BOT)], fill=SLATE3, width=1)
for y in range(MAP_TOP, MAP_BOT, 55):
    draw.line([(0, y), (W, y)], fill=SLATE3, width=1)

# Roads (background street network — muted)
road_color = SLATE2
road_thin = "#1E2535"

# Major roads
roads = [
    # [x1, y1, x2, y2, width, color]
    [0,    600, W,    580, 8,  road_color],
    [0,    700, W,    720, 6,  road_thin],
    [200,  MAP_TOP, 180, MAP_BOT, 8,  road_color],
    [420,  MAP_TOP, 440, MAP_BOT, 6,  road_thin],
    [600,  MAP_TOP, 620, MAP_BOT, 8,  road_color],
    [0,    820, W,    800, 5,  road_thin],
    [0,    930, 500,  910, 5,  road_thin],
    [300,  MAP_TOP, 310, 700, 4, road_thin],
    [500,  MAP_TOP, 520, 650, 4, road_thin],
    [700,  MAP_TOP, 690, MAP_BOT, 4, road_thin],
    [0,    480, 500,  500, 4, road_thin],
]
for r in roads:
    draw.line([(r[0], r[1]), (r[2], r[3])], fill=r[5], width=r[4])

# City blocks (subtle)
blocks = [
    [230, 450, 380, 550],
    [450, 430, 560, 560],
    [640, 450, 760, 540],
    [50,  640, 160, 730],
    [50,  750, 170, 820],
    [230, 640, 380, 720],
    [450, 640, 540, 740],
    [640, 640, 750, 730],
    [50,  850, 160, 930],
    [640, 850, 760, 940],
    [230, 850, 370, 930],
]
for b in blocks:
    draw.rectangle(b, fill=SLATE3)

# Danger zone overlay (red/orange polygon — a blocked area)
dz_points = [(480, 680), (620, 660), (650, 780), (590, 820), (460, 800)]
dz_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
dz_draw = ImageDraw.Draw(dz_overlay)
dz_draw.polygon(dz_points, fill=(255, 107, 53, 35))
dz_draw.polygon(dz_points, outline=(255, 107, 53, 120), width=2)
img_rgba = img.convert("RGBA")
img_rgba = Image.alpha_composite(img_rgba, dz_overlay)
img = img_rgba.convert("RGB")
draw = ImageDraw.Draw(img)

# Danger zone label
draw.text((510, 720), "SPERRZONE", font=font("WorkSans-Regular.ttf", 20),
          fill="#FF6B35")

# ── Active route line ─────────────────────────────────────────────────────────
# Route path: from bottom-center, curves around danger zone, heads NE toward border
route_pts = [
    (414, 980),  # start (user position)
    (400, 900),
    (380, 820),
    (360, 760),
    (340, 700),
    (310, 650),
    (290, 600),
    (260, 540),
    (240, 480),
    (230, 420),
    (220, 360),
    (210, 300),
    (200, 240),
    (195, MAP_TOP + 20),  # border crossing (top of map)
]

# Glow effect for route
route_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
rg_draw = ImageDraw.Draw(route_glow)
for thickness, alpha in [(24, 15), (16, 30), (10, 50), (6, 80)]:
    rg_draw.line(route_pts, fill=(0, 207, 168, alpha), width=thickness, joint="curve")
img_rgba = img.convert("RGBA")
img_rgba = Image.alpha_composite(img_rgba, route_glow)
img = img_rgba.convert("RGB")
draw = ImageDraw.Draw(img)

# Core route line
draw.line(route_pts, fill=TEAL, width=5, joint="curve")

# Route direction chevrons
for i in range(2, len(route_pts) - 1, 2):
    x1, y1 = route_pts[i-1]
    x2, y2 = route_pts[i]
    dx, dy = x2 - x1, y2 - y1
    length = math.sqrt(dx*dx + dy*dy)
    if length < 1:
        continue
    nx, ny = dx/length, dy/length
    mx, my = (x1+x2)//2, (y1+y2)//2
    px, py = -ny, nx
    size = 8
    p1 = (int(mx - nx*size), int(my - ny*size))
    p2 = (int(mx + px*size*0.6), int(my + py*size*0.6))
    p3 = (int(mx - px*size*0.6), int(my - py*size*0.6))
    draw.polygon([p1, p2, p3], fill=TEAL_DIM)

# ── User location dot ─────────────────────────────────────────────────────────
ux, uy = 414, 980
# Pulse rings
pulse = Image.new("RGBA", (W, H), (0, 0, 0, 0))
pd = ImageDraw.Draw(pulse)
for r, a in [(50, 15), (35, 25), (22, 40)]:
    pd.ellipse([ux-r, uy-r, ux+r, uy+r], outline=(0, 207, 168, a), width=2)
img_rgba = img.convert("RGBA")
img_rgba = Image.alpha_composite(img_rgba, pulse)
img = img_rgba.convert("RGB")
draw = ImageDraw.Draw(img)
# Core dot
draw.ellipse([ux-12, uy-12, ux+12, uy+12], fill=WHITE)
draw.ellipse([ux-8, uy-8, ux+8, uy+8], fill=TEAL)

# ── Border crossing marker (top of route) ─────────────────────────────────────
bx, by = 195, MAP_TOP + 20
draw.ellipse([bx-14, by-14, bx+14, by+14], fill=TEAL, outline=WHITE, width=2)
draw.text((bx + 20, by - 14), "GRENZE / CH", font=font("GeistMono-Regular.ttf", 22),
          fill=TEXT_MID)

# ── Top header bar ────────────────────────────────────────────────────────────
HEADER_H = 80
header_y = STATUS_H
draw.rectangle([0, header_y, W, header_y + HEADER_H], fill=BG)

# Logo
draw.text((60, header_y + 14), "SAFE", font=f_logo, fill=TEXT_MAIN)
draw.text((60 + 130, header_y + 14), "ROUTE", font=f_logo, fill=TEAL)

# Sync indicator
sync_x = W - 320
sync_y = header_y + 26
# Green dot
draw.ellipse([sync_x, sync_y + 4, sync_x + 12, sync_y + 16], fill=TEAL)
draw.text((sync_x + 20, sync_y), "vor 3 Min.", font=f_mono_sm, fill=TEXT_MID)

# ── Separator line ────────────────────────────────────────────────────────────
draw.line([(60, header_y + HEADER_H - 1), (W - 60, header_y + HEADER_H - 1)],
          fill=SLATE3, width=1)

# ── Bottom info panel ─────────────────────────────────────────────────────────
PANEL_TOP = MAP_BOT
PANEL_BOT = H - 80

draw.rectangle([0, PANEL_TOP, W, PANEL_BOT], fill=BG2)

# Top border teal accent
draw.line([(0, PANEL_TOP), (W, PANEL_TOP)], fill=TEAL, width=2)

# Destination
dest_y = PANEL_TOP + 40
draw.text((60, dest_y), "SCHWEIZ", font=f_dest, fill=TEXT_MAIN)
draw.text((60, dest_y + 100), "Nächste sichere Grenze — automatisch gewählt",
          font=f_dest_sub, fill=TEXT_MID)

# Divider
draw.line([(60, dest_y + 148), (W - 60, dest_y + 148)], fill=SLATE3, width=1)

# Stats row
stats_y = dest_y + 170

# Distance
draw.text((60, stats_y), "247", font=f_km, fill=TEXT_MAIN)
draw.text((168, stats_y + 36), "km", font=f_km_unit, fill=TEXT_MID)

# Vertical divider
draw.line([(W//2, stats_y + 10), (W//2, stats_y + 80)], fill=SLATE2, width=1)

# ETA
draw.text((W//2 + 40, stats_y), "3h 20m", font=f_km, fill=TEXT_MAIN)
draw.text((W//2 + 196, stats_y + 36), "ETA", font=f_km_unit, fill=TEXT_MID)

# Route update notice
update_y = stats_y + 110
draw.text((60, update_y), "Route aktualisiert.", font=f_update, fill=TEXT_DIM)

# ── Bottom home indicator ─────────────────────────────────────────────────────
draw.rectangle([0, PANEL_BOT, W, H], fill=BG)
home_w = 140
home_x = (W - home_w) // 2
draw.rounded_rectangle([home_x, PANEL_BOT + 24, home_x + home_w, PANEL_BOT + 36],
                        radius=6, fill=SLATE)

# ── Coordinate grid overlay (cartographic feel) ──────────────────────────────
# Subtle degree markers on map edges
for i, lat in enumerate(["48°N", "47°N", "46°N"]):
    y = MAP_TOP + 80 + i * 280
    draw.text((W - 84, y), lat, font=font("GeistMono-Regular.ttf", 18),
              fill=TEXT_DIM)

# ── Final mask to phone shape ─────────────────────────────────────────────────
mask = Image.new("L", (W, H), 0)
mask_d = ImageDraw.Draw(mask)
mask_d.rounded_rectangle([0, 0, W-1, H-1], radius=FRAME_R, fill=255)
img.putalpha(mask)

# Save on white background for clean output
bg = Image.new("RGB", (W, H), "#0B0D14")
bg.paste(img, mask=img.split()[3])

# ── Output ────────────────────────────────────────────────────────────────────
out = "/Users/sk/Downloads/saferoute_ui_mockup.png"
bg.save(out, "PNG", dpi=(144, 144))
print(f"Saved: {out}")
