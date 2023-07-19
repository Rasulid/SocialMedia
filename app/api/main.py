from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from api.auth.admin_auth import router as admin_auth_router
from api.router.user_router import router as user_router
from api.router.post_router import router as post_router
from api.router.like_and_dislike_router import router as like_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.include_router(user_router)
app.include_router(admin_auth_router)
app.include_router(post_router)
app.include_router(like_router)


app.mount('/media', StaticFiles(directory="media/"), name="media")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
