import torch

# Patch torch.load to use weights_only=False by default.
# Required for fairseq checkpoints on PyTorch 2.6+.
_original_torch_load = torch.load
def _patched_torch_load(f, *args, **kwargs):
    kwargs.setdefault("weights_only", False)
    return _original_torch_load(f, *args, **kwargs)
torch.load = _patched_torch_load

from playsound3 import playsound
from rvc_python.infer import RVCInference
import edge_tts
import asyncio

text = "Hello World, my name is John. I am a Twitch streamer and I am testing out my new text to speech system. This is a test message to see how well the TTS works. I hope it sounds good and is clear to understand. Thank you for listening!"


async def edgeTTS(chat):
    print("Sending chat to Edge TTS")
    communicate = edge_tts.Communicate(chat, voice="en-GB-RyanNeural")
    await communicate.save("edge_tts_output.mp3")
    print("Edge TTS returned, sending to RVC model")

    with torch.no_grad():

        rvc = RVCInference(model_path="./tts_models/daniel_uk_oddcast/DanielUK_200e.pth", device="cuda:0")
        rvc.infer_file("./edge_tts_output.mp3", output_path="./audio/rvc_output.wav")
    
    print("Playing RVC output")
    playsound("./audio/rvc_output.wav")


# asyncio.run(edgeTTS(text))