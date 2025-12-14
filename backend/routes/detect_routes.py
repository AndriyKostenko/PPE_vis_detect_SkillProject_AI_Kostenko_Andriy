from uuid import uuid4
import os
import base64

from fastapi import APIRouter, UploadFile, File, HTTPException, status
import aiofiles

from schemas.detect_schemas import ImageUploadSchema, DetectionResponseSchema
from inference import inference_manager
from settings import settings

detect_router = APIRouter()


# TODO: create an ImageService class to handle image processing logic
# TODO: create a custom exceptions for clearbetter error handling
@detect_router.post("/detect",
                    status_code=status.HTTP_201_CREATED,
                    response_model=DetectionResponseSchema,
                    summary="Detect Personal Protective Equipment (PPE) in an uploaded image",
                    description="This endpoint accepts an image file upload and performs PPE detection on the image. Supported image formats are JPEG, PNG, and WEBP with a maximum size of 5MB.")
async def detect_ppe(file: UploadFile = File(...)):
    file_path = None
    annotated_image_path = None
    try:
        
        content = await file.read()
        
        #validating the image file
        ImageUploadSchema(
            filename=file.filename,
            content_type=file.content_type,
            size=len(content)
        )
        
        unique_filename = f"{uuid4()}_{file.filename}"
        file_path = os.path.join(settings.IMAGE_UPLOAD_DIR, unique_filename)
        
        async with aiofiles.open(file_path, 'wb') as out_file:
            await out_file.write(content)
        
        annotated_image_path = inference_manager.annotate_image_and_save(image_path=file_path)
        detections = inference_manager.get_detections(image_path=file_path)
        
        # Reading an annotated image and encoding it to base64
        async with aiofiles.open(annotated_image_path, 'rb') as annotated_file:
            annotated_content = await annotated_file.read()
        
        encoded_image = base64.b64encode(annotated_content).decode('utf-8')
        
        # Clean up the uploaded file after processing
        os.remove(file_path)
        os.remove(annotated_image_path)
        
        return DetectionResponseSchema(
            detections=detections,
            annotated_image=f"{encoded_image}"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while processing the file: {str(e)}")
    finally:
        # Clean up files in case of exceptions
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        if annotated_image_path and os.path.exists(annotated_image_path):
            os.remove(annotated_image_path)