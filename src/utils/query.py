from datetime import datetime
import torch
from gliner import GLiNER
from sentence_transformers import util
from .voice_search_model import jsonify

INTENT_LABELS = {
        "news": ["person", "organization", "place"],
        "ecommerce": ["item", "product"],
    }


class QueryExtractor:
    def __init__(self, intent_detector):
        self.intent_model = intent_detector.intent_model
        self.intents = intent_detector.intents
        self.intent_emb = intent_detector.intent_emb
        self.ner_model = GLiNER.from_pretrained("urchade/gliner_small-v2.1",
                                                 map_location="cuda" if torch.cuda.is_available() else "cpu",
                                                 cache_dir="models")

    def extract_query(self, voice_search):
        started = datetime.now()
        text = voice_search.user_query_text
        intent = voice_search.intent
        spans = list(dict.fromkeys(
            e["text"] for e in self.ner_model.predict_entities(text, INTENT_LABELS[intent], threshold=0.4)
        ))
        if spans:
            emb = self.intent_model.encode([text, *spans], normalize_embeddings=True)
            target = self.intent_emb[self.intents.index(intent)]
            scores = util.cos_sim(emb[0], emb[1:])[0] + 2 * util.cos_sim(target, emb[1:])[0]
            probs = scores.softmax(dim=0)
            i = int(probs.argmax())
            voice_search.searchable_query = spans[i]
        else:
            voice_search.searchable_query = ""
        voice_search.latency_query_extraction = f"{round((datetime.now() - started).total_seconds() * 1000)} ms"
        return jsonify(voice_search)
