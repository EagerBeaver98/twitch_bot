from playsound3 import playsound
from gtts import gTTS
from kokoro import KPipeline
import torchaudio


async def standardTTS(chat):
    print(f"Initiallizing TTS")
    pipeline = KPipeline(lang_code="a")
    print(f"Sending chat to TTS pipeline")
    results = pipeline(chat, voice="am_adam")
    for result in results:
        audio = result.audio
        torchaudio.save("./audio/kokoro-output.wav", audio, 24000)
        print(f"Received TTS results, saving audio and playing sound")
        playsound("./audio/kokoro-output.wav")


# text = "The quick brown fox jumps over the lazy dog"

# pipeline = KPipeline(lang_code="a")

# results = pipeline(text, voice="am_adam")

# for result in results:
#     audio = result.audio

#     torchaudio.save("/audio/kokoro-output.wav", audio, 24000)

#     playsound("kokoro-output.wav")
    


# tts = gTTS(text, lang='en')
# tts.save("gtts_output.mp3")
# print("Audio saved to gtts_output.mp3")
# playsound("gtts_output.mp3")