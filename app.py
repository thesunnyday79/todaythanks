"""
🛒 Amazon Product Review Video Creator
Dán link ảnh/video → AI voiceover (Inworld TTS) → MP4 review chuyên nghiệp
"""

import streamlit as st
import requests
import base64
import os
import time
import tempfile
import traceback
import re
from urllib.parse import urlparse

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
    import numpy as np
    PIL_OK = True
except ImportError:
    PIL_OK = False

try:
    import moviepy.editor as mpy
    MPY_OK = True
except ImportError:
    MPY_OK = False

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Amazon Review Video Creator",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════════════════════
# STYLES — Amazon-inspired warm editorial
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Lora:ital,wght@0,400;0,600;1,400&display=swap');

*,*::before,*::after{box-sizing:border-box}
html,body,.stApp{
  background:#0c0a08 !important;
  font-family:'Plus Jakarta Sans',sans-serif;
  color:#ede8e0;
}
#MainMenu,footer,header{visibility:hidden}
.block-container{padding:1.8rem 2.6rem 4rem !important;max-width:1320px !important}

/* ── Hero */
.hero{
  background:linear-gradient(135deg,#1a0e00 0%,#0c0a08 50%,#0a0c10 100%);
  border:1px solid rgba(255,153,0,0.18);
  border-radius:20px;padding:2.4rem 3rem;
  margin-bottom:1.8rem;position:relative;overflow:hidden;
}
.hero::before{
  content:'';position:absolute;top:-60px;right:-40px;
  width:280px;height:280px;
  background:radial-gradient(circle,rgba(255,153,0,0.12) 0%,transparent 65%);
}
.hero::after{
  content:'';position:absolute;bottom:-50px;left:25%;
  width:200px;height:200px;
  background:radial-gradient(circle,rgba(255,100,30,0.07) 0%,transparent 65%);
}
.hero-brand{
  font-size:0.72rem;font-weight:700;letter-spacing:0.18em;
  text-transform:uppercase;color:#ff9900;margin-bottom:0.5rem;
}
.hero-title{
  font-family:'Plus Jakarta Sans',sans-serif;
  font-size:2.4rem;font-weight:800;line-height:1.15;
  color:#fff;margin:0 0 0.5rem;
}
.hero-title span{color:#ff9900}
.hero-sub{color:#8a8070;font-size:0.95rem;margin:0;font-weight:300}

/* ── Step bar */
.stepbar{
  display:flex;border-radius:12px;overflow:hidden;
  border:1px solid rgba(255,255,255,0.05);margin-bottom:1.8rem;
}
.si{
  flex:1;padding:0.8rem 0.3rem;text-align:center;
  font-size:0.72rem;font-weight:700;letter-spacing:0.06em;
  text-transform:uppercase;background:#100e0c;
  color:#3a3028;border-right:1px solid rgba(255,255,255,0.04);
  transition:all 0.3s;
}
.si:last-child{border-right:none}
.si.act{background:linear-gradient(135deg,#ff6600,#ff9900);color:#fff}
.si.don{background:#1a1410;color:#7a5a20}

/* ── Cards */
.card{
  background:#131109;
  border:1px solid rgba(255,255,255,0.07);
  border-radius:15px;padding:1.4rem 1.6rem;margin-bottom:1.1rem;
}
.card-lbl{
  font-size:0.68rem;font-weight:700;letter-spacing:0.13em;
  text-transform:uppercase;color:#ff9900;margin-bottom:0.85rem;
}

/* ── Media preview grid */
.media-grid{
  display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));
  gap:10px;margin-top:0.8rem;
}
.media-thumb{
  border-radius:10px;overflow:hidden;
  border:2px solid rgba(255,153,0,0.15);
  background:#0a0908;position:relative;
  aspect-ratio:1;cursor:pointer;
  transition:border-color 0.2s;
}
.media-thumb:hover{border-color:rgba(255,153,0,0.5)}
.media-thumb img,.media-thumb video{
  width:100%;height:100%;object-fit:cover;display:block;
}
.media-badge{
  position:absolute;top:6px;right:6px;
  background:rgba(0,0,0,0.75);
  border-radius:6px;padding:2px 7px;
  font-size:0.65rem;font-weight:700;
  color:#ff9900;letter-spacing:0.05em;
}
.media-order{
  position:absolute;top:6px;left:6px;
  width:22px;height:22px;border-radius:50%;
  background:#ff9900;color:#000;
  font-size:0.72rem;font-weight:800;
  display:flex;align-items:center;justify-content:center;
}

/* ── Review scenes */
.scene-row{
  background:#0f0d0b;
  border:1px solid rgba(255,153,0,0.15);
  border-radius:12px;padding:1.1rem 1.3rem;margin:0.5rem 0;
}
.scene-type{
  font-size:0.65rem;font-weight:700;letter-spacing:0.12em;
  text-transform:uppercase;color:#cc7700;margin-bottom:0.3rem;
}
.scene-name{font-size:0.92rem;font-weight:600;color:#e8d8b8;margin-bottom:0.25rem}
.scene-script{font-size:0.82rem;color:#7a6850;line-height:1.5;font-style:italic}

/* ── Stars */
.stars{color:#ff9900;font-size:1.2rem;letter-spacing:2px}
.star-label{font-size:0.8rem;color:#8a7060;margin-left:6px}

/* ── Rating meter */
.meter-row{display:flex;align-items:center;gap:10px;margin:4px 0}
.meter-lbl{font-size:0.78rem;color:#9a8870;width:90px;flex-shrink:0}
.meter-bar{flex:1;height:8px;background:#1e1c18;border-radius:4px;overflow:hidden}
.meter-fill{height:100%;border-radius:4px;background:linear-gradient(90deg,#ff6600,#ff9900)}
.meter-val{font-size:0.78rem;color:#cc7700;width:28px;text-align:right;flex-shrink:0}

/* ── Pro/Con tags */
.pro-tag{
  display:inline-block;background:rgba(34,197,94,0.1);
  border:1px solid rgba(34,197,94,0.25);
  color:#86efac;border-radius:20px;
  padding:3px 12px;font-size:0.78rem;margin:3px 4px 3px 0;
}
.con-tag{
  display:inline-block;background:rgba(239,68,68,0.1);
  border:1px solid rgba(239,68,68,0.25);
  color:#fca5a5;border-radius:20px;
  padding:3px 12px;font-size:0.78rem;margin:3px 4px 3px 0;
}

/* ── Alerts */
.warn{background:#160f00;border:1px solid rgba(217,119,6,0.3);border-radius:10px;padding:0.9rem 1.3rem;color:#fcd34d;font-size:0.86rem}
.info{background:#050c18;border-left:4px solid #3b82f6;border-radius:0 10px 10px 0;padding:0.9rem 1.3rem;color:#93c5fd;font-size:0.88rem}
.ok  {background:linear-gradient(135deg,#042014,#041820);border:1px solid rgba(34,197,94,0.28);border-radius:10px;padding:0.9rem 1.3rem;color:#86efac}
.err {background:#160404;border:1px solid rgba(239,68,68,0.3);border-radius:10px;padding:0.9rem 1.3rem;color:#fca5a5;font-size:0.86rem}

/* ── Inputs */
.stTextArea textarea,.stTextInput input{
  background:#0a0908 !important;
  border:1px solid rgba(255,153,0,0.22) !important;
  border-radius:9px !important;color:#e8d8b8 !important;
  font-family:'Plus Jakarta Sans',sans-serif !important;
}
.stSelectbox>div>div{
  background:#0a0908 !important;
  border:1px solid rgba(255,153,0,0.22) !important;
  color:#e8d8b8 !important;border-radius:9px !important;
}
.stSlider [data-baseweb=slider] div[role=slider]{background:#ff9900 !important}
.stRadio div[role=radiogroup]{gap:0.5rem}

/* ── Buttons */
.stButton>button{
  background:linear-gradient(135deg,#ff6600,#ff9900) !important;
  color:#000 !important;border:none !important;
  border-radius:10px !important;
  font-family:'Plus Jakarta Sans',sans-serif !important;
  font-weight:700 !important;font-size:0.9rem !important;
  padding:0.6rem 1.5rem !important;
  transition:all 0.22s !important;
}
.stButton>button:hover{
  transform:translateY(-2px) !important;
  box-shadow:0 6px 22px rgba(255,153,0,0.35) !important;
}
.stButton>button:disabled{
  background:#1a1710 !important;color:#3a3020 !important;
  transform:none !important;box-shadow:none !important;
}
label,.stMarkdown p{color:#8a8070 !important}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════
INWORLD_TTS = "https://api.inworld.ai/tts/v1/voice"

VOICES = {
    "Liam — Natural Male (Recommended)":       "Liam",
    "Timothy — Young Enthusiastic Male":        "Timothy",
    "Dennis — Confident Male":                  "Dennis",
    "Theodore — Authoritative Male":            "Theodore",
    "Craig — Deep Trustworthy Male":            "Craig",
    "Ashley — Friendly Female":                 "Ashley",
    "Olivia — Energetic Female":                "Olivia",
    "Elizabeth — Professional Female":          "Elizabeth",
    "Sarah — Calm Relatable Female":            "Sarah",
    "Priya — Expressive Female":                "Priya",
}

MODELS = {
    "TTS-1.5 Max — Best quality":  "inworld-tts-1.5-max",
    "TTS-1.5 Mini — Ultra-fast":   "inworld-tts-1.5-mini",
    "TTS-1 Max — Stable":          "inworld-tts-1-max",
}

REVIEW_TEMPLATES = {
    "⭐⭐⭐⭐⭐ 5-Star Glowing": {
        "rating": 5,
        "intro":    "I have been using {product} for {duration} now and I am absolutely blown away.",
        "unbox":    "Right out of the box, the packaging impressed me — this thing feels premium.",
        "details":  "The build quality is outstanding. Every detail has been thought through.",
        "pros":     ["Exceeds expectations", "Great value for money", "Works exactly as advertised"],
        "cons":     ["Minor learning curve at first"],
        "verdict":  "This is hands down one of the best purchases I have made this year. Highly recommend.",
        "cta":      "If you are on the fence — just get it. You will not regret it.",
    },
    "⭐⭐⭐⭐ 4-Star Balanced": {
        "rating": 4,
        "intro":    "I picked up {product} about {duration} ago and it has been a solid performer.",
        "unbox":    "The packaging is decent and everything arrived in perfect condition.",
        "details":  "For the price point, the quality is genuinely impressive. There are a few rough edges.",
        "pros":     ["Great performance", "Solid build quality", "Easy to use"],
        "cons":     ["Could improve in one or two areas", "Instructions could be clearer"],
        "verdict":  "Overall a great product with minor caveats. Would buy again.",
        "cta":      "For the price, this is a fantastic option. Check it out.",
    },
    "⭐⭐⭐ 3-Star Honest": {
        "rating": 3,
        "intro":    "I want to give you an honest review of {product} after {duration} of use.",
        "unbox":    "The unboxing experience was average — nothing special but no damage.",
        "details":  "There are things I like and things that genuinely disappoint me.",
        "pros":     ["Does the basics well", "Affordable price"],
        "cons":     ["Build quality feels cheap", "Missing some expected features", "Customer support slow"],
        "verdict":  "It is okay for casual use but I expected more based on the listing.",
        "cta":      "If your expectations are modest, it might work for you.",
    },
    "🔍 Detailed Tech Review": {
        "rating": 4,
        "intro":    "Today I am doing a deep-dive technical review of {product}.",
        "unbox":    "In the box you get the main unit, accessories, and a quick-start guide.",
        "details":  "Performance tests show impressive results. Specs match what is advertised.",
        "pros":     ["Performance exceeds price tier", "Firmware updates available", "Great compatibility"],
        "cons":     ["Advanced features take time to learn", "App could be more polished"],
        "verdict":  "From a technical standpoint, this delivers excellent value.",
        "cta":      "Link in the description. Let me know your questions in the comments.",
    },
    "✍️ Custom Review": {
        "rating": 5,
        "intro":    "My honest review of {product} after {duration} of testing.",
        "unbox":    "Let me walk you through everything you need to know.",
        "details":  "Here is what stood out to me during my time with this product.",
        "pros":     ["Pro 1", "Pro 2", "Pro 3"],
        "cons":     ["Con 1"],
        "verdict":  "My overall verdict and recommendation.",
        "cta":      "Check it out using the link below. Thanks for watching!",
    },
}

MUSIC = {
    "🎵 Upbeat Review Vibe":  "https://cdn.pixabay.com/download/audio/2022/10/25/audio_946b8bce4f.mp3",
    "🌅 Warm Ambient":        "https://cdn.pixabay.com/download/audio/2023/10/09/audio_c8c8a73467.mp3",
    "🔇 No music":            None,
}

IMAGE_EXTS  = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}
VIDEO_EXTS  = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v"}

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
D = {
    "step": 1,
    "api_key": "",
    "product": "",
    "duration_use": "2 weeks",
    "asin": "",
    "template": "⭐⭐⭐⭐⭐ 5-Star Glowing",
    "rating": 5,
    "pros": ["", "", ""],
    "cons": ["", ""],
    "media_links": [],       # list of {"url":str,"type":"image"|"video","label":str}
    "voice": "Liam — Natural Male (Recommended)",
    "model": "TTS-1.5 Max — Best quality",
    "speed": 1.0,
    "music": "🎵 Upbeat Review Vibe",
    "scenes": [],
    "audios": {},
    "video": None,
    "show_preview": False,
}
for k, v in D.items():
    if k not in st.session_state:
        st.session_state[k] = v

STEPS = ["① Product","② Media","③ Script","④ Voiceover","⑤ Render"]

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def detect_media_type(url: str) -> str:
    path = urlparse(url).path.lower()
    ext  = os.path.splitext(path)[1]
    if ext in VIDEO_EXTS: return "video"
    if ext in IMAGE_EXTS: return "image"
    # YouTube / common video platforms
    if any(x in url for x in ["youtube.com","youtu.be","vimeo.com","streamable.com"]):
        return "video"
    return "image"   # default fallback


def is_valid_url(url: str) -> bool:
    try:
        r = urlparse(url)
        return r.scheme in ("http","https") and bool(r.netloc)
    except:
        return False


def gen_tts(api_key, text, voice_id, model_id, speed=1.0, temp=0.82):
    r = requests.post(
        INWORLD_TTS,
        headers={"Authorization": f"Basic {api_key}", "Content-Type": "application/json"},
        json={"text": text, "voiceId": voice_id, "modelId": model_id,
              "audioConfig": {"speakingRate": speed, "temperature": temp, "audioEncoding": "MP3"}},
        timeout=30,
    )
    r.raise_for_status()
    return base64.b64decode(r.json()["audioContent"])


def download_media(url: str, tmpdir: str, idx: int, mtype: str):
    """Download image/video to temp file. Returns local path or None."""
    try:
        resp = requests.get(url, timeout=20, stream=True,
                            headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        ext  = ".mp4" if mtype == "video" else ".jpg"
        path = os.path.join(tmpdir, f"media_{idx}{ext}")
        with open(path, "wb") as f:
            for chunk in resp.iter_content(65536):
                f.write(chunk)
        return path
    except Exception as e:
        return None


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2],16) for i in (0,2,4))


def make_overlay_frame(img: "Image.Image", scene: dict, product: str, w=1280, h=720) -> "Image.Image":
    """Add lower-third overlay + scene info on top of a product image."""
    # Resize/crop image to 1280x720
    img = img.convert("RGB")
    iw, ih = img.size
    scale  = max(w/iw, h/ih)
    nw, nh = int(iw*scale), int(ih*scale)
    img    = img.resize((nw, nh), Image.LANCZOS)
    left   = (nw - w) // 2
    top    = (nh - h) // 2
    img    = img.crop((left, top, left+w, top+h))

    # Darken slightly for readability
    img = ImageEnhance.Brightness(img).enhance(0.75)

    d = ImageDraw.Draw(img)

    # Bottom gradient bar (lower third)
    for y in range(h-200, h):
        alpha = int(200 * (y - (h-200)) / 200)
        r,g,b = 10, 8, 4
        # Blend dark gradient
        for x in range(0, w, 4):
            px = img.getpixel((x, y))
            nr = int(px[0] * (1 - alpha/255) + r * (alpha/255))
            ng = int(px[1] * (1 - alpha/255) + g * (alpha/255))
            nb = int(px[2] * (1 - alpha/255) + b * (alpha/255))
            d.line([(x,y),(x+3,y)], fill=(nr,ng,nb))

    # Top bar: scene type label
    if scene.get("scene_type"):
        lbl = scene["scene_type"].upper()
        d.rectangle([0, 0, w, 44], fill=(10, 8, 4, 200))
        d.rectangle([0, 0, 4, 44], fill=(255, 153, 0))
        d.text((16, 12), lbl, fill=(255, 153, 0))

    # Product name (top right)
    pname = (product[:22]+"…") if len(product)>22 else product
    d.text((w-220, 12), pname, fill=(220,200,160))

    # Scene title / script (bottom)
    title  = scene.get("name","")
    script = scene.get("script","")
    # Title
    d.text((40, h-170), title, fill=(255, 153, 0))
    # Script — wrapped
    words  = script.split()
    max_ch = 62
    lines, cur = [], ""
    for word in words:
        if len(cur)+len(word)+1 <= max_ch:
            cur = (cur+" "+word).strip()
        else:
            lines.append(cur); cur = word
    if cur: lines.append(cur)
    for i,line in enumerate(lines[:3]):
        d.text((40, h-140 + i*34), line, fill=(230, 220, 200))

    # Star rating (if applicable)
    rating = scene.get("rating")
    if rating:
        stars = "★"*rating + "☆"*(5-rating)
        d.text((40, h-46), stars, fill=(255, 153, 0))
        d.text((40 + rating*18 + 10, h-44), f"({rating}/5)", fill=(160, 130, 80))

    return img


def build_scenes(product, duration_use, template_key, pros, cons, media_links, rating):
    tmpl    = dict(REVIEW_TEMPLATES[template_key])
    p       = product or "this product"
    du      = duration_use or "a few weeks"
    pros_ok = [x for x in pros if x.strip()] or tmpl["pros"]
    cons_ok = [x for x in cons if x.strip()] or tmpl["cons"]

    def fmt(s):
        return s.format(product=p, duration=du)

    # Base review scenes (always present)
    scenes = [
        {"id":"intro",   "name":"Introduction",     "scene_type":"intro",
         "script":fmt(tmpl["intro"]),  "rating":None},
        {"id":"unbox",   "name":"Unboxing & First Look","scene_type":"unboxing",
         "script":fmt(tmpl["unbox"]), "rating":None},
        {"id":"details", "name":"Features & Details","scene_type":"features",
         "script":fmt(tmpl["details"]),"rating":None},
        {"id":"pros",    "name":"Pros",              "scene_type":"pros",
         "script":"Here is what I love: " + ". ".join(pros_ok) + ".", "rating":None},
        {"id":"cons",    "name":"Cons & Caveats",    "scene_type":"cons",
         "script":"A few things to know: " + ". ".join(cons_ok) + ".", "rating":None},
        {"id":"verdict", "name":"Final Verdict",     "scene_type":"verdict",
         "script":fmt(tmpl["verdict"]),  "rating":rating},
        {"id":"cta",     "name":"Call to Action",    "scene_type":"outro",
         "script":fmt(tmpl["cta"]),  "rating":None},
    ]

    # Map media to scenes: cycle through available media
    n = len(media_links)
    if n > 0:
        for i, sc in enumerate(scenes):
            sc["media"] = media_links[i % n]
    else:
        for sc in scenes:
            sc["media"] = None

    return scenes


def render_hero():
    st.markdown("""
    <div class="hero">
      <div class="hero-brand">Amazon · Product Review</div>
      <div class="hero-title">🛒 Review Video <span>Creator</span></div>
      <div class="hero-sub">
        Paste your product images & video links → AI voiceover (Inworld TTS) → 
        Professional review MP4 ready to upload
      </div>
    </div>
    """, unsafe_allow_html=True)


def render_steps(cur):
    items = ""
    for i, lbl in enumerate(STEPS, 1):
        if i < cur:   items += f'<div class="si don">✓ {lbl}</div>'
        elif i == cur: items += f'<div class="si act">▶ {lbl}</div>'
        else:          items += f'<div class="si">{lbl}</div>'
    st.markdown(f'<div class="stepbar">{items}</div>', unsafe_allow_html=True)


def stars_html(n):
    return "★"*n + "☆"*(5-n)


# ══════════════════════════════════════════════════════════════════════════════
# STEP 1 — PRODUCT INFO
# ══════════════════════════════════════════════════════════════════════════════
def step1():
    st.markdown("### 🛍️ Product Information")

    c1, c2 = st.columns([1.1, 1], gap="large")

    with c1:
        st.markdown('<div class="card"><div class="card-lbl">🔑 Inworld API Key</div>', unsafe_allow_html=True)
        key = st.text_input("key", value=st.session_state.api_key, type="password",
                            placeholder="Base64 credentials — platform.inworld.ai",
                            label_visibility="collapsed")
        st.session_state.api_key = key
        if key:
            st.markdown('<div class="ok">✅ API key saved</div>', unsafe_allow_html=True)
        else:
            st.markdown("""<div class="warn">🔑 Free key →
            <a href="https://platform.inworld.ai/api-keys" target="_blank" style="color:#fcd34d">
            platform.inworld.ai</a> → Generate → copy <b>Basic (Base64)</b></div>""",
            unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="card"><div class="card-lbl">📦 Product Details</div>', unsafe_allow_html=True)
        st.session_state.product = st.text_input(
            "Product name / title",
            value=st.session_state.product,
            placeholder="e.g. YABER Pro V7 Projector, Anker PowerBank 26800…",
        )
        st.session_state.asin = st.text_input(
            "Amazon ASIN (optional)",
            value=st.session_state.asin,
            placeholder="e.g. B0XXXXXX — shown in video for viewers",
        )
        st.session_state.duration_use = st.text_input(
            "How long have you tested it?",
            value=st.session_state.duration_use,
            placeholder="e.g. 2 weeks, 1 month, 3 days…",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="card"><div class="card-lbl">⭐ Review Template & Rating</div>', unsafe_allow_html=True)
        tmpl = st.selectbox("Template", list(REVIEW_TEMPLATES.keys()),
                             index=list(REVIEW_TEMPLATES.keys()).index(st.session_state.template),
                             label_visibility="collapsed")
        st.session_state.template = tmpl

        rating = st.slider("Your rating", 1, 5, st.session_state.rating)
        st.session_state.rating = rating
        st.markdown(f'<div class="stars">{stars_html(rating)}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="card"><div class="card-lbl">✅ Pros (what you loved)</div>', unsafe_allow_html=True)
        for i in range(3):
            v = st.text_input(f"Pro {i+1}", value=st.session_state.pros[i],
                               placeholder=REVIEW_TEMPLATES[tmpl]["pros"][i] if i < len(REVIEW_TEMPLATES[tmpl]["pros"]) else "",
                               key=f"pro_{i}")
            st.session_state.pros[i] = v
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="card"><div class="card-lbl">⚠️ Cons (honest caveats)</div>', unsafe_allow_html=True)
        for i in range(2):
            v = st.text_input(f"Con {i+1}", value=st.session_state.cons[i],
                               placeholder=REVIEW_TEMPLATES[tmpl]["cons"][i] if i < len(REVIEW_TEMPLATES[tmpl]["cons"]) else "",
                               key=f"con_{i}")
            st.session_state.cons[i] = v
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    _, rc = st.columns([3,1])
    with rc:
        if st.button("Next → Add Media", use_container_width=True):
            if not st.session_state.api_key:
                st.error("Please enter your Inworld API Key.")
            elif not st.session_state.product.strip():
                st.error("Please enter a product name.")
            else:
                st.session_state.step = 2; st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# STEP 2 — MEDIA LINKS
# ══════════════════════════════════════════════════════════════════════════════
def step2():
    st.markdown("### 🖼️ Add Your Product Images & Videos")

    st.markdown("""<div class="info">
    📌 <b>Paste direct links</b> to your images/videos. Supported: JPG, PNG, WebP, MP4, MOV, WebM.<br>
    💡 Use <b>Amazon listing images</b>, Google Drive (with share link), Imgur, Cloudinary, S3, or any direct URL.<br>
    🔁 Media will be <b>cycled across scenes</b> — more media = more visual variety.
    </div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Add links input
    col_inp, col_add = st.columns([4,1], gap="small")
    with col_inp:
        new_url = st.text_input(
            "url",
            placeholder="https://example.com/product-photo.jpg  or  https://example.com/demo-video.mp4",
            label_visibility="collapsed",
            key="url_input",
        )
    with col_add:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Add Link", use_container_width=True):
            url = new_url.strip()
            if not url:
                st.warning("Please paste a URL first.")
            elif not is_valid_url(url):
                st.error("That doesn't look like a valid URL (must start with http/https).")
            elif any(m["url"] == url for m in st.session_state.media_links):
                st.warning("This URL is already added.")
            else:
                mtype = detect_media_type(url)
                label = os.path.basename(urlparse(url).path) or f"media_{len(st.session_state.media_links)+1}"
                st.session_state.media_links.append({"url":url,"type":mtype,"label":label})
                st.rerun()

    # ── Bulk paste
    with st.expander("📋 Bulk paste multiple links at once"):
        bulk = st.text_area(
            "bulk",
            height=110,
            placeholder="Paste one URL per line:\nhttps://…/photo1.jpg\nhttps://…/photo2.png\nhttps://…/demo.mp4",
            label_visibility="collapsed",
        )
        if st.button("Add All", use_container_width=True):
            added = 0
            for line in bulk.splitlines():
                url = line.strip()
                if is_valid_url(url) and not any(m["url"]==url for m in st.session_state.media_links):
                    mtype = detect_media_type(url)
                    label = os.path.basename(urlparse(url).path) or f"media_{len(st.session_state.media_links)+1}"
                    st.session_state.media_links.append({"url":url,"type":mtype,"label":label})
                    added += 1
            if added:
                st.success(f"Added {added} links."); st.rerun()
            else:
                st.warning("No new valid URLs found.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Current media list
    media = st.session_state.media_links
    if not media:
        st.markdown("""
        <div style='text-align:center;padding:3rem 2rem;color:#3a3020;border:1px dashed rgba(255,153,0,0.2);border-radius:14px'>
          <div style='font-size:3rem'>📷</div>
          <div style='font-size:1rem;margin-top:0.8rem'>
            No media added yet.<br>
            <span style='font-size:0.85rem'>Paste image/video URLs above to see them here.</span>
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='card-lbl' style='margin-bottom:0.6rem'>📁 {len(media)} media item(s) added — drag to reorder via Remove & Re-add</div>", unsafe_allow_html=True)

        # ── Preview grid
        cols = st.columns(min(len(media), 4))
        to_remove = None
        for i, m in enumerate(media):
            with cols[i % 4]:
                badge = "🎬 VIDEO" if m["type"]=="video" else "🖼️ IMAGE"
                if m["type"] == "video":
                    try:
                        st.video(m["url"])
                    except:
                        st.markdown(f"""<div style='background:#0a0908;border:1px solid rgba(255,153,0,0.2);border-radius:10px;padding:1rem;text-align:center;color:#cc7700;font-size:0.8rem'>
                        🎬<br>{m['label'][:20]}</div>""", unsafe_allow_html=True)
                else:
                    try:
                        st.image(m["url"], use_container_width=True)
                    except:
                        st.markdown(f"""<div style='background:#0a0908;border:1px solid rgba(255,153,0,0.2);border-radius:10px;padding:1rem;text-align:center;color:#cc7700;font-size:0.8rem'>
                        🖼️<br>{m['label'][:20]}</div>""", unsafe_allow_html=True)

                st.markdown(f"<div style='font-size:0.7rem;color:#6a5840;text-align:center;margin:-4px 0 4px'>#{i+1} · {badge}</div>", unsafe_allow_html=True)
                # Label edit
                new_lbl = st.text_input(f"Label", value=m["label"], key=f"lbl_{i}",
                                         label_visibility="collapsed")
                st.session_state.media_links[i]["label"] = new_lbl

                if st.button(f"🗑️ Remove", key=f"rm_{i}", use_container_width=True):
                    to_remove = i

        if to_remove is not None:
            st.session_state.media_links.pop(to_remove); st.rerun()

        # ── Type overrides
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("⚙️ Override media type (if auto-detection is wrong)"):
            for i, m in enumerate(media):
                cc, ct = st.columns([3,1])
                with cc:
                    st.markdown(f"<small style='color:#6a5840'>{m['url'][:60]}{'…' if len(m['url'])>60 else ''}</small>", unsafe_allow_html=True)
                with ct:
                    tp = st.selectbox("", ["image","video"],
                                       index=0 if m["type"]=="image" else 1,
                                       key=f"tp_{i}", label_visibility="collapsed")
                    st.session_state.media_links[i]["type"] = tp

    # ── Voice settings here too
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🎙️ Voice & Music Settings")
    vc1, vc2, vc3 = st.columns(3, gap="medium")
    with vc1:
        st.session_state.voice = st.selectbox("AI Voice", list(VOICES.keys()),
            index=list(VOICES.keys()).index(st.session_state.voice))
    with vc2:
        st.session_state.model = st.selectbox("TTS Model", list(MODELS.keys()),
            index=list(MODELS.keys()).index(st.session_state.model))
    with vc3:
        st.session_state.music = st.selectbox("Background Music", list(MUSIC.keys()),
            index=list(MUSIC.keys()).index(st.session_state.music))
    st.session_state.speed = st.slider("Speaking speed", 0.75, 1.35, st.session_state.speed, 0.05)

    st.markdown("<br>", unsafe_allow_html=True)
    lc, rc = st.columns(2)
    with lc:
        if st.button("← Back", use_container_width=True):
            st.session_state.step = 1; st.rerun()
    with rc:
        if st.button("Next → Review Script", use_container_width=True):
            if not st.session_state.media_links:
                st.warning("⚠️ No media added — video will use text-only slides. Continue anyway?")
            scenes = build_scenes(
                st.session_state.product, st.session_state.duration_use,
                st.session_state.template, st.session_state.pros,
                st.session_state.cons, st.session_state.media_links,
                st.session_state.rating,
            )
            st.session_state.scenes = scenes
            st.session_state.step = 3; st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# STEP 3 — SCRIPT REVIEW
# ══════════════════════════════════════════════════════════════════════════════
def step3():
    st.markdown("### 📝 Review & Edit Script")

    col_info, col_cfg = st.columns([2, 1], gap="large")
    with col_info:
        st.markdown("""<div class="info">
        ✏️ Each scene below will become a segment in your video with its own voiceover.
        Edit freely — make it sound natural and authentic to your voice.
        </div>""", unsafe_allow_html=True)
    with col_cfg:
        n_media = len(st.session_state.media_links)
        n_scene = len(st.session_state.scenes)
        st.markdown(f"""<div class="card" style="margin:0">
        <p style='color:#e8d8b8;font-size:0.85rem;margin:0;line-height:2'>
        🎬 {n_scene} scenes<br>
        🖼️ {n_media} media items<br>
        ⭐ {stars_html(st.session_state.rating)}
        </p></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    scenes = st.session_state.scenes
    updated = []
    words   = 0
    for i, sc in enumerate(scenes):
        # Show which media is assigned
        m     = sc.get("media")
        m_tag = ""
        if m:
            icon  = "🎬" if m["type"]=="video" else "🖼️"
            m_tag = f"<span style='color:#6a5840;font-size:0.68rem;margin-left:8px'>{icon} {m['label'][:30]}</span>"

        st.markdown(f"""<div class="scene-row">
        <div class="scene-type">{sc['scene_type'].upper()} · Scene {i+1}/{len(scenes)}{m_tag}</div>
        <div class="scene-name">{sc['name']}</div>
        </div>""", unsafe_allow_html=True)

        nv = st.text_area(f"sc{i}", value=sc["script"], height=90,
                          key=f"s_{i}", label_visibility="collapsed")
        words += len(nv.split())
        updated.append({**sc, "script": nv})

    st.session_state.scenes = updated

    est_min = words // 130  # ~130 wpm
    est_sec = int((words / 130) * 60)
    st.markdown(f"""<div class="card" style="margin-top:1rem">
    <p style='color:#e8d8b8;font-size:0.85rem;margin:0'>
    📊 <b>{words}</b> words · 
    ⏱️ ~{est_min}m {est_sec % 60}s spoken at normal pace ·
    🎬 {len(scenes)} scenes
    </p></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    lc, rc = st.columns(2)
    with lc:
        if st.button("← Back", use_container_width=True):
            st.session_state.step = 2; st.rerun()
    with rc:
        if st.button("Next → Generate Voiceover", use_container_width=True):
            st.session_state.step = 4; st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# STEP 4 — VOICEOVER
# ══════════════════════════════════════════════════════════════════════════════
def step4():
    st.markdown("### 🎙️ Generate AI Voiceover")

    scenes  = st.session_state.scenes
    vid     = VOICES[st.session_state.voice]
    mid     = MODELS[st.session_state.model]
    done    = set(st.session_state.audios.keys())
    n_done  = len(done)
    n_total = len(scenes)
    all_ok  = (n_done == n_total)

    st.markdown(f"""<div class="info">
    🎙️ <b>{st.session_state.voice}</b> &nbsp;·&nbsp;
    ⚡ <b>{st.session_state.model.split('—')[0].strip()}</b> &nbsp;·&nbsp;
    ✅ <b>{n_done}/{n_total}</b> scenes generated
    </div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    ga, gb = st.columns([2,1])
    with ga:
        if st.button("⚡ Generate ALL Voiceovers", use_container_width=True, disabled=all_ok):
            pb  = st.progress(0)
            msg = st.empty()
            for i, sc in enumerate(scenes):
                if sc["id"] in done: continue
                msg.markdown(f'<div class="info">🎙️ Recording: <b>{sc["name"]}</b> ({i+1}/{n_total})…</div>', unsafe_allow_html=True)
                try:
                    a = gen_tts(st.session_state.api_key, sc["script"],
                                vid, mid, st.session_state.speed)
                    st.session_state.audios[sc["id"]] = a
                    done.add(sc["id"])
                except requests.HTTPError as e:
                    code = e.response.status_code if e.response else 0
                    st.error(f"HTTP {code}: {'❌ Invalid API Key — check your credentials.' if code==401 else str(e)}")
                    break
                except Exception as e:
                    st.error(f"Error on scene {sc['name']}: {e}"); break
                pb.progress((i+1)/n_total)
                time.sleep(0.05)
            pb.empty(); msg.empty(); st.rerun()

    with gb:
        if st.button("🗑️ Reset Voiceovers", use_container_width=True):
            st.session_state.audios = {}; st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    for sc in scenes:
        sid  = sc["id"]
        has  = sid in st.session_state.audios
        m    = sc.get("media")

        ca, cb, cc = st.columns([2.5, 1.5, 1.5])
        with ca:
            icon = "✅" if has else "⬜"
            m_info = ""
            if m:
                em = "🎬" if m["type"]=="video" else "🖼️"
                m_info = f"<span style='color:#6a5840;font-size:0.68rem'> · {em} {m['label'][:25]}</span>"
            st.markdown(f"""<div class="scene-row">
            <div class="scene-type">{icon} {sc['scene_type'].upper()}{m_info}</div>
            <div class="scene-name">{sc['name']}</div>
            <div class="scene-script">"{sc['script'][:120]}{'…' if len(sc['script'])>120 else ''}"</div>
            </div>""", unsafe_allow_html=True)
        with cb:
            if has:
                st.audio(st.session_state.audios[sid], format="audio/mp3")
                st.download_button(f"⬇️ MP3", data=st.session_state.audios[sid],
                    file_name=f"review_{sid}.mp3", mime="audio/mpeg",
                    key=f"dl_{sid}", use_container_width=True)
        with cc:
            if not has:
                if st.button(f"🎙️ Record", key=f"rec_{sid}", use_container_width=True):
                    with st.spinner(f"Generating {sc['name']}…"):
                        try:
                            a = gen_tts(st.session_state.api_key, sc["script"],
                                        vid, mid, st.session_state.speed)
                            st.session_state.audios[sid] = a; st.rerun()
                        except Exception as e:
                            st.error(str(e))
            else:
                if st.button(f"🔄 Re-record", key=f"re_{sid}", use_container_width=True):
                    st.session_state.audios.pop(sid, None); st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    all_ok2 = all(s["id"] in st.session_state.audios for s in scenes)
    lc, rc  = st.columns(2)
    with lc:
        if st.button("← Back", use_container_width=True):
            st.session_state.step = 3; st.rerun()
    with rc:
        if st.button("🎬 Next → Render Video", use_container_width=True, disabled=not all_ok2):
            st.session_state.step = 5; st.rerun()
        if not all_ok2:
            missing = n_total - len(st.session_state.audios)
            st.markdown(f"<small style='color:#6a5840'>{missing} scene(s) still need voiceover</small>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# STEP 5 — RENDER
# ══════════════════════════════════════════════════════════════════════════════
def step5():
    st.markdown("### 🎬 Render Your Review Video")

    scenes = st.session_state.scenes
    m_url  = MUSIC[st.session_state.music]

    # ── Summary
    n_img = sum(1 for m in st.session_state.media_links if m["type"]=="image")
    n_vid = sum(1 for m in st.session_state.media_links if m["type"]=="video")
    asin_str = f" · ASIN: {st.session_state.asin}" if st.session_state.asin else ""

    st.markdown(f"""<div class="card">
    <div class="card-lbl">Render Summary</div>
    <p style='color:#e8d8b8;font-size:0.88rem;line-height:2.1;margin:0'>
    📦 <b>{st.session_state.product}</b>{asin_str}<br>
    ⭐ {stars_html(st.session_state.rating)} ({st.session_state.rating}/5) · {st.session_state.template.split()[0]}<br>
    🖼️ {n_img} images · 🎬 {n_vid} videos · 📐 1280×720 HD · 🎞️ 24fps<br>
    🎙️ {st.session_state.voice} · 🎵 {st.session_state.music}
    </p></div>""", unsafe_allow_html=True)

    # ── Already rendered
    if st.session_state.video:
        st.markdown('<div class="ok">✅ Video ready! Preview below, then download.</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.video(st.session_state.video)
        fn = f"{re.sub(r'[^a-z0-9]+', '_', st.session_state.product.lower())}_amazon_review.mp4"
        st.download_button(
            "⬇️  Download Review Video (MP4)",
            data=st.session_state.video, file_name=fn,
            mime="video/mp4", use_container_width=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)
        ca, cb = st.columns(2)
        with ca:
            if st.button("🔄 Re-render with changes", use_container_width=True):
                st.session_state.video = None; st.rerun()
        with cb:
            if st.button("🆕 Start New Review", use_container_width=True):
                for k, v in D.items(): st.session_state[k] = v
                st.rerun()
        return

    # ── Dependency check
    if not PIL_OK or not MPY_OK:
        missing = [p for p, ok in [("Pillow", PIL_OK), ("moviepy", MPY_OK)] if not ok]
        st.markdown(f"""<div class="warn">
        ⚠️ Missing packages: <b>{', '.join(missing)}</b><br><br>
        Add to <b>requirements.txt</b>:<br>
        <code style="color:#fcd34d">Pillow>=10.0.0<br>moviepy>=1.0.3</code><br><br>
        You can still download individual voiceover MP3s from Step 4.
        </div>""", unsafe_allow_html=True)
        if st.button("← Back", use_container_width=True):
            st.session_state.step = 4; st.rerun()
        return

    # ── Render button
    st.markdown("<br>", unsafe_allow_html=True)
    rc, _ = st.columns([1, 1])
    with rc:
        if st.button("🚀 Render Review Video", use_container_width=True):
            tmpdir = tempfile.mkdtemp()
            clips  = []
            pb     = st.progress(0)
            msg    = st.empty()
            n      = len(scenes)
            errors = []

            for i, sc in enumerate(scenes):
                msg.markdown(f'<div class="info">⚙️ Rendering scene {i+1}/{n}: <b>{sc["name"]}</b>…</div>', unsafe_allow_html=True)

                # Save audio
                audio_bytes = st.session_state.audios[sc["id"]]
                ap = os.path.join(tmpdir, f"a{i}.mp3")
                with open(ap, "wb") as f: f.write(audio_bytes)
                ac = mpy.AudioFileClip(ap)
                dur = ac.duration + 0.3

                m = sc.get("media")
                clip_made = False

                # ── Video clip from user's video link
                if m and m["type"] == "video":
                    try:
                        vp = download_media(m["url"], tmpdir, i, "video")
                        if vp:
                            vc = mpy.VideoFileClip(vp).resize((1280, 720))
                            if vc.duration > dur:
                                vc = vc.subclip(0, dur)
                            elif vc.duration < dur:
                                reps = int(dur / vc.duration) + 1
                                vc   = mpy.concatenate_videoclips([vc]*reps).subclip(0, dur)
                            vc = vc.set_audio(ac).fadein(0.25).fadeout(0.25)
                            clips.append(vc)
                            clip_made = True
                    except Exception as e:
                        errors.append(f"Video error scene {i+1}: {e}")

                # ── Image clip from user's image link
                if not clip_made and m and m["type"] == "image":
                    try:
                        ip = download_media(m["url"], tmpdir, i, "image")
                        if ip:
                            pil_img = Image.open(ip)
                            pil_img = make_overlay_frame(pil_img, sc, st.session_state.product)
                            op = os.path.join(tmpdir, f"slide_{i}.png")
                            pil_img.save(op)
                            ic = (mpy.ImageClip(op).set_duration(dur)
                                  .set_audio(ac).fadein(0.3).fadeout(0.3))
                            clips.append(ic)
                            clip_made = True
                    except Exception as e:
                        errors.append(f"Image error scene {i+1}: {e}")

                # ── Fallback: text-only slide
                if not clip_made:
                    try:
                        fb = Image.new("RGB", (1280, 720), (12, 10, 8))
                        d  = ImageDraw.Draw(fb)
                        # Gradient
                        for x in range(1280):
                            t = x/1280
                            r = int(12 + 30*t*0.3)
                            g = int(10 + 10*t*0.1)
                            b = int(8  + 20*t*0.2)
                            d.line([(x,0),(x,720)], fill=(r,g,b))
                        d.rectangle([0,0,5,720], fill=(255,153,0))
                        d.text((40, 40), sc["scene_type"].upper(), fill=(255,153,0))
                        # Product name
                        pn = (st.session_state.product[:30]+"…") if len(st.session_state.product)>30 else st.session_state.product
                        d.text((40, 80), pn, fill=(230,210,170))
                        # Script wrapped
                        words_s = sc["script"].split()
                        lines, cur = [], ""
                        for w in words_s:
                            if len(cur)+len(w)+1 <= 55:
                                cur = (cur+" "+w).strip()
                            else:
                                lines.append(cur); cur = w
                        if cur: lines.append(cur)
                        for li, ln in enumerate(lines[:6]):
                            color = (255,153,0) if li==0 else (200,185,165)
                            d.text((40, 200+li*60), ln, fill=color)
                        # Stars
                        if sc.get("rating"):
                            d.text((40, 600), "★"*sc["rating"]+"☆"*(5-sc["rating"]), fill=(255,153,0))
                        fp = os.path.join(tmpdir, f"fb_{i}.png")
                        fb.save(fp)
                        ic = (mpy.ImageClip(fp).set_duration(dur)
                              .set_audio(ac).fadein(0.3).fadeout(0.3))
                        clips.append(ic)
                        clip_made = True
                    except Exception as e:
                        errors.append(f"Fallback error scene {i+1}: {e}")

                pb.progress((i+1)/(n+2))

            if clips:
                msg.markdown('<div class="info">⚙️ Compositing all scenes…</div>', unsafe_allow_html=True)
                final = mpy.concatenate_videoclips(clips, method="compose")

                # Background music
                if m_url:
                    try:
                        mr  = requests.get(m_url, timeout=20)
                        mp  = os.path.join(tmpdir, "music.mp3")
                        with open(mp, "wb") as f: f.write(mr.content)
                        mc  = mpy.AudioFileClip(mp).volumex(0.08).audio_fadein(2).audio_fadeout(3)
                        if mc.duration < final.duration:
                            reps = int(final.duration/mc.duration)+1
                            mc   = mpy.concatenate_audioclips([mc]*reps)
                        mc    = mc.set_duration(final.duration)
                        mixed = mpy.CompositeAudioClip([final.audio, mc])
                        final = final.set_audio(mixed)
                    except Exception:
                        pass

                msg.markdown('<div class="info">⚙️ Encoding MP4 (this may take 1–3 mins)…</div>', unsafe_allow_html=True)
                pb.progress((n+1)/(n+2))
                out = os.path.join(tmpdir, "review.mp4")
                final.write_videofile(out, fps=24, codec="libx264",
                                       audio_codec="aac", logger=None, verbose=False)
                pb.progress(1.0)
                pb.empty(); msg.empty()
                with open(out,"rb") as f:
                    st.session_state.video = f.read()
                if errors:
                    for e in errors:
                        st.warning(f"⚠️ {e}")
                st.rerun()
            else:
                pb.empty(); msg.empty()
                st.error("No clips could be created. Check your media URLs and try again.")
                for e in errors:
                    st.markdown(f'<div class="err">❌ {e}</div>', unsafe_allow_html=True)

    if st.button("← Back to Voiceover", use_container_width=True):
        st.session_state.step = 4; st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
render_hero()
render_steps(st.session_state.step)

{1: step1, 2: step2, 3: step3, 4: step4, 5: step5}[st.session_state.step]()
