from fastapi import APIRouter, UploadFile, File, HTTPException
from main import settings


detect_router = APIRouter()


@detect_router.post("/detect")
def detect_ppe(file: UploadFile = File(...)):  
    return {"message": "PPE detection endpoint"}

