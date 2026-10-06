import os
import tempfile
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
import uvicorn
from src.app.voice_search.pipeline import VoiceSearchPipeline
from src.utils.logging_setup import setup_logging

app = FastAPI()
pipeline = VoiceSearchPipeline()


@app.get("/health_check")
def health_check():
    return {"status": "ok"}


@app.post("/voice_search")
async def voice_search(file: UploadFile = File(...)):
    if not (file.filename or "").lower().endswith(".wav"):
        raise HTTPException(status_code=400, detail="A .wav file is required")
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty audio file")
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(data)
        path = tmp.name
    try:
        result = pipeline.run(path)
    finally:
        os.remove(path)
    return result.__dict__


def main():
    load_dotenv()
    setup_logging()
    uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("PORT1", 7680)))


if __name__ == "__main__":
    main()
