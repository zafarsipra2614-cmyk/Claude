"""Bold line-art object library for brandonomics-whiteboard (black ink, Brandonomics blue #4D96FF). Writes assets/library/*.svg."""
import os
K, B, G, Wt = "#1f2328", "#4D96FF", "#8a8f98", "#ffffff"
st = f'stroke="{K}" stroke-linecap="round" stroke-linejoin="round"'
def svg(name, vb, body):
    x, y, w, h = vb
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "library", name + ".svg"), "w").write(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x} {y} {w} {h}" width="{w}" height="{h}">{body}</svg>')

svg("eye", (-30, -40, 660, 460), f'''
  <path d="M30 200 Q300 -30 570 200 Q300 430 30 200 Z" fill="{Wt}" {st} stroke-width="16"/>
  <circle cx="300" cy="200" r="100" fill="{B}" {st} stroke-width="13"/>
  <circle cx="300" cy="200" r="44" fill="{K}"/>
  <circle cx="328" cy="172" r="17" fill="{Wt}"/>
  <path d="M150 112 L122 62 M225 80 L210 26 M300 70 L300 14 M375 80 L390 26 M450 112 L478 62" fill="none" {st} stroke-width="13"/>''')

def bulb(on):
    glass = Wt if on else G
    rays = "".join(f'<path d="M{300+170*c:.0f} {230+170*s:.0f} L{300+230*c:.0f} {230+230*s:.0f}" {st} stroke-width="14"/>'
                   for c, s in [(-1, 0), (-.87, -.5), (-.5, -.87), (0, -1), (.5, -.87), (.87, -.5), (1, 0)]) if on else ""
    return f'''{rays}
  <path d="M230 360 C150 320 130 250 130 220 A170 170 0 1 1 470 220 C470 250 450 320 370 360 L360 420 L240 420 Z" fill="{glass}" {st} stroke-width="15"/>
  <path d="M255 360 L270 260 L300 300 L330 260 L345 360" fill="none" {st} stroke-width="11"/>
  <path d="M240 420 L360 420 L355 500 Q300 520 245 500 Z" fill="{B}" {st} stroke-width="14"/>
  <path d="M246 448 L354 448 M248 476 L352 476" {st} stroke-width="10"/>
  <path d="M275 515 Q300 545 325 515" fill="{K}" {st} stroke-width="12"/>'''
svg("bulb-on", (40, -20, 520, 590), bulb(True))
svg("bulb-off", (40, -20, 520, 590), bulb(False))

svg("factory", (-30, -40, 920, 640), f'''
  <path d="M20 540 L840 540" {st} stroke-width="16"/>
  <rect x="610" y="40" width="80" height="260" fill="{Wt}" {st} stroke-width="15"/>
  <rect x="610" y="90" width="80" height="40" fill="{B}" {st} stroke-width="12"/>
  <path d="M60 540 L60 290 L180 200 L180 290 L300 200 L300 290 L420 200 L420 290 L540 200 L540 290 L780 290 L780 540 Z" fill="{Wt}" {st} stroke-width="16"/>
  {"".join(f'<rect x="{x}" y="340" width="70" height="60" fill="{B}" {st} stroke-width="11"/>' for x in (100, 210, 320, 430))}
  {"".join(f'<rect x="{x}" y="430" width="70" height="60" fill="{B}" {st} stroke-width="11"/>' for x in (100, 210, 320))}
  <rect x="560" y="400" width="120" height="140" fill="{K}" {st} stroke-width="12"/>
  <path d="M120 290 L120 230 M240 290 L240 230 M360 290 L360 230 M480 290 L480 230" {st} stroke-width="9"/>
  <circle cx="700" cy="10" r="26" fill="none" {st} stroke-width="11"/><circle cx="745" cy="-12" r="20" fill="none" {st} stroke-width="10"/>''')

svg("chart-up", (-30, -40, 560, 480), f'''
  <path d="M20 0 L20 400 L500 400" fill="none" {st} stroke-width="16"/>
  <rect x="70" y="280" width="90" height="120" fill="{B}" {st} stroke-width="13"/>
  <rect x="210" y="190" width="90" height="210" fill="{B}" {st} stroke-width="13"/>
  <rect x="350" y="90" width="90" height="310" fill="{B}" {st} stroke-width="13"/>
  <path d="M115 235 L255 145 L395 45 L428 22" fill="none" {st} stroke-width="13"/>
  <path d="M382 27 L428 22 L408 63" fill="none" {st} stroke-width="13"/>''')

svg("chart-flat", (-30, -40, 620, 480), f'''
  <path d="M20 0 L20 400 L560 400" fill="none" {st} stroke-width="16"/>
  {"".join(f'<rect x="{70+i*120}" y="{y}" width="80" height="{400-y}" fill="{G}" {st} stroke-width="12"/>' for i, y in enumerate((210, 195, 220, 205)))}''')

svg("clipboard", (-30, -40, 420, 540), f'''
  <rect x="10" y="30" width="340" height="440" rx="26" fill="{B}" {st} stroke-width="15"/>
  <rect x="50" y="80" width="260" height="350" fill="{Wt}" {st} stroke-width="12"/>
  <rect x="115" y="0" width="130" height="62" rx="14" fill="{K}" {st} stroke-width="12"/>
  <path d="M90 160 L270 160 M90 220 L270 220 M90 280 L270 280 M90 340 L200 340" {st} stroke-width="12"/>''')

svg("survey", (-30, -40, 420, 540), f'''
  <path d="M10 10 L290 10 L350 70 L350 470 L10 470 Z" fill="{Wt}" {st} stroke-width="15"/>
  <path d="M290 10 L290 70 L350 70" fill="none" {st} stroke-width="12"/>
  {"".join(f'<rect x="50" y="{y}" width="56" height="56" rx="8" fill="{Wt}" {st} stroke-width="11"/><path d="M135 {y+28} L300 {y+28}" {st} stroke-width="12"/>' for y in (110, 220, 330))}
  <path d="M60 140 L76 158 L104 116 M60 250 L76 268 L104 226" fill="none" stroke="{B}" stroke-width="13" stroke-linecap="round" stroke-linejoin="round"/>''')

def star(cx, cy, r, fill):
    import math
    p = " ".join(f"{cx + (r if i % 2 == 0 else r*.45) * math.cos(math.radians(-90 + 36*i)):.0f},{cy + (r if i % 2 == 0 else r*.45) * math.sin(math.radians(-90 + 36*i)):.0f}" for i in range(10))
    return f'<polygon points="{p}" fill="{fill}" {st} stroke-width="9"/>'
svg("review", (-30, -40, 560, 420), f'''
  <rect x="10" y="10" width="480" height="320" rx="24" fill="{Wt}" {st} stroke-width="15"/>
  {"".join(star(80 + i*85, 110, 36, B if i < 3 else Wt) for i in range(5))}
  <path d="M60 210 L440 210 M60 265 L330 265" {st} stroke-width="12"/>''')

svg("magnifier", (-30, -30, 520, 520), f'''
  <path d="M280 280 L430 430" {st} stroke-width="44"/>
  <circle cx="180" cy="180" r="150" fill="{Wt}" fill-opacity="0" {st} stroke-width="26"/>
  <path d="M95 140 Q120 90 170 75" fill="none" stroke="{B}" stroke-width="16" stroke-linecap="round"/>''')
