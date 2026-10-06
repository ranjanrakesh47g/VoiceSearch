import json
import logging
from datetime import datetime
from src.utils.logging_setup import setup_logging
from src.utils.transcribe import ASR_MODELS, Transcriber, save_audio

setup_logging()
logger = logging.getLogger("asr_comparison")

MODELS = [*ASR_MODELS, "aws"]
transcribers = {name: Transcriber(model=name) for name in MODELS}


def compare(filepath):
    results = {}
    for name, transcriber in transcribers.items():
        started = datetime.now()
        try:
            text = transcriber.asr(filepath)["text"]
        except Exception as error:
            text = str(error)
        latency_ms = round((datetime.now() - started).total_seconds() * 1000)
        results[name] = {"text": text, "latency": f"{latency_ms} ms"}
    text = results["whisper-small"]["text"].strip() or "null"
    saved = save_audio(filepath, text, "logs/audio_comparison")
    logger.info(json.dumps({"time": datetime.now().isoformat(), "user_query_audio": saved, "transcriptions": results}))
    logger.info("")
    return results
