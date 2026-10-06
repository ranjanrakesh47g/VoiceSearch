FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src src
COPY config.yml config.yml
EXPOSE 7680 7681
ENTRYPOINT ["sh", "-c", "if [ \"$0\" = asr_comparison ]; then exec python -m uvicorn src.app.asr_comparison.api:app --host 0.0.0.0 --port 7681; else exec python -m uvicorn src.app.api:app --host 0.0.0.0 --port 7680; fi"]
CMD ["voice_search"]
