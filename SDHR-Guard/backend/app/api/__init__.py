from fastapi import APIRouter
from .controllers import router as controllers_router
from .monitor import router as monitor_router

router = APIRouter()

# 注册控制器路由
router.include_router(
    controllers_router, 
    prefix="/controllers", 
    tags=["controllers"]
)

# 注册监控路由
router.include_router(
    monitor_router,
    prefix="/monitor",
    tags=["monitor"]
) 