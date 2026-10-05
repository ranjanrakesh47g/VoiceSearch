from datetime import datetime
import torch
from sentence_transformers import SentenceTransformer, util
from .search import PDP_PATH
from .voice_search_model import jsonify


class IntentDetector:
    def __init__(self):
        self.intent_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2",
                                                 device="cuda" if torch.cuda.is_available() else "cpu",
                                                 model_kwargs={"cache_dir": "models"})
        self.intents = ["news", "ecommerce"]
        stores = list(PDP_PATH)
        self.intent_descriptions = ["latest news or headlines about a person or topic",
                                    f"shop for a product on {', '.join(stores[:-1])}, or {stores[-1]}"]
        self.intent_emb = self.intent_model.encode(self.intent_descriptions, normalize_embeddings=True)

    def detect_intent(self, voice_search):
        started = datetime.now()
        emb = self.intent_model.encode(voice_search.user_query_text, normalize_embeddings=True)
        scores = util.cos_sim(emb, self.intent_emb)[0]
        probs = scores.softmax(dim=0)
        i = int(probs.argmax())
        voice_search.intent = self.intents[i]
        voice_search.latency_intent_detection = f"{round((datetime.now() - started).total_seconds() * 1000)} ms"
        return jsonify(voice_search)
