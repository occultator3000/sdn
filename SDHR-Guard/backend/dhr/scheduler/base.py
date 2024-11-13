from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

class BaseScheduler(ABC):
    """DHR调度器基类"""
    
    def __init__(self):
        self.logger = logging.getLogger("dhr_scheduler")
        self.active_controllers: Dict[str, float] = {}  # 控制器ID -> 健康分数
        self.controller_types: Dict[str, str] = {}      # 控制器ID -> 控制器类型
        self.last_switch: datetime = datetime.now()
        self.min_switch_interval = 5  # 最小切换间隔（秒）
    
    @abstractmethod
    async def select_controller(self) -> Optional[str]:
        """选择最适合的控制器"""
        pass
    
    def add_controller(self, controller_id: str, controller_type: str):
        """添加控制器到调度池"""
        self.controller_types[controller_id] = controller_type
        self.active_controllers[controller_id] = 1.0
        self.logger.info(f"Added controller {controller_id} ({controller_type}) to scheduler")
    
    def remove_controller(self, controller_id: str):
        """从调度池移除控制器"""
        if controller_id in self.active_controllers:
            del self.active_controllers[controller_id]
            del self.controller_types[controller_id]
            self.logger.info(f"Removed controller {controller_id} from scheduler")
    
    async def update_health_scores(self, health_scores: Dict[str, float]):
        """更新控制器健康分数"""
        for controller_id, score in health_scores.items():
            if controller_id in self.active_controllers:
                self.active_controllers[controller_id] = score
    
    def can_switch(self) -> bool:
        """检查是否可以进行控制器切换"""
        time_since_last_switch = (datetime.now() - self.last_switch).total_seconds()
        return time_since_last_switch >= self.min_switch_interval
    
    def get_controller_status(self) -> Dict[str, Any]:
        """获取调度器状态"""
        return {
            "active_controllers": self.active_controllers,
            "controller_types": self.controller_types,
            "last_switch": self.last_switch.isoformat()
        } 