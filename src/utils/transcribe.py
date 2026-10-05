import os
import shutil
from datetime import datetime

import gradio as gr
from transformers import pipeline

from .voice_search_model import jsonify


def save_audio(filepath, text):
    if filepath is None:
        return None
    audio_dir = os.path.abspath("logs/audio")
    os.makedirs(audio_dir, exist_ok=True)
    src = os.path.abspath(filepath)
    stem = "".join(c for c in text.strip() if c.isalnum() or c in " ,.'-")[:80].strip() or "audio"
    ext = os.path.splitext(src)[1] or ".wav"
    dest = os.path.join(audio_dir, stem + ext)
    i = 2
    while os.path.exists(dest):
        dest = os.path.join(audio_dir, f"{stem} {i}{ext}")
        i += 1
    if src.startswith(audio_dir + os.sep):
        os.replace(src, dest)
        os.rmdir(os.path.dirname(src))
    else:
        shutil.copy(src, dest)
    return os.path.relpath(dest)


class Transcriber:
    def __init__(self):
        self.asr = pipeline(task="automatic-speech-recognition",
                            model="distil-whisper/distil-small.en",
                            model_kwargs={"cache_dir": "models"})
        print("asr_freq:", self.asr.feature_extractor.sampling_rate)

    def transcribe_speech(self, voice_search):
        filepath = voice_search.user_query_audio
        latency_ms = None
        if filepath is None:
            gr.Warning("No audio found, please retry.")
            voice_search.user_query_text = ""
        else:
            started = datetime.now()
            output = self.asr(filepath)
            latency_ms = round((datetime.now() - started).total_seconds() * 1000)
            voice_search.user_query_text = output["text"]
            voice_search.latency_transcription = f"{latency_ms} ms"
        voice_search.user_query_audio = save_audio(filepath, voice_search.user_query_text)
        return jsonify(voice_search)
