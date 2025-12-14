import io
import base64
import sys
import os
from unittest.mock import AsyncMock, patch, MagicMock
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from fastapi import status
from httpx import AsyncClient, ASGITransport
import asyncio

from main import app
import routes.detect_routes as detect_routes
from schemas.detect_schemas import DetectionSchema

# marking with package to use same event_loop() for all tests in package
pytestmark = pytest.mark.asyncio(loop_scope="package")


@pytest.fixture(autouse=True)
def mock_inference_manager(monkeypatch):
    # Mock inference_manager methods if used in routes
    try:
        mock = MagicMock()
        mock.annotate_image_and_save.return_value = "/tmp/fake_annotated.png"
        mock.get_detections.return_value = (
            [
                {"class": "helmet", "confidence": 0.99, "bbox": [1, 2, 3, 4]},
                {"class": "helmet", "confidence": 0.98, "bbox": [5, 6, 7, 8]},
            ],
            1, 2
        )
        monkeypatch.setattr(detect_routes, "inference_manager", mock)
    except ImportError:
        pass
    # Patch aiofiles and os if neededs
    class FakeAioFile:
        def __init__(self, *a, **kw): pass
        async def __aenter__(self): return self
        async def __aexit__(self, *a): pass
        async def write(self, data): pass
        async def read(self): return b"fakeimage"
    monkeypatch.setattr("aiofiles.open", lambda *a, **kw: FakeAioFile())
    monkeypatch.setattr("os.remove", lambda *a, **kw: None)
    monkeypatch.setattr("os.path.exists", lambda *a, **kw: True)
    
    # Pathch Canvas to avoid generating actual PDF files
    class FakeCanvas:
        def __init__(self, *a, **kw): pass
        def drawImage(self, *a, **kw): pass
        def showPage(self): pass
        def setFont(self, *a, **kw): pass
        def drawString(self, *a, **kw): pass
        def save(self): pass
    monkeypatch.setattr("reportlab.pdfgen.canvas.Canvas", FakeCanvas)

    # Patch ImageReader to avoid processing the fake image
    class FakeImageReader:
        def __init__(self, *a, **kw): pass
    monkeypatch.setattr("pdf_report_generator.ImageReader", FakeImageReader)


async def test_all_routes():
    async with AsyncClient(transport=ASGITransport(app), base_url="http://127.0.0.1") as client:
        # Prepare a fake image file
        file_content = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+X2ZkAAAAASUVORK5CYII="
        )
        files = {"file": ("test.png", io.BytesIO(file_content), "image/png")}
        
        wrong_files = {"file": ("test.txt", io.BytesIO(b"notanimage"), "text/plain")}
        
        
        response_1 = await client.post('/api/v1/detect', files=files)
        response_2 = await client.post('/api/v1/report', json={
                                                    "image_id": "feaeb09a-78c9-401c-a8dc-f1de1c3e2e84_test_img_2.jpeg",
                                                    "timestamp": "2025-12-14T08:22:27.412566",
                                                    "detections": [
                                                        {
                                                        "class": "helmet",
                                                        "confidence": 0.89,
                                                        "bbox": [
                                                            197,
                                                            41,
                                                            260,
                                                            112
                                                        ]
                                                        },
                                                        {
                                                        "class": "helmet",
                                                        "confidence": 0.87,
                                                        "bbox": [
                                                            125,
                                                            46,
                                                            195,
                                                            133
                                                        ]
                                                        }
                                                    ],
                                                    "summary": {
                                                        "helmet_count": 2,
                                                        "no_helmet_count": 0
                                                    },
                                                    "annotated_image": "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAIBAQEBAQIBAQECAgICAgQDAgIC"})
        response_3 = await client.post('/api/v1/detect', files=wrong_files)
        response_4 = await client.post('/api/v1/report', json={})

        assert response_1.status_code == status.HTTP_201_CREATED
        assert response_2.status_code == status.HTTP_201_CREATED
        assert response_3.status_code == status.HTTP_400_BAD_REQUEST
        assert response_4.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT