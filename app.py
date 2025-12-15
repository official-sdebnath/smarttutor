from fastapi import FastAPI
from backend.routers import ingest, qa
import uvicorn

app = FastAPI(title="SmartTutor API")

app.include_router(ingest.router)
app.include_router(qa.router)

@app.get("/")
def root():
    return {"message": "SmartTutor backend is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
    