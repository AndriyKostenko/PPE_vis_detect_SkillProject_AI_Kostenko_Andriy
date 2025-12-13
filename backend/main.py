import uvicorn 
from fastapi import FastAPI
from settings import settings


app = FastAPI(title="PPE Vision Detection App",
              version="0.0.1")


@app.get("/")
def health_check():
    return {"status": "ok", "message": "PPE Vision Detection Backend is running."}




if __name__ == "__main__":
    uvicorn.run(app, host=settings.APP_HOST, port=settings.APP_PORT)