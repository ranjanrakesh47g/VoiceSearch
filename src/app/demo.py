import json
import os
from datetime import datetime

import gradio as gr

from src.utils.logging_setup import setup_logging

voice_search_logger = setup_logging()

from src.utils.intent import IntentDetector
from src.utils.query import QueryExtractor
from src.utils.search import Searcher
from src.utils.transcribe import Transcriber
from src.utils.voice_search_model import VoiceSearch


def inference_hardware(asr):
    on_gpu = asr.device.type == "cuda"
    in_colab = "COLAB_RELEASE_TAG" in os.environ
    if on_gpu and in_colab:
        return "colab gpu"
    if on_gpu:
        return "local gpu"
    return "cpu"


def build_demo(transcriber=None, intent_detector=None, query_extractor=None, searcher=None):
    transcriber = transcriber or Transcriber()
    intent_detector = intent_detector or IntentDetector()
    query_extractor = query_extractor or QueryExtractor(intent_detector)
    searcher = searcher or Searcher(query_extractor)

    def run_voice_search(filepath):
        if not filepath:
            gr.Warning("Recording is still uploading. Wait a moment and try again.")
            return tuple(gr.skip() for _ in range(5))
        voice_search = VoiceSearch(user_query_audio=filepath)
        transcriber.transcribe_speech(voice_search)
        if voice_search.user_query_text:
            intent_detector.detect_intent(voice_search)
            query_extractor.extract_query(voice_search)
            try:
                searcher.search_results(voice_search)
            except Exception as error:
                voice_search.search_results = str(error)
                parts = [voice_search.latency_transcription, voice_search.latency_intent_detection, voice_search.latency_query_extraction]
                voice_search.latency_overall = f"{sum(int(part.split()[0]) for part in parts if part)} ms"

        voice_search_logger.info(json.dumps({"time": datetime.now().isoformat(), **voice_search.__dict__,
                                             "model": transcriber.asr.model.name_or_path, "hardware": inference_hardware(transcriber.asr)}))
        voice_search_logger.info("")

        def component(value, name, latency):
            return gr.update(value=value, label=name if not latency else f"{name} ({latency})")

        return (
            component(voice_search.user_query_text, "Transcription", voice_search.latency_transcription),
            component(voice_search.intent, "Intent", voice_search.latency_intent_detection),
            component(voice_search.searchable_query, "Searchable query", voice_search.latency_query_extraction),
            component(voice_search.search_results, "Search results", voice_search.latency_search),
            voice_search.latency_overall,
        )

    def voice_search_ui(sources):
        audio = gr.Audio(sources=sources, type="filepath", format="wav")
        clear = gr.ClearButton()
        outputs = [
            gr.Textbox(label="Transcription", lines=3),
            gr.Textbox(label="Intent"),
            gr.Textbox(label="Searchable query"),
            gr.JSON(label="Search results"),
            gr.Textbox(label="Overall latency"),
        ]
        clear.add([audio, *outputs])
        if sources == "microphone":
            audio.stop_recording(run_voice_search, inputs=audio, outputs=outputs)
        else:
            audio.upload(run_voice_search, inputs=audio, outputs=outputs)

    with gr.Blocks() as demo:
        with gr.Tabs():
            with gr.Tab("Transcribe Microphone"):
                voice_search_ui("microphone")
            with gr.Tab("Transcribe Audio File"):
                voice_search_ui("upload")

    return demo
