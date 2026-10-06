import os
import tempfile
from fastapi import FastAPI, File, HTTPException, UploadFile
from src.app.asr_comparison.compare_utils import compare

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
