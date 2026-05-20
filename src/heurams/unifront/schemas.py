"""unifront Pydantic 模型"""

from pydantic import BaseModel


class RepoInfo(BaseModel):
    """仓库信息"""

    package: str
    title: str
    author: str
    desc: str
    source: str
    total: int
    touched: int


class AtomInfo(BaseModel):
    """原子信息"""

    ident: str
    activated: bool
    due: bool
    rept: int
    interval: int
    next_date: int
    last_date: int


class ConfigTree(BaseModel):
    """配置树节点"""

    key: str
    type: str
    value: object = None
    children: list["ConfigTree"] | None = None


class PuzzlePayload(BaseModel):
    """谜题数据载荷"""

    category: str
    alia: str
    atom_ident: str
    puzzle: dict


class ReviewProgress(BaseModel):
    """复习进度"""

    phase: str
    current: int
    total: int


class WSMessage(BaseModel):
    """WebSocket 消息基类"""

    type: str
    data: dict | None = None
    message: str | None = None


class RateAction(BaseModel):
    """评分动作"""

    rating: int  # 0-5
