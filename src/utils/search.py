import json
import os
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

from dotenv import load_dotenv

from .voice_search_model import jsonify

load_dotenv()

PDP_PATH = {
    "amazon.com": "inurl:/dp/",
    "ebay.com": "inurl:/itm/",
    "walmart.com": "inurl:/ip/",
    "target.com": "inurl:/p/",
    "bestbuy.com": "inurl:.p",
    "etsy.com": "inurl:/listing/",
    "flipkart.com": "inurl:/p/",
    "myntra.com": "inurl:/buy",
}


class Searcher:
    def __init__(self, query_extractor):
        self.ner_model = query_extractor.ner_model

    def store_site(self, text):
        orgs = self.ner_model.predict_entities(text, ["organization"], threshold=0.4)
        people = {e["text"].lower() for e in self.ner_model.predict_entities(text, ["person"], threshold=0.3)}
        for org in orgs:
            if org["text"].lower() in people:
                continue
            name = org["text"].lower().removeprefix("www.").rstrip(".")
            return name if "." in name else f"{name}.com"
        return None

    def product_query(self, text, searchable_query):
        site = self.store_site(text)
        if not site:
            return f"buy {searchable_query}"
        return f"buy {searchable_query} site:{site} {PDP_PATH.get(site, '')}".rstrip()

    def news_hits(self, searchable_query):
        url = "https://news.google.com/rss/search?" + urllib.parse.urlencode({"q": searchable_query, "hl": "en-US", "gl": "US", "ceid": "US:en"})
        with urllib.request.urlopen(url, timeout=5) as response:
            root = ET.fromstring(response.read())
        return [{"title": item.findtext("title"), "url": item.findtext("link")} for item in root.findall("./channel/item")[:5]]

    def product_hits(self, text, searchable_query):
        url = "https://api.search.brave.com/res/v1/web/search?" + urllib.parse.urlencode({"q": self.product_query(text, searchable_query), "count": 5})
        request = urllib.request.Request(url, headers={"Accept": "application/json", "X-Subscription-Token": os.environ.get("BRAVE_API_KEY")})
        with urllib.request.urlopen(request, timeout=5) as response:
            data = json.load(response)
        return [{"title": hit["title"], "url": hit["url"], "description": hit.get("description")} for hit in data.get("web", {}).get("results", [])[:5]]

    def search_results(self, voice_search):
        started = datetime.now()
        if voice_search.intent == "news":
            hits = self.news_hits(voice_search.searchable_query)
        else:
            hits = self.product_hits(voice_search.user_query_text, voice_search.searchable_query)
        voice_search.search_results = hits
        voice_search.latency_search = f"{round((datetime.now() - started).total_seconds() * 1000)} ms"
        parts = [
            voice_search.latency_transcription,
            voice_search.latency_intent_detection,
            voice_search.latency_query_extraction,
            voice_search.latency_search,
        ]
        voice_search.latency_overall = f"{sum(int(part.split()[0]) for part in parts if part)} ms"
        return jsonify(voice_search)
