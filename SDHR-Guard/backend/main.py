from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings
from app.api import controllers, topology, monitor
from app.core.controller import ControllerManager
from app.core.topology import TopologyManager
import logging
from app.api import router as api_router

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SDN DHR Defense System",
    description="SDN控制器异构冗余防御系统API",
    version="1.0.0",
    debug=settings.DEBUG
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化管理器
controller_manager = ControllerManager()
topology_manager = TopologyManager()

# API路由
@app.get("/")
async def root():
    return {"message": "SDN DHR Defense System API"}

# 控制器相关API
@app.get("/api/controllers")
async def get_controllers():
    """获取所有控制器状态"""
    return controller_manager.get_all_status()

@app.post("/api/controllers/{controller_id}/start")
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

@app.post("/api/controllers/{controller_id}/stop")
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

# 添加健康检查API
@app.get("/api/controllers/{controller_id}/health")
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

# 拓扑相关API
@app.get("/api/topology")
async def get_topology():
    """获取当前网络拓扑"""
    try:
        return topology_manager.get_current_topology()
    except Exception as e:
        logger.error(f"获取拓扑失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取拓扑失败")

@app.get("/api/topology/stats")
async def get_topology_stats():
    """获取拓扑统计信息"""
    try:
        return topology_manager.get_statistics()
    except Exception as e:
        logger.error(f"获取统计信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取统计信息失败")

# 注册路由
app.include_router(api_router, prefix="/api")

# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化操作"""
    logger.info("正在初始化SDN DHR Defense System...")
    try:
        # 验证控制器路径
        await controller_manager.validate_paths()
        # 初始化拓扑管理器
        await topology_manager.initialize()
        logger.info("系统初始化完成")
    except Exception as e:
        logger.error(f"系统初始化失败: {str(e)}")
        raise

# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的清理操作"""
    logger.info("正在关闭SDN DHR Defense System...")
    try:
        # 停止所有控制器
        for controller_id in controller_manager.controllers:
            await controller_manager.stop_controller(controller_id)
        # 清理拓扑
        await topology_manager.cleanup()
        logger.info("系统已安全关闭")
    except Exception as e:
        logger.error(f"系统关闭时发生错误: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    ) 