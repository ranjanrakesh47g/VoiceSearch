import os

from dotenv import load_dotenv

load_dotenv()

from src.utils.logging_setup import setup_logging

setup_logging()

from src.app.demo import build_demo
from src.utils.intent import IntentDetector
from src.utils.query import QueryExtractor
from src.utils.search import Searcher
from src.utils.transcribe import Transcriber

def main(transcriber=None, intent_detector=None, query_extractor=None, searcher=None):
    transcriber = transcriber or Transcriber()
    intent_detector = intent_detector or IntentDetector()
    query_extractor = query_extractor or QueryExtractor(intent_detector)
    searcher = searcher or Searcher(query_extractor)
    demo = build_demo(transcriber, intent_detector, query_extractor, searcher)
    demo.launch(share=True, server_port=int(os.environ.get("PORT1", 7680)))
    return demo


if __name__ == "__main__":
    main()
