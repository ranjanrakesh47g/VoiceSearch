# Voice Search

Voice Search accepts a speech recording and returns relevant search results. The `.wav` file is transcribed, the transcript is classified as a news or ecommerce query, a searchable phrase is detected, and that phrase is searched. Per-stage and overall latencies are included in the response. News queries are retrieved from Google News, and product queries from the Brave Search API. 

Each request passes through four stages:

1. Transcription
2. Intent detection
3. Searchable query extraction
4. Search

## Transcription

The transcription model is selected in `config.yml` with `asr_model`.


| **Name**        | **Checkpoint**                             |
| --------------- | ------------------------------------------ |
| `whisper-small` | `distil-whisper/distil-small.en`           |
| `whisper-large` | `openai/whisper-large-v3`                  |
| `parakeet`      | `ai-and-i-project/parakeet-tdt-0.6b-v2-hf` |
| `aws`           | Amazon Transcribe streaming                |


The current configuration uses `parakeet`, which is suited to low-latency transcription. A comparison of these speech-to-text models and commercial APIs is given in the [Noise Cancellation README](https://github.com/ranjanrakesh47g/NoiseCancellation/blob/main/README.md).

## Intent Detection

Intent Detection is done using the embedding model `sentence-transformers/all-MiniLM-L6-v2`. The transcript is compared with two descriptions, and the one with the higher cosine similarity is selected:

- `news`: a request for recent news or headlines about a person or topic
- `ecommerce`: a request to shop for a product



## Searchable Query Extraction

The searchable phrase is extracted with open-vocabulary ner model `urchade/gliner_small-v2.1`. Entity labels depend on the detected intent:

- `news`: person, organization, place
- `ecommerce`: item, product

When several spans are found, the span closest to both the transcript and the selected intent is kept.

## Search

News queries are sent to the Google News RSS feed. The response contains up to five items, each with a title and a URL.

Product queries are sent to the Brave Search API and require `BRAVE_API_KEY` in `.env`. The transcript is scanned for a store name. When one is found, the query is restricted to that site and to a product-page path for the specified store like Amazon, Ebay etc. The response contains up to five items, each with a title, a URL, and a description.



## Interfaces

The Gradio UI and the FastAPI service both use port `7680`. Run one at a time.

- **Gradio** is at `http://127.0.0.1:7680`. The microphone tab runs the pipeline when recording stops, and the file tab runs it when a `.wav` file is uploaded. The page shows the transcript, intent, searchable query, search results, and latencies.
- **FastAPI** is at `http://127.0.0.1:7680`.

  | Method | Path            | Body                                  |
  | ------ | --------------- | ------------------------------------- |
  | GET    | `/health_check` | none                                  |
  | POST   | `/voice_search` | form-data field `file`, a `.wav` file |

  - `/health_check` returns `{"status": "ok"}`.
  - `/voice_search` rejects a missing, empty, or non-`.wav` file with HTTP 400. A successful response returns the saved recording path, transcript, intent (`news` or `ecommerce`), searchable phrase, and relevant search results, along with the latencies (stage-wise as well as overall).

## Local setup

Python 3.12 is required.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the project root. Set `BRAVE_API_KEY` for product search.

Gradio UI:

```bash
python -m src.app.gradio_demo
```

FastAPI:

```bash
python -m src.app.api
```

## Docker

An NVIDIA GPU and a `.env` file are required. The `.env` file supplies `BRAVE_API_KEY` for product search.

```bash
docker build -t voicesearch .
```

Gradio UI:

```bash
docker run --runtime=nvidia -e NVIDIA_VISIBLE_DEVICES=all --env-file .env -p 7680:7680 voicesearch gradio
```

FastAPI:

```bash
docker run --runtime=nvidia -e NVIDIA_VISIBLE_DEVICES=all --env-file .env -p 7680:7680 voicesearch
```

