from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import overview, posts

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(overview.router)
app.include_router(posts.router)
