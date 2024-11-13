from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime
import logging

class BaseSyncStrategy(ABC):
    """同步策略基类"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"sync_strategy.{self.__class__.__name__}")
    
    @abstractmethod
    async def should_sync(self, controller_id: str, last_sync: datetime,
                         current_config: Dict[str, Any],
                         controller_config: Dict[str, Any]) -> bool:
        """判断是否需要同步"""
        pass
    
    @abstractmethod
    async def get_sync_priority(self, controller_id: str) -> float:
        """获取同步优先级"""
        pass


class ImmediateSyncStrategy(BaseSyncStrategy):
    """即时同步策略"""
    
    async def should_sync(self, controller_id: str, last_sync: datetime,
                         current_config: Dict[str, Any],
                         controller_config: Dict[str, Any]) -> bool:
        return current_config != controller_config
    
    async def get_sync_priority(self, controller_id: str) -> float:
        return 1.0


class TimedSyncStrategy(BaseSyncStrategy):
    """定时同步策略"""
    
    def __init__(self, sync_interval: int = 300):
        super().__init__()
        self.sync_interval = sync_interval
    
    async def should_sync(self, controller_id: str, last_sync: datetime,
                         current_config: Dict[str, Any],
                         controller_config: Dict[str, Any]) -> bool:
        if not last_sync:
            return True
            
        time_since_sync = (datetime.now() - last_sync).total_seconds()
        return time_since_sync >= self.sync_interval
    
    async def get_sync_priority(self, controller_id: str) -> float:
        return 0.5


class DifferentialSyncStrategy(BaseSyncStrategy):
    """差异同步策略"""
    
    def __init__(self, diff_threshold: float = 0.1):
        super().__init__()
        self.diff_threshold = diff_threshold
    
    async def should_sync(self, controller_id: str, last_sync: datetime,
                         current_config: Dict[str, Any],
                         controller_config: Dict[str, Any]) -> bool:
        if not controller_config:
            return True
            
        diff_ratio = self._calculate_diff_ratio(current_config, controller_config)
        return diff_ratio > self.diff_threshold
    
    async def get_sync_priority(self, controller_id: str) -> float:
        return 0.8
    
    def _calculate_diff_ratio(self, config1: Dict[str, Any],
                            config2: Dict[str, Any]) -> float:
        """计算配置差异率"""
        try:
            total_keys = set(config1.keys()) | set(config2.keys())
            diff_keys = set(k for k in total_keys
                          if config1.get(k) != config2.get(k))
            return len(diff_keys) / len(total_keys)
        except Exception:
            return 1.0


class AdaptiveSyncStrategy(BaseSyncStrategy):
    """自适应同步策略"""
    
    def __init__(self):
        super().__init__()
        self.controller_metrics = {}
        self.sync_history = {}
    
    async def should_sync(self, controller_id: str, last_sync: datetime,
                         current_config: Dict[str, Any],
                         controller_config: Dict[str, Any]) -> bool:
        # 基于控制器状态和历史同步情况决定是否同步
        metrics = self.controller_metrics.get(controller_id, {})
        
        # 如果控制器负载高，减少同步频率
        if metrics.get('load', 0) > 0.8:
            return False
            
        # 检查配置差异
        if current_config != controller_config:
            # 检查同步历史
            history = self.sync_history.get(controller_id, [])
            if len(history) >= 3:
                # 如果最近同步频繁失败，降低同步频率
                recent_failures = sum(1 for result in history[-3:] if not result)
                if recent_failures >= 2:
                    return False
            return True
            
        return False
    
    async def get_sync_priority(self, controller_id: str) -> float:
        metrics = self.controller_metrics.get(controller_id, {})
        
        # 基于控制器状态计算优先级
        base_priority = 0.5
        
        # 负载因子
        load_factor = 1 - (metrics.get('load', 0) * 0.5)
        
        # 健康度因子
        health_factor = metrics.get('health_score', 1.0)
        
        # 错误率因子
        error_rate = metrics.get('error_rate', 0)
        error_factor = 1 - (error_rate * 0.3)
        
        return base_priority * load_factor * health_factor * error_factor
    
    def update_metrics(self, controller_id: str, metrics: Dict[str, Any]):
        """更新控制器指标"""
        self.controller_metrics[controller_id] = metrics
    
    def record_sync_result(self, controller_id: str, success: bool):
        """记录同步结果"""
        if controller_id not in self.sync_history:
            self.sync_history[controller_id] = []
            
        history = self.sync_history[controller_id]
        history.append(success)
        
        # 保持历史记录在合理范围内
        if len(history) > 10:
            history.pop(0) 