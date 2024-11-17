from fastapi import APIRouter, HTTPException
from app.core.controller import ControllerManager
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
controller_manager = ControllerManager()

@router.get("/")
async def get_controllers():
    """获取所有控制器状态"""
    return controller_manager.get_all_status()

@router.post("/{controller_id}/start")
async def start_controller(controller_id: str):
    """启动指定控制器"""
    try:
        result = await controller_manager.start_controller(controller_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"启动控制器失败: {str(e)}")
        raise HTTPException(status_code=500, detail="启动控制器失败")

@router.post("/{controller_id}/stop")
async def stop_controller(controller_id: str):
    """停止指定控制器"""
    try:
        result = await controller_manager.stop_controller(controller_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"停止控制器失败: {str(e)}")
        raise HTTPException(status_code=500, detail="停止控制器失败")

@router.get("/{controller_id}/health")
async def check_controller_health(controller_id: str):
    """获取指定控制器的健康状态"""
    try:
        result = await controller_manager.health_check(controller_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        raise HTTPException(status_code=500, detail="健康检查失败")