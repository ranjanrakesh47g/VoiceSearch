import json
from dataclasses import dataclass


@dataclass
class VoiceSearch:
    user_query_audio: str | None = None
    user_query_text: str | None = None
    intent: str | None = None
    searchable_query: str | None = None
    search_results: list | None = None
    latency_transcription: str | None = None
    latency_intent_detection: str | None = None
    latency_query_extraction: str | None = None
    latency_search: str | None = None
    latency_overall: str | None = None

    def __str__(self):
        return json.dumps(self.__dict__, indent=2)


def jsonify(voice_search):
    return str(voice_search)
