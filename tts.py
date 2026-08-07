import torch

# Patch torch.load to use weights_only=False by default.
# Required for fairseq checkpoints on PyTorch 2.6+.
_original_torch_load = torch.load
def _patched_torch_load(f, *args, **kwargs):
    kwargs.setdefault("weights_only", False)
    return _original_torch_load(f, *args, **kwargs)
torch.load = _patched_torch_load

from playsound3 import playsound
# from TTS.api import TTS
from rvc_python.infer import RVCInference
import edge_tts
import asyncio

# device = "cuda" if torch.cuda.is_available() else "cpu"

text = "Once there was a young rat named Arthur, who could never make up his mind. Whenever his friends asked him if he would like to go out with them, he would only answer, I don't know. He wouldn't say yes or no either. He would always shirk making a choice. His aunt Helen said to him, Now look here. No one is going to care for you if you carry on like this. You have no more mind than a blade of grass. One rainy day, the rats heard a great noise in the loft. The pine rafters were all rotten, so that the barn was rather unsafe. At last the joists gave way and fell to the ground. The walls shook and all the rats' hair stood on end with fear and horror. This won't do, said the captain. I'll send out scouts to search for a new home."

print("Initializing tts")
# tts = TTS(model_path = "./tts_models/daniel_uk_oddcast/DanielUK_200e.pth").to(device)

# async def coquiTTS(chat):
#     await tts.tts_to_file(text=chat, file_path="./audio/coqui_output.wav")
#     playsound("./audio/coqui_output.wav")

async def edgeTTS(chat):
    print("Sending chat to Edge TTS")
    communicate = edge_tts.Communicate(chat, voice="en-GB-RyanNeural")
    await communicate.save("./audio/edge_tts_output.mp3")
    print("Edge TTS returned, sending to RVC model")

    with torch.no_grad():

        rvc = RVCInference(model_path="./tts_models/daniel_uk_oddcast/DanielUK_200e.pth", device="cuda:0")
        rvc.infer_file("./audio/edge_tts_output.mp3", output_path="./audio/rvc_output.wav")
        rvc.unload_model()
    
    print("Playing RVC output")
    playsound("./audio/rvc_output.wav")





if __name__ == "__main__":
    asyncio.run(edgeTTS(text))
