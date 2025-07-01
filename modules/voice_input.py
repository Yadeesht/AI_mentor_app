import speech_recognition as sr
import io

def transcribe_audio(wav_audio_data: bytes):
    if not wav_audio_data:
        return None, None

    r = sr.Recognizer()
    
    audio_bytes = io.BytesIO(wav_audio_data)
    with sr.AudioFile(audio_bytes) as source:
        try:
            audio = r.record(source)
            text = r.recognize_google(audio)
            return text, None 
        except sr.UnknownValueError:
            return None, "Could not understand the audio. Please try speaking again."
        except sr.RequestError as e:
            return None, f"Speech service unavailable; {e}"