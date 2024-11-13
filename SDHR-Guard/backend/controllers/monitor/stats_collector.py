from typing import Dict, List, Any
import asyncio
import time
from dataclasses import dataclass
from datetime import datetime

@dataclass
class FlowStats:
    """流表统计数据结构"""
    packet_count: int
    byte_count: int
    duration_sec: int
    last_updated: datetime

@dataclass
class ControllerStats:
    """控制器统计数据结构"""
    flow_count: int
    packet_count: int
    byte_count: int
    response_time: float
    error_count: int
    last_updated: datetime

class StatsCollector:
    """统计信息收集器"""
    
    def __init__(self, controller):
        self.controller = controller
        self.flow_stats: Dict[str, FlowStats] = {}
        self.controller_stats = ControllerStats(
            flow_count=0,
            packet_count=0,
            byte_count=0,
            response_time=0.0,
            error_count=0,
            last_updated=datetime.now()
        )
        self._running = False
    
    async def start_collecting(self, interval: int = 5):
        """开始收集统计信息"""
        self._running = True
        while self._running:
            try:
                await self._collect_stats()
                await asyncio.sleep(interval)
            except Exception as e:
                self.controller.logger.error(f"Error collecting stats: {str(e)}")
                self.controller_stats.error_count += 1
    
    async def stop_collecting(self):
        """停止收集统计信息"""
        self._running = False
    
    async def _collect_stats(self):
        """收集统计信息"""
        start_time = time.time()
        
        try:
            # 获取流表统计
            flows = await self.controller.get_flows()
            self.controller_stats.flow_count = len(flows)
            
            # 获取交换机统计
            switch_stats = await self.controller.get_switch_stats()
            
            # 更新统计信息
            total_packets = 0
            total_bytes = 0
            
            for flow_id, flow_data in flows.items():
                stats = FlowStats(
                    packet_count=flow_data.get('packet_count', 0),
                    byte_count=flow_data.get('byte_count', 0),
                    duration_sec=flow_data.get('duration_sec', 0),
                    last_updated=datetime.now()
                )
                self.flow_stats[flow_id] = stats
                total_packets += stats.packet_count
                total_bytes += stats.byte_count
            
            # 更新控制器统计
            self.controller_stats.packet_count = total_packets
            self.controller_stats.byte_count = total_bytes
            self.controller_stats.response_time = time.time() - start_time
            self.controller_stats.last_updated = datetime.now()
            
        except Exception as e:
            self.controller.logger.error(f"Error in stats collection: {str(e)}")
            self.controller_stats.error_count += 1
    
    def get_flow_stats(self, flow_id: str = None) -> Dict[str, Any]:
        """获取流表统计信息"""
        if flow_id:
            stats = self.flow_stats.get(flow_id)
            if stats:
                return {
                    "packet_count": stats.packet_count,
                    "byte_count": stats.byte_count,
                    "duration_sec": stats.duration_sec,
                    "last_updated": stats.last_updated.isoformat()
                }
            return {}
        
        return {
            flow_id: {
                "packet_count": stats.packet_count,
                "byte_count": stats.byte_count,
                "duration_sec": stats.duration_sec,
                "last_updated": stats.last_updated.isoformat()
            }
            for flow_id, stats in self.flow_stats.items()
        }
    
    def get_controller_stats(self) -> Dict[str, Any]:
        """获取控制器统计信息"""
        return {
            "flow_count": self.controller_stats.flow_count,
            "packet_count": self.controller_stats.packet_count,
            "byte_count": self.controller_stats.byte_count,
            "response_time": self.controller_stats.response_time,
            "error_count": self.controller_stats.error_count,
            "last_updated": self.controller_stats.last_updated.isoformat()
        } 