from fastapi import FastAPI
from .routers import auth, tasks, image_recognition
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(image_recognition.router)

@app.get("/", response_class=HTMLResponse)
async def homepage():
    with open("app/templates/upload_image.html", "r", encoding="utf-8") as f:
        return f.read()
