from datetime import datetime
from src.utils.transcribe import ASR_MODELS, Transcriber

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
    return results
