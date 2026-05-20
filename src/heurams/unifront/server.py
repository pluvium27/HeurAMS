"""unifront FastAPI 应用工厂"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from heurams.services.logger import get_logger
from heurams.services.version import ver
from heurams.context import rootdir

from .routes import repos_router, config_router, atoms_router, review_router, misc_router

logger = get_logger(__name__)


def create_app() -> FastAPI:
    """创建并配置 FastAPI 应用"""
    app = FastAPI(
        title="HeurAMS API",
        version=ver,
        description="HeurAMS 启发式辅助记忆调度器 - unifront API",
    )

    # CORS — 允许本地开发前端
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 静态文件 (Web 前端)
    static_dir = rootdir / "unifront" / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    # 注册路由
    app.include_router(repos_router)
    app.include_router(config_router)
    app.include_router(atoms_router)
    app.include_router(review_router)
    app.include_router(misc_router)

    @app.get("/api")
    def api_root():
        return {
            "service": "HeurAMS",
            "version": ver,
            "endpoints": {
                "repos": "/api/repos",
                "config": "/api/config",
                "atoms": "/api/repos/{package}/atoms",
                "review_ws": "/api/review/{package}",
            },
        }

    @app.get("/api/health")
    def health():
        return {"status": "ok", "version": ver}

    @app.get("/")
    def index():
        from fastapi.responses import RedirectResponse

        return RedirectResponse(url="/static/index.html")

    logger.info("unifront API 应用已创建")
    return app
