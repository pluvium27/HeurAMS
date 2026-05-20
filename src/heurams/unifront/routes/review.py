"""复习 WebSocket 路由"""

import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from heurams.services.logger import get_logger

from ..dependencies import get_repo
from ..session import Session, SessionError

logger = get_logger(__name__)
router = APIRouter()

# 活跃会话存储 {repo_name: Session}
_active_sessions: dict[str, Session] = {}


@router.websocket("/api/review/{package}")
async def review_websocket(ws: WebSocket, package: str):
    """复习会话 WebSocket 端点

    消息协议 (JSON):
    客户端 -> 服务端:
        {"action": "start", "scheduled_num": 10}
        {"action": "rate", "rating": 4}

    服务端 -> 客户端:
        {"type": "puzzle", "data": {...}}
        {"type": "progress", "data": {"phase": "...", "current": 1, "total": 10}}
        {"type": "finished", "data": {"repo_name": "...", "total_atoms": 10}}
        {"type": "error", "message": "..."}
    """
    await ws.accept()
    logger.debug("WebSocket 连接: package=%s", package)

    session: Session | None = None

    try:
        while True:
            raw = await ws.receive_text()
            msg = json.loads(raw)
            action = msg.get("action")

            if action == "start":
                if session is not None:
                    await ws.send_json({"type": "error", "message": "会话已开始"})
                    continue

                repo = get_repo(package)
                if repo is None:
                    await ws.send_json({
                        "type": "error",
                        "message": f"仓库 '{package}' 未找到",
                    })
                    continue

                try:
                    session = Session(repo)
                    scheduled_num = msg.get("scheduled_num", -1)
                    session.start(scheduled_num)
                    _active_sessions[session.id] = session
                except SessionError as e:
                    await ws.send_json({"type": "error", "message": str(e)})
                    continue

                # 发送初始进度和第一个谜题
                await ws.send_json({
                    "type": "progress",
                    "data": session.progress,
                })
                puzzle = session.get_current_puzzle()
                if puzzle:
                    await ws.send_json({"type": "puzzle", "data": puzzle})
                else:
                    await ws.send_json({
                        "type": "finished",
                        "data": {"repo_name": package, "total_atoms": 0},
                    })

            elif action == "rate":
                if session is None or session.finished:
                    await ws.send_json({
                        "type": "error",
                        "message": "没有活跃的复习会话",
                    })
                    continue

                rating = msg.get("rating", 3)
                continuing = session.rate(rating)

                if not continuing:
                    # 复习完成
                    await ws.send_json({
                        "type": "finished",
                        "data": {
                            "repo_name": package,
                            "total_atoms": session.repo.data_length,
                        },
                    })
                else:
                    await ws.send_json({
                        "type": "progress",
                        "data": session.progress,
                    })
                    puzzle = session.get_current_puzzle()
                    if puzzle:
                        await ws.send_json({"type": "puzzle", "data": puzzle})

            else:
                await ws.send_json({
                    "type": "error",
                    "message": f"未知动作: {action}",
                })

    except WebSocketDisconnect:
        logger.debug("WebSocket 断开: package=%s", package)
    except Exception as e:
        logger.error("WebSocket 错误: %s", e)
    finally:
        if session:
            session.cleanup()
            _active_sessions.pop(session.id, None)
