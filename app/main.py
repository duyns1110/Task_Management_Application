from fastapi import FastAPI
from .routers import auth, tasks
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Task Management API")

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:3000",  # Frontend URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(tasks.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Task Management API"}
