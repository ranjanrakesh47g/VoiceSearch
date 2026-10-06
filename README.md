# VoiceSearch

Speech query API. A `.wav` file is transcribed, then searched as news or a product. The same audio can be transcribed by every ASR model for comparison.

## Voice search API

Base URL: `http://127.0.0.1:7680`


| Method | Path            | Body                                        |
| ------ | --------------- | ------------------------------------------- |
| GET    | `/health_check` | none                                        |
| POST   | `/voice_search` | form-data field `file`, type File, a `.wav` |


`/health_check` returns `{"status": "ok"}`.

`/voice_search` returns json having the transcription, intent, searchable query, results, and latencies. The transcription model is selected using `config.yml`

## ASR comparison API

Base URL: `http://127.0.0.1:7681`


| Method | Path            | Body                                        |
| ------ | --------------- | ------------------------------------------- |
| GET    | `/health_check` | none                                        |
| POST   | `/compare`      | form-data field `file`, type File, a `.wav` |


`/compare` returns json having the transcription and latency of each model.

## Steps for running in local

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Voice search:

```bash
python -m src.app.main
```

ASR comparison:

```bash
python -m src.app.asr_comparison.main
```



## Steps for running Docker

Requires an NVIDIA GPU and a `.env` file. Voice search uses it for product search. ASR comparison uses it for Amazon Transcribe.

```bash
docker build -t voicesearch .
```

Voice search:

```bash
docker run --runtime=nvidia -e NVIDIA_VISIBLE_DEVICES=all --env-file .env -p 7680:7680 voicesearch
```

ASR comparison:

```bash
docker run --runtime=nvidia -e NVIDIA_VISIBLE_DEVICES=all --env-file .env -p 7681:7681 voicesearch asr_comparison
```

Both containers can run at the same time, one container each.