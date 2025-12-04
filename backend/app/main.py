from fastapi import FastAPI
from .routes import students, courses, ratings
from .database import Base, engine
from . import models
from .seed_data import seed_database

# Seed the database on startup (which also handles table recreation)
seed_database()

app = FastAPI()

app.include_router(students.router)
app.include_router(courses.router)
app.include_router(ratings.router)

@app.get("/")
def root():
    return {"message": "API is running"}
