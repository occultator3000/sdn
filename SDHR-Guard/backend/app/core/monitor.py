import asyncio
import logging
from typing import Dict, List
from datetime import datetime
from mininet.net import Mininet

logger = logging.getLogger(__name__)

class FlowMonitor:
    def __init__(self):
        self.flow_stats: Dict[str, List] = {
            'timestamps': [],
            'bytes': [],
            'packets': [],
            'flows': []
        }
        self.max_data_points = 100
        
    async def collect_stats(self, switch_id: str):
        """收集指定交换机的流量统计"""
        try:
            net = Mininet.get()
            switch = net.getNodeByName(switch_id)
            
            if not switch:
                raise ValueError(f"交换机 {switch_id} 不存在")
            
            # 获取端口统计
            port_stats = await self._get_port_stats(switch)
            # 获取流表统计
            flow_stats = await self._get_flow_stats(switch)
            
            # 更新统计数据
            timestamp = datetime.now().strftime('%H:%M:%S')
            self.flow_stats['timestamps'].append(timestamp)
            self.flow_stats['bytes'].append(port_stats['total_bytes'])
            self.flow_stats['packets'].append(port_stats['total_packets'])
            self.flow_stats['flows'].append(len(flow_stats))
            
            # 保持数据点数量限制
            if len(self.flow_stats['timestamps']) > self.max_data_points:
                for key in self.flow_stats:
                    self.flow_stats[key] = self.flow_stats[key][-self.max_data_points:]
            
            return {
                'bytes': port_stats['total_bytes'],
                'packets': port_stats['total_packets'],
                'flows': len(flow_stats)
            }
        except Exception as e:
            logger.error(f"获取流量统计失败: {str(e)}")
            raise
            
    async def _get_port_stats(self, switch):
        """获取端口统计信息"""
        try:
            stats = {'total_bytes': 0, 'total_packets': 0}
            
            # 使用dpctl获取端口统计
            output = switch.dpctl('dump-ports')
            lines = output.split('\n')
            
            for line in lines:
                if 'rx bytes=' in line:
                    stats['total_bytes'] += int(line.split('bytes=')[1].split()[0])
                if 'rx pkts=' in line:
                    stats['total_packets'] += int(line.split('pkts=')[1].split()[0])
                    
            return stats
        except Exception as e:
            logger.error(f"获取端口统计失败: {str(e)}")
            return {'total_bytes': 0, 'total_packets': 0}
            
    async def _get_flow_stats(self, switch):
        """获取流表统计信息"""
        try:
            # 使用dpctl获取流表
            output = switch.dpctl('dump-flows')
            return output.split('\n')[1:]  # 去掉头部
        except Exception as e:
            logger.error(f"获取流表统计失败: {str(e)}")
            return []
        
    def get_flow_history(self):
        """获取历史流量数据"""
        return self.flow_stats