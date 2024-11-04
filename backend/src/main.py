from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routes import routes


def create_app():
    app = FastAPI(title="Transport Problem")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(routes)

    return app
