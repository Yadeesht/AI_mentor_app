import asyncio
import edge_tts

def generate_and_play_audio(text, voice="en-IN-NeerjaNeural", model=None):
    async def tts():
        communicate = edge_tts.Communicate(text, voice,rate="+20%")
        await communicate.save("output.mp3")
        print("Audio saved as output.mp3")
    asyncio.run(tts())
    return "output.mp3"
