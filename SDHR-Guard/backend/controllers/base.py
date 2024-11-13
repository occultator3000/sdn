from abc import ABC, abstractmethod
from typing import Dict, Any, List
import asyncio
import logging
from .flow_manager import FlowManager, FlowRule
from .monitor.stats_collector import StatsCollector

class BaseController(ABC):
    """控制器基类，定义所有控制器必须实现的接口"""
    
    def __init__(self, controller_id: str, config: Dict[str, Any]):
        self.controller_id = controller_id
        self.config = config
        self.status = "inactive"
        self.logger = logging.getLogger(f"controller.{controller_id}")
        self.metrics = {
            "packet_count": 0,
            "flow_count": 0,
            "latency": 0.0,
            "error_count": 0
        }
        self.flow_manager = FlowManager()
        self.stats_collector = StatsCollector(self)
    
    @abstractmethod
    async def start(self) -> bool:
        """启动控制器"""
        if await self._start_controller():
            # 启动统计收集
            asyncio.create_task(self.stats_collector.start_collecting())
            return True
        return False
    
    @abstractmethod
    async def stop(self) -> bool:
        """停止控制器"""
        await self.stats_collector.stop_collecting()
        return await self._stop_controller()
    
    @abstractmethod
    async def _start_controller(self) -> bool:
        """实际的控制器启动逻辑"""
        pass
    
    @abstractmethod
    async def _stop_controller(self) -> bool:
        """实际的控制器停止逻辑"""
        pass
    
    @abstractmethod
    async def get_flows(self) -> Dict[str, Any]:
        """获取流表信息"""
        pass
    
    @abstractmethod
    async def install_flow(self, flow_rule: Dict[str, Any]) -> bool:
        """安装流表项"""
        pass
    
    @abstractmethod
    async def remove_flow(self, flow_id: str) -> bool:
        """删除流表项"""
        pass
    
    async def get_metrics(self) -> Dict[str, Any]:
        """获取控制器指标"""
        return {
            **await super().get_metrics(),
            **self.stats_collector.get_controller_stats()
        }
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            await self.get_flows()
            return True
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return False 
    
    async def install_flow_rule(self, flow_rule: FlowRule) -> bool:
        """安装流表规则"""
        try:
            # 先在本地管理器中添加
            self.flow_manager.flows[flow_rule.flow_id] = flow_rule
            
            # 转换为控制器特定格式并安装
            success = await self.install_flow(self.flow_manager.to_dict(flow_rule))
            
            if not success:
                # 如果安装失败，从本地管理器中删除
                del self.flow_manager.flows[flow_rule.flow_id]
                
            return success
        except Exception as e:
            self.logger.error(f"Failed to install flow rule: {str(e)}")
            return False
    
    async def remove_flow_rule(self, flow_id: str) -> bool:
        """删除流表规则"""
        try:
            flow_rule = self.flow_manager.get_flow(flow_id)
            if not flow_rule:
                return False
                
            # 先从控制器中删除
            success = await self.remove_flow(flow_id)
            
            if success:
                # 成功后从本地管理器中删除
                self.flow_manager.delete_flow(flow_id)
                
            return success
        except Exception as e:
            self.logger.error(f"Failed to remove flow rule: {str(e)}")
            return False
    
    async def get_all_flows(self) -> List[Dict[str, Any]]:
        """获取所有流表"""
        try:
            flows = await self.get_flows()
            # 更新本地管理器
            for flow in flows:
                if flow["flow_id"] not in self.flow_manager.flows:
                    self.flow_manager.flows[flow["flow_id"]] = \
                        self.flow_manager.from_dict(flow)
            return flows
        except Exception as e:
            self.logger.error(f"Failed to get flows: {str(e)}")
            return [] 