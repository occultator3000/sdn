from fastapi import APIRouter, HTTPException
from app.core.monitor import FlowMonitor

router = APIRouter()
flow_monitor = FlowMonitor()

@router.get("/stats/{switch_id}")
async def get_flow_stats(switch_id: str):
    """获取指定交换机的流量统计"""
    try:
        stats = await flow_monitor.collect_stats(switch_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/history")
async def get_flow_history():
    """获取流量历史数据"""
    return flow_monitor.get_flow_history() 