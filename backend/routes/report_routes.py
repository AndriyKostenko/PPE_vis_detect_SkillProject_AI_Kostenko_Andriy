from fastapi import APIRouter, UploadFile, File, HTTPException


report_router = APIRouter()


@report_router.post("/report")
def generate_the_report():  
    return {"message": "Report generation endpoint"}