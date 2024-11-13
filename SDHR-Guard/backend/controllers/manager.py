from typing import Dict, List, Any
import asyncio
from .base import BaseController
from .pox.controller import POXController
# 后续会添加RYU和ODL的导入

class ControllerManager:
    """控制器管理器，负责管理所有控制器实例"""
    
    def __init__(self):
        self.controllers: Dict[str, BaseController] = {}
        self.active_controllers: List[str] = []
    
    async def create_controller(self, controller_type: str, config: Dict[str, Any]) -> str:
        """创建新的控制器实例"""
        controller_id = f"{controller_type}_{len(self.controllers)}"
        
        if controller_type.lower() == 'pox':
            controller = POXController(controller_id, config)
        # 后续添加其他控制器类型的处理
        else:
            raise ValueError(f"Unsupported controller type: {controller_type}")
        
        self.controllers[controller_id] = controller
        return controller_id
    
    async def start_controller(self, controller_id: str) -> bool:
        """启动指定的控制器"""
        if controller_id not in self.controllers:
            return False
            
        controller = self.controllers[controller_id]
        if await controller.start():
            self.active_controllers.append(controller_id)
            return True
        return False
    
    async def stop_controller(self, controller_id: str) -> bool:
        """停止指定的控制器"""
        if controller_id not in self.controllers:
            return False
            
        controller = self.controllers[controller_id]
        if await controller.stop():
            self.active_controllers.remove(controller_id)
            return True
        return False
    
    async def get_controller_status(self, controller_id: str) -> Dict[str, Any]:
        """获取控制器状态"""
        if controller_id not in self.controllers:
            return {}
            
        controller = self.controllers[controller_id]
        return {
            "id": controller_id,
            "type": controller.__class__.__name__,
            "status": controller.status,
            "metrics": await controller.get_metrics()
        }
    
    async def get_all_controllers(self) -> List[Dict[str, Any]]:
        """获取所有控制器的状态"""
        return [
            await self.get_controller_status(controller_id)
            for controller_id in self.controllers
        ] 