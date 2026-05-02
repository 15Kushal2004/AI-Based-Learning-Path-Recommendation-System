"""Simple helpers to generate downloadable certificate images."""

from datetime import date
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont


def _safe_text(value):
    return str(value or "").strip()


def certificate_image_filename(name, title):
    base = f"{_safe_text(name)}_{_safe_text(title)}_Certificate"
    cleaned = "".join(ch if ch.isalnum() or ch in ("_", "-") else "_" for ch in base)
    return f"{cleaned}.png"


def _get_font(size, bold=False):
    candidates = [
        "arialbd.ttf" if bold else "arial.ttf",
        "segoeuib.ttf" if bold else "segoeui.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _hex_to_rgb(hex_color):
    return tuple(int(hex_color[i:i + 2], 16) for i in (1, 3, 5))


def generate_certificate_image(name, domain, goal, title, progress_pct, issue_date=None):
    """Generate a simple level-based certificate PNG and return bytes."""
    name = _safe_text(name) or "Learner"
    domain = _safe_text(domain) or "Learning"
    goal = _safe_text(goal) or "Personal Growth"
    title = _safe_text(title) or "Achievement"
    issue_date = issue_date or date.today().strftime("%d %b %Y")

    palette = {
        "Beginner": ("#d97706", "#0f172a", "#1e293b"),
        "Intermediate": ("#6b7280", "#111827", "#1f2937"),
        "Advanced": ("#f59e0b", "#0f172a", "#1e293b"),
        "Expert": ("#6366f1", "#0b1020", "#1a2140"),
    }
    accent_hex, bg1_hex, bg2_hex = palette.get(title, ("#6366f1", "#0f172a", "#1e293b"))
    accent = _hex_to_rgb(accent_hex)
    bg1 = _hex_to_rgb(bg1_hex)
    bg2 = _hex_to_rgb(bg2_hex)

    width, height = 1400, 900
    image = Image.new("RGB", (width, height), bg1)
    draw = ImageDraw.Draw(image)

    for y in range(height):
        t = y / max(height - 1, 1)
        r = int(bg1[0] * (1 - t) + bg2[0] * t)
        g = int(bg1[1] * (1 - t) + bg2[1] * t)
        b = int(bg1[2] * (1 - t) + bg2[2] * t)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    draw.rounded_rectangle((25, 25, width - 25, height - 25), radius=28, outline=accent, width=5)

    title_font = _get_font(64, bold=True)
    name_font = _get_font(56, bold=True)
    text_font = _get_font(34)
    small_font = _get_font(24)

    center_x = width // 2

    def centered(text, y, font, fill):
        left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
        text_w = right - left
        draw.text((center_x - text_w // 2, y), text, font=font, fill=fill)

    centered("Certificate of Achievement", 100, title_font, "#e5e7eb")
    centered("This is proudly presented to", 220, text_font, "#94a3b8")
    centered(name, 290, name_font, "#f8fafc")
    draw.line((350, 370, 1050, 370), fill="#334155", width=2)
    centered("for successfully completing the learning path in", 410, text_font, "#94a3b8")
    centered(domain, 470, name_font, accent_hex)

    centered(f"Level Earned: {title}", 560, text_font, "#cbd5e1")
    centered(f"Goal: {goal}", 610, text_font, "#cbd5e1")
    centered(f"Progress: {progress_pct}%", 660, text_font, "#cbd5e1")

    draw.text((120, 780), f"Date: {issue_date}", font=small_font, fill="#94a3b8")
    draw.text((930, 780), "AI Learning System", font=small_font, fill="#94a3b8")
    draw.text((930, 815), "Authorized Signature", font=small_font, fill=accent_hex)

    output = BytesIO()
    image.save(output, format="PNG")
    output.seek(0)
    return output.getvalue()
