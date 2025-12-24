from typing import Any
import shutil
import os
import uuid
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from app import models
from app.api import deps

router = APIRouter()

UPLOAD_DIR = "app/uploads"

@router.post("/upload", response_model=dict)
async def upload_file(
    file: UploadFile = File(...),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Upload a file. Only superusers.
    Returns the URL to the uploaded file.
    """
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    # Generate unique filename
    file_ext = file.filename.split(".")[-1] if "." in file.filename else "png"
    file_name = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, file_name)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not upload file: {e}")

    # Return URL
    # Assuming mounted at /static
    return {"url": f"/static/{file_name}"}
