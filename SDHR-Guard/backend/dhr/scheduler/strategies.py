from typing import Optional, List
from .base import BaseScheduler

class RoundRobinScheduler(BaseScheduler):
    """轮询调度策略"""
    
    def __init__(self):
        super().__init__()
        self.current_index = 0
    
    async def select_controller(self) -> Optional[str]:
        if not self.active_controllers:
            return None
            
        # 获取活跃的控制器列表
        controllers = list(self.active_controllers.keys())
        
        # 选择下一个控制器
        self.current_index = (self.current_index + 1) % len(controllers)
        return controllers[self.current_index]


class HealthAwareScheduler(BaseScheduler):
    """基于健康状况的调度策略"""
    
    async def select_controller(self) -> Optional[str]:
        if not self.active_controllers:
            return None
            
        # 选择健康分数最高的控制器
        return max(self.active_controllers.items(), key=lambda x: x[1])[0]


class DiversityAwareScheduler(BaseScheduler):
    """考虑异构性的调度策略"""
    
    def __init__(self):
        super().__init__()
        self.type_history: List[str] = []  # 控制器类型使用历史
        self.history_limit = 3  # 历史记录限制
    
    async def select_controller(self) -> Optional[str]:
        if not self.active_controllers:
            return None
            
        # 获取最近未使用的控制器类型
        used_types = set(self.type_history)
        available_types = set(self.controller_types.values())
        preferred_types = available_types - used_types
        
        if not preferred_types:
            preferred_types = available_types
        
        # 在首选类型中选择健康分数最高的控制器
        best_controller = None
        best_score = -1
        
        for controller_id, score in self.active_controllers.items():
            if (self.controller_types[controller_id] in preferred_types and 
                score > best_score):
                best_controller = controller_id
                best_score = score
        
        if best_controller:
            # 更新类型历史
            self.type_history.append(self.controller_types[best_controller])
            if len(self.type_history) > self.history_limit:
                self.type_history.pop(0)
                
        return best_controller 