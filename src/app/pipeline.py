import json
import os
from datetime import datetime
from src.utils.intent import IntentDetector
from src.utils.logging_setup import setup_logging
from src.utils.query import QueryExtractor
from src.utils.search import Searcher
from src.utils.transcribe import Transcriber
from src.utils.voice_search_model import VoiceSearch

voice_search_logger = setup_logging()


def inference_hardware(asr):
    if getattr(asr, "hardware", None):
        return asr.hardware
    on_gpu = asr.device.type == "cuda"
    in_colab = "COLAB_RELEASE_TAG" in os.environ
    if on_gpu and in_colab:
        return "colab gpu"
    if on_gpu:
        return "local gpu"
    return "cpu"


class VoiceSearchPipeline:
    def __init__(self, transcriber=None, intent_detector=None, query_extractor=None, searcher=None):
        self.transcriber = transcriber or Transcriber()
        self.intent_detector = intent_detector or IntentDetector()
        self.query_extractor = query_extractor or QueryExtractor(self.intent_detector)
        self.searcher = searcher or Searcher(self.query_extractor)

    def run(self, filepath):
        voice_search = VoiceSearch(user_query_audio=filepath)
        self.transcriber.transcribe_speech(voice_search)
        if voice_search.user_query_text:
            self.intent_detector.detect_intent(voice_search)
            self.query_extractor.extract_query(voice_search)
            try:
                self.searcher.search_results(voice_search)
            except Exception as error:
                voice_search.search_results = [{"error": str(error)}]
                parts = [voice_search.latency_transcription, voice_search.latency_intent_detection, voice_search.latency_query_extraction]
                voice_search.latency_overall = f"{sum(int(part.split()[0]) for part in parts if part)} ms"

        voice_search_logger.info(json.dumps({"time": datetime.now().isoformat(), **voice_search.__dict__,
                                             "model": getattr(self.transcriber.asr, "name", None) or self.transcriber.asr.model.name_or_path,
                                             "hardware": inference_hardware(self.transcriber.asr)}))
        voice_search_logger.info("")
        return voice_search
