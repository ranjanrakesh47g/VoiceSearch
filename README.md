# VoiceSearch

Speech query API. A `.wav` file is transcribed, then searched as news or a product.

## API

Base URL: `http://127.0.0.1:7680`

| Method | Path | Body |
| --- | --- | --- |
| GET | `/health_check` | none |
| POST | `/voice_search` | form-data field `file`, type File, a `.wav` |

`/health_check` returns `{"status": "ok"}`.

`/voice_search` returns json having the transcription, intent, searchable query, results, and latencies.

## Local

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.app.main
```

## Docker

Requires an NVIDIA GPU and a `.env` file (used for product search).

```bash
docker build -t voicesearch .
docker run --runtime=nvidia -e NVIDIA_VISIBLE_DEVICES=all --env-file .env -p 7680:7680 voicesearch
```
