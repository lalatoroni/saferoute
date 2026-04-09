#!/usr/bin/env python3
"""SafeRoute — Onboarding + Main Screen nebeneinander"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, os

FONTS = "/Users/sk/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin/f068c39a-40db-4704-874e-a48245c0809b/f3a0a4df-c9d3-4af1-8242-90e7b5f9ac1a/skills/canvas-design/canvas-fonts"

def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)

# Phone dimensions
PW, PH = 414, 896  # logical size (will be 2x)
SCALE = 2
W, H = PW * SCALE, PH * SCALE
FRAME_R = 76

# Palette
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
SLATE   = "#3A4A5C"
SLATE2  = "#2A3340"
SLATE3  = "#1A2030"
T_MAIN  = "#E4EAF6"
T_MID   = "#7A8CA0"
T_DIM   = "#3E4E60"
ORANGE  = "#FF6B35"

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def make_phone_mask(w, h, r):
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w-1, h-1], radius=r, fill=255)
    return mask

# ─────────────────────────────────────────────
# SCREEN 1: ONBOARDING
# ─────────────────────────────────────────────
def draw_onboarding():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # Status bar
    STATUS_H = 80
    d.rectangle([0, 0, W, STATUS_H], fill=BG)
    d.text((52, 24), "09:41", font=font("GeistMono-Bold.ttf", 36), fill=T_MAIN)
    # battery minimal
    bx = W - 68
    d.rounded_rectangle([bx, 30, bx+46, 50], radius=5, outline=T_MID, width=2)
    d.rectangle([bx+3, 33, bx+35, 47], fill=TEAL)
    d.rounded_rectangle([bx+47, 36, bx+52, 44], radius=2, fill=T_MID)

    # Logo area
    d.text((52, STATUS_H + 40), "SAFE", font=font("BigShoulders-Bold.ttf", 48), fill=T_MAIN)
    d.text((52 + 122, STATUS_H + 40), "ROUTE", font=font("BigShoulders-Bold.ttf", 48), fill=TEAL)

    # Subtle divider
    d.line([(52, STATUS_H + 108), (W - 52, STATUS_H + 108)], fill=SLATE3, width=1)

    # ── Trust content ──
    y = STATUS_H + 148

    # Section: was wir wissen
    d.text((52, y), "Was SafeRoute über dich weiß:",
           font=font("WorkSans-Regular.ttf", 28), fill=T_MID)
    y += 44
    for item in ["Deinen Standort  (nur lokal)", "Dein Gerät"]:
        # dot
        d.ellipse([52, y + 10, 66, y + 24], outline=T_MID, width=2)
        d.text((82, y), item, font=font("WorkSans-Regular.ttf", 32), fill=T_MAIN)
        y += 48
    y += 28

    # Section: was wir NIE wissen
    d.text((52, y), "Was SafeRoute nie wissen wird:",
           font=font("WorkSans-Regular.ttf", 28), fill=T_MID)
    y += 44
    for item in ["Deinen Namen", "Deine Route  (kein Upload)", "Irgendetwas über dich"]:
        # teal dot
        d.ellipse([52, y + 10, 66, y + 24], fill=TEAL)
        d.text((82, y), item, font=font("WorkSans-Regular.ttf", 32), fill=TEAL)
        y += 48
    y += 40

    # Privacy note
    note = "Deine Daten verlassen nie dein Gerät."
    d.text((52, y), note, font=font("WorkSans-Regular.ttf", 24), fill=T_DIM)
    y += 36
    d.text((52, y), "Keine Cloud. Kein Account. Keine Werbung.",
           font=font("WorkSans-Regular.ttf", 24), fill=T_DIM)

    # ── CTA Button ──
    btn_y = H - 240
    btn_margin = 52
    # Glow behind button
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for i in range(20, 0, -1):
        alpha = int(25 * (i / 20))
        gd.rounded_rectangle(
            [btn_margin - i, btn_y - i, W - btn_margin + i, btn_y + 76 + i],
            radius=18 + i, fill=(0, 207, 168, alpha)
        )
    img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
    d = ImageDraw.Draw(img)

    d.rounded_rectangle([btn_margin, btn_y, W - btn_margin, btn_y + 76],
                        radius=16, fill=TEAL)
    btn_text = "Ich bin dabei"
    btn_font = font("BigShoulders-Bold.ttf", 46)
    bbox = d.textbbox((0, 0), btn_text, font=btn_font)
    tw = bbox[2] - bbox[0]
    d.text(((W - tw) // 2, btn_y + 14), btn_text, font=btn_font, fill=BG)

    # Hint below button
    d.text((0, btn_y + 92), "GPS-Berechtigung wird nach dem Tap abgefragt",
           font=font("WorkSans-Regular.ttf", 22), fill=T_DIM)
    # Center that text
    hint_font = font("WorkSans-Regular.ttf", 22)
    hbbox = d.textbbox((0, 0), "GPS-Berechtigung wird nach dem Tap abgefragt", font=hint_font)
    hw = hbbox[2] - hbbox[0]
    d.text(((W - hw) // 2, btn_y + 94),
           "GPS-Berechtigung wird nach dem Tap abgefragt",
           font=hint_font, fill=T_DIM)

    # Home indicator
    hiw = 120
    hix = (W - hiw) // 2
    d.rounded_rectangle([hix, H - 32, hix + hiw, H - 20], radius=6, fill=SLATE)

    # Frame
    d.rounded_rectangle([0, 0, W-1, H-1], radius=FRAME_R, outline=SLATE2, width=3)

    # Mask
    mask = make_phone_mask(W, H, FRAME_R)
    out = Image.new("RGB", (W, H), BG)
    out.paste(img, mask=mask)
    return out

# ─────────────────────────────────────────────
# SCREEN 2: MAIN NAVIGATION
# ─────────────────────────────────────────────
def draw_main():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    STATUS_H  = 80
    HEADER_H  = 80
    MAP_TOP   = STATUS_H + HEADER_H
    MAP_BOT   = int(H * 0.595)

    # Map base
    d.rectangle([0, MAP_TOP, W, MAP_BOT], fill=MAP_BG)
    for x in range(0, W, 40):
        d.line([(x, MAP_TOP), (x, MAP_BOT)], fill=GRID, width=1)
    for y in range(MAP_TOP, MAP_BOT, 40):
        d.line([(0, y), (W, y)], fill=GRID, width=1)

    # Water
    river = [(460, MAP_BOT), (490, 680), (520, 610), (560, 555),
             (600, 510), (650, 470), (W, 440), (W, MAP_BOT)]
    d.polygon(river, fill=WATER)

    # Roads
    roads = [
        [(0, 420), (W, 405), 10, ROAD_MJ],
        [(0, 540), (W, 525), 8, ROAD_MJ],
        [(0, 630), (W, 615), 7, ROAD_MJ],
        [(120, MAP_TOP), (110, MAP_BOT), 10, ROAD_MJ],
        [(300, MAP_TOP), (315, MAP_BOT), 8, ROAD_MJ],
        [(470, MAP_TOP), (490, MAP_BOT), 10, ROAD_MJ],
        [(0, 470), (310, 485), 5, ROAD_MN],
        [(0, 580), (W, 568), 5, ROAD_MN],
        [(0, 700), (430, 688), 5, ROAD_MN],
        [(200, MAP_TOP), (196, 530), 4, ROAD_MN],
        [(400, MAP_TOP), (408, 480), 4, ROAD_MN],
        [(600, MAP_TOP), (615, MAP_BOT), 4, ROAD_MN],
    ]
    for r in roads:
        d.line([r[0], r[1]], fill=r[3], width=r[2], joint="curve")

    # Blocks
    blocks = [
        [20,380,90,455],[20,500,90,565],[20,590,90,645],[20,680,90,725],
        [135,380,188,455],[135,500,188,570],[135,590,188,645],[135,680,188,728],
        [215,380,278,455],[215,500,275,568],[215,590,275,643],[215,680,275,726],
        [330,375,390,455],[330,495,388,567],[330,590,388,643],
        [500,375,558,452],[500,495,556,565],[500,590,558,642],
    ]
    for b in blocks:
        d.rectangle(b, fill=BLOCK)
        d.rectangle([b[0], b[1], b[2], b[1]+1], fill=ROAD_MN)

    # Danger zone
    dz = [(330, 500), (420, 482), (450, 548), (438, 618), (370, 638), (310, 596)]
    dz_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dzd = ImageDraw.Draw(dz_layer)
    dzd.polygon(dz, fill=(255, 107, 53, 28))
    for thick, alpha in [(10, 8), (4, 55), (2, 130)]:
        dzd.polygon(dz, outline=(255, 107, 53, alpha), width=thick)
    img = Image.alpha_composite(img.convert("RGBA"), dz_layer).convert("RGB")
    d = ImageDraw.Draw(img)
    d.text((344, 552), "SPERRZONE",
           font=font("GeistMono-Regular.ttf", 18), fill=ORANGE)

    # Lat markers
    for lat, y in [("48°N", MAP_TOP+44), ("47°N", MAP_TOP+240), ("46°N", MAP_TOP+435)]:
        d.text((W - 68, y), lat, font=font("GeistMono-Regular.ttf", 18), fill=T_DIM)

    # Route
    route = [
        (290, 730), (278, 680), (262, 630), (245, 575),
        (228, 520), (212, 460), (196, 398),
        (180, 338), (168, 278), (158, MAP_TOP + 14),
    ]
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for w_px, a in [(30, 8), (20, 18), (12, 35), (6, 60)]:
        gd.line(route, fill=(0, 207, 168, a), width=w_px, joint="curve")
    img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
    d = ImageDraw.Draw(img)
    d.line(route, fill=TEAL, width=5, joint="curve")

    # Chevrons
    for i in range(2, len(route)-1, 2):
        x0, y0 = route[i-1]; x1, y1 = route[i]
        dx, dy = x1-x0, y1-y0
        ln = math.sqrt(dx*dx+dy*dy)
        if ln < 1: continue
        nx, ny = dx/ln, dy/ln
        px, py = -ny, nx
        mx, my = (x0+x1)/2, (y0+y1)/2
        s = 7
        p1 = (int(mx-nx*s), int(my-ny*s))
        p2 = (int(mx+px*s*0.55+nx*s), int(my+py*s*0.55+ny*s))
        p3 = (int(mx-px*s*0.55+nx*s), int(my-py*s*0.55+ny*s))
        d.polygon([p1, p2, p3], fill=TEAL_D)

    # User dot
    ux, uy = 290, 730
    pulse = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pulse)
    for r, a in [(44, 8), (30, 20), (18, 38)]:
        pd.ellipse([ux-r, uy-r, ux+r, uy+r], outline=(0,207,168,a), width=2)
    img = Image.alpha_composite(img.convert("RGBA"), pulse).convert("RGB")
    d = ImageDraw.Draw(img)
    d.ellipse([ux-12, uy-12, ux+12, uy+12], fill="#FFFFFF")
    d.ellipse([ux-8, uy-8, ux+8, uy+8], fill=TEAL)

    # Border marker
    bx, by = 158, MAP_TOP + 14
    d.ellipse([bx-13, by-13, bx+13, by+13], fill=TEAL, outline="#FFFFFF", width=2)
    d.text((bx+20, by-12), "CH  Grenzübergang",
           font=font("GeistMono-Regular.ttf", 20), fill=T_MID)

    # Map fades
    for (yt, yb, direct) in [(MAP_TOP, MAP_TOP+70, "down"), (MAP_BOT-70, MAP_BOT, "up")]:
        fade = Image.new("RGBA", (W, H), (0,0,0,0))
        fd = ImageDraw.Draw(fade)
        steps = 70
        for i in range(steps):
            a = int(180*(1-i/steps)) if direct=="down" else int(180*i/steps)
            y_line = yt+i if direct=="down" else yb-steps+i
            fd.rectangle([0,y_line,W,y_line+1], fill=(12,15,24,a))
        img = Image.alpha_composite(img.convert("RGBA"), fade).convert("RGB")
        d = ImageDraw.Draw(img)

    # Compass
    cx, cy, cr = W-72, MAP_BOT-84, 40
    comp = Image.new("RGBA", (W, H), (0,0,0,0))
    cd = ImageDraw.Draw(comp)
    cd.ellipse([cx-cr, cy-cr, cx+cr, cy+cr], fill=(12,15,24,210))
    cd.ellipse([cx-cr, cy-cr, cx+cr, cy+cr], outline=(58,74,92,180), width=2)
    n_tip=(cx, cy-int(cr*0.72)); n_bl=(cx-8, cy+5); n_br=(cx+8, cy+5); n_mid=(cx, cy-3)
    cd.polygon([n_tip, n_bl, n_mid], fill=(0,207,168,230))
    cd.polygon([n_tip, n_br, n_mid], fill=(0,157,128,230))
    s_tip=(cx, cy+int(cr*0.72)); s_bl=(cx-8, cy-5); s_br=(cx+8, cy-5); s_mid=(cx, cy+3)
    cd.polygon([s_tip, s_bl, s_mid], fill=(42,51,64,230))
    cd.polygon([s_tip, s_br, s_mid], fill=(58,74,92,230))
    cd.ellipse([cx-4, cy-4, cx+4, cy+4], fill=(200,210,220,255))
    n_fnt = font("GeistMono-Bold.ttf", 18)
    cd.text((cx-6, cy-cr-22), "N", font=n_fnt, fill=(0,207,168,220))
    img = Image.alpha_composite(img.convert("RGBA"), comp).convert("RGB")
    d = ImageDraw.Draw(img)

    # Status bar
    d.rectangle([0, 0, W, STATUS_H], fill=BG)
    d.text((52, 22), "09:41", font=font("GeistMono-Bold.ttf", 36), fill=T_MAIN)
    bx_sig = W-168
    for i, h in enumerate([8,12,16,20]):
        bxs = bx_sig + i*18
        d.rectangle([bxs, 36+(20-h), bxs+11, 56], fill=T_MAIN if i<3 else SLATE)
    bat = W-66
    d.rounded_rectangle([bat, 30, bat+44, 50], radius=5, outline=T_MID, width=2)
    d.rectangle([bat+3, 33, bat+34, 47], fill=TEAL)
    d.rounded_rectangle([bat+45, 36, bat+50, 44], radius=2, fill=T_MID)

    # Header
    d.rectangle([0, STATUS_H, W, STATUS_H+HEADER_H], fill=BG)
    d.line([(40, STATUS_H+HEADER_H-1), (W-40, STATUS_H+HEADER_H-1)], fill=SLATE3, width=1)
    d.text((52, STATUS_H+14), "SAFE", font=font("BigShoulders-Bold.ttf", 50), fill=T_MAIN)
    d.text((52+118, STATUS_H+14), "ROUTE", font=font("BigShoulders-Bold.ttf", 50), fill=TEAL)
    sx = W-260; sy = STATUS_H+26
    d.ellipse([sx, sy+2, sx+12, sy+14], fill=TEAL)
    d.text((sx+18, sy), "vor 3 Min.", font=font("GeistMono-Regular.ttf", 24), fill=T_MID)

    # Bottom panel
    d.rectangle([0, MAP_BOT, W, H], fill=BG2)
    d.line([(0, MAP_BOT), (W, MAP_BOT)], fill=TEAL, width=3)

    dest_y = MAP_BOT + 28
    d.text((52, dest_y), "SCHWEIZ",
           font=font("BigShoulders-Bold.ttf", 88), fill=T_MAIN)
    d.text((52, dest_y + 96),
           "Nächste sichere Grenze  —  automatisch",
           font=font("WorkSans-Regular.ttf", 26), fill=T_MID)
    d.text((52, dest_y + 128), "ermittelt aus deinem Standort",
           font=font("WorkSans-Regular.ttf", 26), fill=T_DIM)

    div_y = dest_y + 166
    d.line([(52, div_y), (W-52, div_y)], fill=ROAD_MJ, width=1)

    stats_y = div_y + 20
    mid = W // 2
    d.text((52, stats_y), "247",
           font=font("GeistMono-Bold.ttf", 72), fill=T_MAIN)
    d.text((52+158, stats_y+36), "KM", font=font("GeistMono-Regular.ttf", 24), fill=T_MID)
    d.text((52, stats_y+78), "Distanz",
           font=font("WorkSans-Regular.ttf", 24), fill=T_DIM)
    d.line([(mid, stats_y+6), (mid, stats_y+96)], fill=ROAD_MJ, width=1)
    d.text((mid+36, stats_y), "3h 20",
           font=font("GeistMono-Bold.ttf", 72), fill=T_MAIN)
    d.text((mid+214, stats_y+36), "MIN", font=font("GeistMono-Regular.ttf", 24), fill=T_MID)
    d.text((mid+36, stats_y+78), "Fahrzeit",
           font=font("WorkSans-Regular.ttf", 24), fill=T_DIM)

    div2_y = stats_y + 110
    d.line([(52, div2_y), (W-52, div2_y)], fill=ROAD_MJ, width=1)
    update_y = div2_y + 18
    d.text((52, update_y), "Route aktualisiert.",
           font=font("WorkSans-Regular.ttf", 26), fill=T_DIM)
    d.text((W-52-180, update_y), "via A3 · A1",
           font=font("GeistMono-Regular.ttf", 24), fill=T_DIM)

    hiw = 120; hix = (W-hiw)//2
    d.rounded_rectangle([hix, H-28, hix+hiw, H-18], radius=5, fill=SLATE)
    d.rounded_rectangle([0, 0, W-1, H-1], radius=FRAME_R, outline=SLATE2, width=3)

    mask = make_phone_mask(W, H, FRAME_R)
    out = Image.new("RGB", (W, H), BG)
    out.paste(img, mask=mask)
    return out

# ─────────────────────────────────────────────
# COMPOSE: beide Screens auf dunklem Canvas
# ─────────────────────────────────────────────
GAP     = 120
PADDING = 100
LABEL_H = 80

CW = PADDING*2 + W*2 + GAP
CH = PADDING*2 + H + LABEL_H

canvas = Image.new("RGB", (CW, CH), "#080B12")
cd = ImageDraw.Draw(canvas)

# Subtle grid background
for x in range(0, CW, 60):
    cd.line([(x, 0), (x, CH)], fill="#0F1320", width=1)
for y in range(0, CH, 60):
    cd.line([(0, y), (CW, y)], fill="#0F1320", width=1)

# Screen glow
for screen_x in [PADDING, PADDING + W + GAP]:
    glow_layer = Image.new("RGBA", (CW, CH), (0,0,0,0))
    gd = ImageDraw.Draw(glow_layer)
    for i in range(40, 0, -1):
        a = int(18 * (i/40))
        gd.rounded_rectangle(
            [screen_x - i, LABEL_H + PADDING - i,
             screen_x + W + i, LABEL_H + PADDING + H + i],
            radius=FRAME_R + i,
            fill=(0, 207, 168, a)
        )
    canvas = Image.alpha_composite(canvas.convert("RGBA"), glow_layer).convert("RGB")
    cd = ImageDraw.Draw(canvas)

# Draw phones
s1 = draw_onboarding()
s2 = draw_main()
canvas.paste(s1, (PADDING, LABEL_H + PADDING))
canvas.paste(s2, (PADDING + W + GAP, LABEL_H + PADDING))

# Labels
lbl_font = font("GeistMono-Regular.ttf", 32)
cd.text((PADDING + W//2 - 90, PADDING//2 + 14), "01  Onboarding",
        font=lbl_font, fill="#3A4A5C")
cd.text((PADDING + W + GAP + W//2 - 80, PADDING//2 + 14), "02  Navigation",
        font=lbl_font, fill="#3A4A5C")

# Arrow between screens
ax = PADDING + W + GAP//2
ay = LABEL_H + PADDING + H//2
arrow_size = 18
cd.line([(ax - 28, ay), (ax + 28, ay)], fill=TEAL, width=2)
cd.polygon([(ax+28, ay), (ax+14, ay-arrow_size//2), (ax+14, ay+arrow_size//2)],
           fill=TEAL)

# Footer
footer_y = LABEL_H + PADDING + H + 28
cd.text((PADDING, footer_y), "SAFEROUTE  —  Notzeiger Design  —  Phase 1 MVP",
        font=font("GeistMono-Regular.ttf", 26), fill="#1E2A38")

canvas.save("/Users/sk/Downloads/saferoute_screens.png", "PNG", dpi=(144,144))
print("Saved: /Users/sk/Downloads/saferoute_screens.png")
