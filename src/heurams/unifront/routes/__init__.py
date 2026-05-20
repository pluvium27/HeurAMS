"""unifront 路由"""

from .repos import router as repos_router
from .config import router as config_router
from .atoms import router as atoms_router
from .review import router as review_router
from .misc import router as misc_router

__all__ = ["repos_router", "config_router", "atoms_router", "review_router", "misc_router"]
