from fastapi import FastAPI
from src.audio.router import router as audio_router
from src.audio import warmup

app = FastAPI(title="Audio deepfake detector")
app.include_router(audio_router)

@app.on_event("startup")
def load_model():
    warmup()