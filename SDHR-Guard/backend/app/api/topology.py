from fastapi import APIRouter, HTTPException
from app.core.topology import TopologyManager
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
topology_manager = TopologyManager()

@router.get("/")
async def get_topology():
    """获取当前网络拓扑"""
    try:
        return topology_manager.get_current_topology()
    except Exception as e:
        logger.error(f"获取拓扑失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取拓扑失败")

@router.get("/stats")
async def get_topology_stats():
    """获取拓扑统计信息"""
    try:
        return topology_manager.get_statistics()
    except Exception as e:
        logger.error(f"获取统计信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取统计信息失败") 