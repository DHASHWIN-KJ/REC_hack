"""
FastAPI router for the audio module.

In src/api/routes.py (or wherever the FastAPI app is created):

    from src.audio.router import router as audio_router
    app.include_router(audio_router)

Endpoints:
    POST /analyze/audio          (multipart file upload)
    GET  /analyze/audio/health
"""
import os
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from starlette.concurrency import run_in_threadpool

from . import model as model_lib
from .config import get_config
from .detector import analyze_audio
from .preprocess import AudioPreprocessError

router = APIRouter(prefix="/analyze", tags=["audio"])

ALLOWED_EXTS = {".wav", ".flac", ".mp3", ".m4a", ".aac", ".ogg", ".opus",
                ".amr", ".webm", ".mp4", ".mov", ".mkv", ".3gp"}


@router.post("/audio")
async def analyze_audio_endpoint(
    file: UploadFile = File(...),
    saliency: bool = Query(True, description="Return the saliency_map image (slower)"),
    details: bool = Query(True, description="Include the 'details' block"),
):
    cfg = get_config()
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTS:
        raise HTTPException(400, f"Unsupported file type '{suffix}'. Allowed: {sorted(ALLOWED_EXTS)}")

    max_bytes = cfg.max_upload_mb * 1024 * 1024
    tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    try:
        size = 0
        while chunk := await file.read(1 << 20):
            size += len(chunk)
            if size > max_bytes:
                raise HTTPException(413, f"File larger than {cfg.max_upload_mb} MB.")
            tmp.write(chunk)
        tmp.close()

        # Model inference is blocking; run it off the event loop.
        result = await run_in_threadpool(analyze_audio, tmp.name, cfg, saliency, details)
        if details:
            result["details"]["filename"] = file.filename
        return result

    except HTTPException:
        raise
    except AudioPreprocessError as exc:
        raise HTTPException(400, str(exc))
    except FileNotFoundError as exc:      # model weights missing
        raise HTTPException(503, str(exc))
    except Exception as exc:
        raise HTTPException(500, f"Audio analysis failed: {exc}")
    finally:
        tmp.close()
        if os.path.exists(tmp.name):
            os.remove(tmp.name)


@router.get("/audio/health")
async def audio_health():
    cfg = get_config()
    return {
        "model_loaded": model_lib.is_loaded(),
        "model_version": cfg.model_version,
        "calibrated": cfg.calibrated,
        "weights_present": Path(cfg.xlsr_path).exists() and Path(cfg.checkpoint_path).exists(),
    }