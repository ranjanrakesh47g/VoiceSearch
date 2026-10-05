# VoiceSearch

## APIs
Health Check API (GET): http://127.0.0.1:7680/health_check

Voice Search API (POST): http://127.0.0.1:7680/voice_search

For Voice Search API:
    - Open Body and choose form-data.
    - Set the key name to file, type to File.
    - Choose/Upload .wav file.

## Steps for Local Setup
```bash
python3.12 -m venv .venv; source .venv/bin/activate
pip install -r requirements.txt
python -m src.app.main
```

## Steps for Running Docker
```
docker build -t voicesearch .
docker run --runtime=nvidia -e NVIDIA_VISIBLE_DEVICES=all --env-file .env -p 7680:7680 voicesearch
```