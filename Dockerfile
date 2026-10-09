FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src src
COPY config.yml config.yml
EXPOSE 7680
ENTRYPOINT ["sh", "-c", "case \"$0\" in \
  gradio) exec python -m src.app.gradio_demo ;; \
  *) exec python -m uvicorn src.app.api:app --host 0.0.0.0 --port 7680 ;; \
esac"]
CMD ["voice_search"]
