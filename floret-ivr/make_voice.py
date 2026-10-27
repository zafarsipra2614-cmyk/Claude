"""Generate the Floret Capitals IVR voice clips with edge-tts.

Usage: python3 make_voice.py <female|male> <clips_dir>
"""
import asyncio, os, ssl, sys, edge_tts
import edge_tts.communicate as _c

# Use a custom CA bundle when running behind a TLS-inspecting proxy.
if os.environ.get("TTS_CA_BUNDLE"):
    _c._SSL_CTX = ssl.create_default_context(cafile=os.environ["TTS_CA_BUNDLE"])

VOICES = {
    "female": ("en-IN-NeerjaNeural", "ur-PK-UzmaNeural"),
    "male":   ("en-IN-PrabhatNeural", "ur-PK-AsadNeural"),
}
RATE = "-8%"   # a little slower for phone lines without sounding dragged

# Written as natural sentences so the voice keeps its normal flow.
# Each section is one utterance (no splicing) to avoid a stitched, robotic sound.
LINES = {
    "01_en_greeting": ("en", "Thank you for calling Flor-et Capitals."),
    "02_ur_greeting": ("ur", "فلورِٹ کیپٹلز کو کال کرنے کا شکریہ۔"),
    "03_en_menu":     ("en", "Press 1 for P M E X. Press 2 for P S X."),
    "04_ur_menu":     ("ur", "پی ایم ای ایکس کے لیے ایک دبائیں۔ پی ایس ایکس کے لیے دو دبائیں۔"),
    "05_en_hold":     ("en", "Please hold while we connect you to a representative."),
    "06_ur_hold":     ("ur", "براہِ کرم انتظار فرمائیں، ہم آپ کو ہمارے نمائندے سے ملا رہے ہیں۔"),
}

async def main(gender, out):
    en, ur = VOICES[gender]
    for name, (lang, text) in LINES.items():
        voice = en if lang == "en" else ur
        await edge_tts.Communicate(text, voice, rate=RATE).save(f"{out}/{name}.mp3")

asyncio.run(main(sys.argv[1], sys.argv[2]))
