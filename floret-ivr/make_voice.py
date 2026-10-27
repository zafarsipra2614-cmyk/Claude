"""Generate the Floret Capitals IVR voice clips with edge-tts."""
import asyncio, os, ssl, sys, edge_tts
import edge_tts.communicate as _c

# Use a custom CA bundle when running behind a TLS-inspecting proxy.
if os.environ.get("TTS_CA_BUNDLE"):
    _c._SSL_CTX = ssl.create_default_context(cafile=os.environ["TTS_CA_BUNDLE"])

EN = "en-IN-NeerjaNeural"
UR = "ur-PK-UzmaNeural"
RATE = "-10%"   # about 10% slower for phone lines

# Spellings tuned for pronunciation:
#  - "Flor-et" / "فلورِٹ" -> FLOR-et
#  - letters spaced with commas -> P, M, E, X with a small gap
#  - numbers set off with commas so they get a slight stress
LINES = {
    "01_en_greeting": (EN, "Thank you for calling Flor-et Capitals."),
    "02_ur_greeting": (UR, "فلورِٹ کیپٹلز کو کال کرنے کا شکریہ۔"),
    "03_en_menu1":    (EN, "Press, ONE, for P. M. E. X."),
    "04_en_menu2":    (EN, "Press, TWO, for P. S. X."),
    "05_ur_menu1":    (UR, "پی، ایم، ای، ایکس کے لیے، ایک، دبائیں۔"),
    "06_ur_menu2":    (UR, "پی، ایس، ایکس کے لیے، دو، دبائیں۔"),
    "07_en_hold":     (EN, "Please hold, while we connect you to a representative."),
    "08_ur_hold":     (UR, "براہِ کرم انتظار فرمائیں، ہم آپ کو ہمارے نمائندے سے ملا رہے ہیں۔"),
}

async def main(out):
    for name, (voice, text) in LINES.items():
        await edge_tts.Communicate(text, voice, rate=RATE).save(f"{out}/{name}.mp3")
        print("made", name)

asyncio.run(main(sys.argv[1]))
