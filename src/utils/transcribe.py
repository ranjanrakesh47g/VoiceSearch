import asyncio
import os
import shutil
from datetime import datetime
import gradio as gr
import yaml
from transformers import pipeline
from .voice_search_model import jsonify
import librosa
import numpy as np
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from dotenv import load_dotenv
from amazon_transcribe.auth import StaticCredentialResolver

load_dotenv()

ASR_MODELS = {
    "whisper-small": "distil-whisper/distil-small.en",
    "whisper-large": "openai/whisper-large-v3",
    "parakeet": "ai-and-i-project/parakeet-tdt-0.6b-v2-hf",
}


def save_audio(filepath, text, audio_dir="logs/audio"):
    if filepath is None:
        return None
    audio_dir = os.path.abspath(audio_dir)
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


def run_async(coro):
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(1) as pool:
        return pool.submit(asyncio.run, coro).result()


class AmazonTranscribe:
    name = "amazon-transcribe"
    hardware = "aws"

    def __call__(self, filepath):
        audio, _ = librosa.load(filepath, sr=16000, mono=True)
        pcm = (np.clip(audio, -1, 1) * 32767).astype("<i2").tobytes()
        lines = []

        class Handler(TranscriptResultStreamHandler):
            async def handle_transcript_event(self, event):
                for result in event.transcript.results:
                    if not result.is_partial and result.alternatives:
                        lines.append(result.alternatives[0].transcript)

        async def transcribe():
            access_key = os.getenv("AWS_ACCESS_KEY_ID")
            secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
            region = os.getenv("AWS_DEFAULT_REGION")
            client = TranscribeStreamingClient(
                region=region,
                credential_resolver=StaticCredentialResolver(access_key, secret_key, os.getenv("AWS_SESSION_TOKEN")),
            )
            stream = await client.start_stream_transcription(language_code="en-US", media_sample_rate_hz=16000, media_encoding="pcm")

            async def send():
                await stream.input_stream.send_audio_event(audio_chunk=pcm)
                await stream.input_stream.end_stream()

            await asyncio.gather(send(), Handler(stream.output_stream).handle_events())
            return " ".join(lines)

        return {"text": run_async(transcribe())}


def configured_asr_model():
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "config.yml"))
    with open(path) as config_file:
        config = yaml.safe_load(config_file) or {}
    asr_model = config.get("asr_model")
    return asr_model


class Transcriber:
    def __init__(self, model=None):
        asr_model = model or configured_asr_model()
        if asr_model == "aws":
            self.asr = AmazonTranscribe()
        else:
            self.asr = pipeline(task="automatic-speech-recognition",
                                model=ASR_MODELS[asr_model],
                                model_kwargs={"cache_dir": "models"})
        print("asr:", getattr(self.asr, "name", None) or self.asr.model.name_or_path)
        if getattr(self.asr, "feature_extractor", None):
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
