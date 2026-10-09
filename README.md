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

Product queries are sent to the Brave Search API and require `BRAVE_API_KEY` in `.env`. The transcript is scanned for a store name. When one is found, the query is restricted to that site and to a product-page path for Amazon, eBay, Walmart, Target, Best Buy, Etsy, Flipkart, or Myntra. The response contains up to five items, each with a title, a URL, and a description. If the search request fails, the result is a single item whose `error` field contains the failure message.

## Interfaces

The Gradio UI and the FastAPI service both use port `7680`. Run one at a time. Open the Gradio UI at `http://127.0.0.1:7680`. The process also prints a temporary public URL; use the local address.

The microphone tab runs the pipeline when recording stops. The file tab runs it when a `.wav` file is uploaded. The page shows the transcript, intent, searchable query, search results, and latencies.

The FastAPI base URL is `http://127.0.0.1:7680`. The local port can be changed with `PORT1`.


| Method | Path            | Body                                  |
| ------ | --------------- | ------------------------------------- |
| GET    | `/health_check` | none                                  |
| POST   | `/voice_search` | form-data field `file`, a `.wav` file |


`/health_check` returns `{"status": "ok"}`.

`/voice_search` rejects a missing, empty, or non-`.wav` file with HTTP 400. A successful response contains:


| Field                      | Description                                                    |
| -------------------------- | -------------------------------------------------------------- |
| `user_query_audio`         | Path of the saved recording, relative to the working directory |
| `user_query_text`          | Transcript                                                     |
| `intent`                   | `news` or `ecommerce`                                          |
| `searchable_query`         | Phrase used for search                                         |
| `search_results`           | List of result objects                                         |
| `latency_transcription`    | Transcription time, in milliseconds                            |
| `latency_intent_detection` | Intent detection time, in milliseconds                         |
| `latency_query_extraction` | Query extraction time, in milliseconds                         |
| `latency_search`           | Search time, in milliseconds                                   |
| `latency_overall`          | Sum of the stage times, in milliseconds                        |


`voice_search.ipynb` walks through the same stages and can launch the Gradio UI locally or in Google Colab. In Colab, the UI is exposed with a temporary public link.

## Local setup

Python 3.12 is required.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the project root. Set `BRAVE_API_KEY` for product search. Set the AWS variables above only when `asr_model` is `aws`.

Gradio UI:

```bash
python -m src.app.gradio_demo
```

FastAPI:

```bash
python -m src.app.api
```



## Docker

The image is based on Python 3.12 and includes FFmpeg. An NVIDIA GPU and a `.env` file are required. The `.env` file supplies `BRAVE_API_KEY` for product search.

```bash
docker build -t voicesearch .
```

Gradio UI:

```bash
docker run --runtime=nvidia -e NVIDIA_VISIBLE_DEVICES=all --env-file .env -p 7680:7680 voicesearch gradio
```

FastAPI, which is the image default:

```bash
docker run --runtime=nvidia -e NVIDIA_VISIBLE_DEVICES=all --env-file .env -p 7680:7680 voicesearch
```

