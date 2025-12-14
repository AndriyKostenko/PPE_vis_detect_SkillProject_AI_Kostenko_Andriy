# The PPE Vision Detection project by Andriy Kostenko.

This is my PPE Vision Detection project based on specific technical details.
That project solves the problem of identification on violations about the proper wearing PPE (in our case just Helmets).
The flow of the project is simple: load an image -> wait for image object detection -> get an annotated image with generated pdf report. 


## The Tech. Stack

- Frontend: Next.js (JavaScript)
- Backend: FastApi (Python)
- Base Detection Model: YOLO11 (Ultralytics)
- Fine-tuned Model: yolo11m (fine-tuned with setup: 60 epochs,
                                                    16 batch size,
                                                    5k annotated images for training, etc.)
- PDF Generator: ReportLab
- Containerization: Docker


## To start the project you have to:

1. Install the Docker for your specific system: https://www.docker.com/get-started/
2. `git clone https://github.com/AndriyKostenko/PPE_vis_detect_SkillProject_AI_Kostenko_Andriy.git` - cloning the project to your machine
3. `docker compose up --build` - build the project using Docker
4. After building, you will get access to frontend via: http://localhost:3000 and backend API endpoints via: http://0.0.0.0:8000/docs
6. To run the tests you have to go inside the Docker "backend" container: `docker exec -it backend /bin/bash`
   After you appear inside the container you can run: `pytest tests/`


[Screencast from 2025-12-14 15-33-43.webm](https://github.com/user-attachments/assets/63d920b6-ad9a-4ae3-9856-e8311bf5fddd)

