import os
import tempfile
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
import uvicorn
from src.app.asr_comparison.compare_utils import compare
from src.utils.logging_setup import setup_logging

app = FastAPI()


@app.get("/health_check")
def health_check():
    return {"status": "ok"}


@app.post("/compare")
async def compare_audio(file: UploadFile = File(...)):
    if not (file.filename or "").lower().endswith(".wav"):
        raise HTTPException(status_code=400, detail="A .wav file is required")
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty audio file")
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(data)
        path = tmp.name
    try:
        return compare(path)
    finally:
        os.remove(path)


def main():
    load_dotenv()
    setup_logging()
    uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("PORT2", 7681)))


if __name__ == "__main__":
    main()
