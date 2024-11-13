from typing import Dict, List, Any, Optional
import numpy as np
from datetime import datetime, timedelta
from .base import BaseScheduler
from .strategies import RoundRobinScheduler, HealthAwareScheduler, DiversityAwareScheduler

class AdaptiveScheduler(BaseScheduler):
    """自适应调度器"""
    
    def __init__(self):
        super().__init__()
        # 初始化不同的调度策略
        self.strategies = {
            'round_robin': RoundRobinScheduler(),
            'health_aware': HealthAwareScheduler(),
            'diversity_aware': DiversityAwareScheduler()
        }
        
        # 策略性能记录
        self.strategy_performance = {
            'round_robin': [],
            'health_aware': [],
            'diversity_aware': []
        }
        
        # 当前策略
        self.current_strategy = 'health_aware'
        self.performance_window = 10  # 性能评估窗口
        self.adaptation_interval = 60  # 策略调整间隔（秒）
        self.last_adaptation = datetime.now()
        
        # 系统状态指标
        self.system_metrics = {
            'load_level': 0.0,      # 系统负载水平
            'error_rate': 0.0,      # 错误率
            'diversity_score': 0.0   # 异构性得分
        }
    
    async def select_controller(self) -> Optional[str]:
        """选择控制器"""
        # 更新系统状态
        await self._update_system_metrics()
        
        # 检查是否需要调整策略
        await self._adapt_strategy()
        
        # 使用当前策略选择控制器
        selected = await self.strategies[self.current_strategy].select_controller()
        
        # 记录选择结果的性能
        await self._record_performance(selected)
        
        return selected
    
    async def _update_system_metrics(self):
        """更新系统状态指标"""
        try:
            # 计算系统负载
            load_level = sum(self.active_controllers.values()) / len(self.active_controllers)
            
            # 计算错误率
            error_count = sum(1 for score in self.active_controllers.values() if score < 0.5)
            error_rate = error_count / len(self.active_controllers) if self.active_controllers else 0
            
            # 计算异构性得分
            controller_types = set(self.controller_types.values())
            diversity_score = len(controller_types) / 3  # 3是支持的控制器类型总数
            
            self.system_metrics.update({
                'load_level': load_level,
                'error_rate': error_rate,
                'diversity_score': diversity_score
            })
            
        except Exception as e:
            self.logger.error(f"Error updating system metrics: {str(e)}")
    
    async def _adapt_strategy(self):
        """调整调度策略"""
        now = datetime.now()
        if (now - self.last_adaptation).total_seconds() < self.adaptation_interval:
            return
            
        try:
            # 基于系统状态选择最适合的策略
            if self.system_metrics['error_rate'] > 0.3:
                # 错误率高时使用健康感知策略
                new_strategy = 'health_aware'
            elif self.system_metrics['load_level'] > 0.8:
                # 负载高时使用轮询策略
                new_strategy = 'round_robin'
            elif self.system_metrics['diversity_score'] < 0.6:
                # 异构性不足时使用多样性感知策略
                new_strategy = 'diversity_aware'
            else:
                # 选择性能最好的策略
                new_strategy = self._select_best_performing_strategy()
            
            if new_strategy != self.current_strategy:
                self.logger.info(
                    f"Switching strategy from {self.current_strategy} to {new_strategy}"
                )
                self.current_strategy = new_strategy
                
            self.last_adaptation = now
            
        except Exception as e:
            self.logger.error(f"Error in strategy adaptation: {str(e)}")
    
    def _select_best_performing_strategy(self) -> str:
        """选择性能最好的策略"""
        avg_performance = {}
        for strategy, performance in self.strategy_performance.items():
            if performance:
                avg_performance[strategy] = np.mean(performance[-self.performance_window:])
            else:
                avg_performance[strategy] = 0.0
                
        return max(avg_performance.items(), key=lambda x: x[1])[0]
    
    async def _record_performance(self, selected_controller: Optional[str]):
        """记录策略性能"""
        if not selected_controller:
            performance = 0.0
        else:
            # 基于选择的控制器的健康分数评估性能
            performance = self.active_controllers.get(selected_controller, 0.0)
            
        self.strategy_performance[self.current_strategy].append(performance)
        
        # 保持性能记录在窗口大小内
        if len(self.strategy_performance[self.current_strategy]) > self.performance_window:
            self.strategy_performance[self.current_strategy].pop(0)
    
    def get_strategy_status(self) -> Dict[str, Any]:
        """获取策略状态信息"""
        return {
            'current_strategy': self.current_strategy,
            'system_metrics': self.system_metrics,
            'strategy_performance': {
                strategy: np.mean(perf) if perf else 0.0
                for strategy, perf in self.strategy_performance.items()
            },
            'last_adaptation': self.last_adaptation.isoformat()
        } 