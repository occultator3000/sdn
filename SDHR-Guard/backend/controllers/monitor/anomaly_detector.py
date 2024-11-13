from typing import Dict, List, Any
import numpy as np
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass

@dataclass
class AnomalyThreshold:
    """异常阈值配置"""
    flow_change_rate: float = 0.3      # 流表变化率阈值
    packet_rate_change: float = 0.5    # 数据包率变化阈值
    response_time_max: float = 1.0     # 最大响应时间
    error_rate_max: float = 0.1        # 最大错误率
    sync_delay_max: float = 5.0        # 最大同步延迟

class AnomalyDetector:
    """异常检测器"""
    
    def __init__(self, controller, thresholds: AnomalyThreshold = None):
        self.controller = controller
        self.logger = logging.getLogger(f"anomaly_detector.{controller.controller_id}")
        self.thresholds = thresholds or AnomalyThreshold()
        
        # 历史数据存储
        self.history = {
            'flow_counts': [],
            'packet_rates': [],
            'response_times': [],
            'error_counts': [],
            'timestamps': []
        }
        self.window_size = 10  # 历史窗口大小
        
    async def detect_anomalies(self) -> Dict[str, Any]:
        """检测异常"""
        try:
            # 获取当前指标
            current_metrics = await self._get_current_metrics()
            
            # 更新历史数据
            self._update_history(current_metrics)
            
            # 执行异常检测
            anomalies = {
                'flow_anomaly': self._detect_flow_anomaly(),
                'performance_anomaly': self._detect_performance_anomaly(),
                'error_anomaly': self._detect_error_anomaly(),
                'sync_anomaly': self._detect_sync_anomaly(),
                'timestamp': datetime.now().isoformat()
            }
            
            # 记录检测到的异常
            if any(anomalies.values()):
                self.logger.warning(
                    f"Detected anomalies in controller {self.controller.controller_id}: {anomalies}"
                )
            
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Error in anomaly detection: {str(e)}")
            return {}
    
    async def _get_current_metrics(self) -> Dict[str, float]:
        """获取当前性能指标"""
        stats = await self.controller.get_metrics()
        return {
            'flow_count': stats['flow_count'],
            'packet_rate': stats['packet_count'] / stats.get('duration_sec', 1),
            'response_time': stats['response_time'],
            'error_count': stats['error_count']
        }
    
    def _update_history(self, metrics: Dict[str, float]):
        """更新历史数据"""
        for key, value in metrics.items():
            history_key = f"{key}s"
            if len(self.history[history_key]) >= self.window_size:
                self.history[history_key].pop(0)
            self.history[history_key].append(value)
        
        # 更新时间戳
        if len(self.history['timestamps']) >= self.window_size:
            self.history['timestamps'].pop(0)
        self.history['timestamps'].append(datetime.now())
    
    def _detect_flow_anomaly(self) -> bool:
        """检测流表异常"""
        if len(self.history['flow_counts']) < 2:
            return False
            
        flow_changes = np.diff(self.history['flow_counts']) / np.array(self.history['flow_counts'][:-1])
        return any(abs(change) > self.thresholds.flow_change_rate for change in flow_changes)
    
    def _detect_performance_anomaly(self) -> bool:
        """检测性能异常"""
        if not self.history['response_times']:
            return False
            
        # 检查响应时间
        current_response_time = self.history['response_times'][-1]
        if current_response_time > self.thresholds.response_time_max:
            return True
            
        # 检查数据包率变化
        if len(self.history['packet_rates']) > 1:
            packet_rate_change = (
                self.history['packet_rates'][-1] - self.history['packet_rates'][-2]
            ) / self.history['packet_rates'][-2]
            if abs(packet_rate_change) > self.thresholds.packet_rate_change:
                return True
                
        return False
    
    def _detect_error_anomaly(self) -> bool:
        """检测错误率异常"""
        if not self.history['error_counts']:
            return False
            
        total_operations = len(self.history['timestamps'])
        error_rate = self.history['error_counts'][-1] / total_operations
        return error_rate > self.thresholds.error_rate_max
    
    def _detect_sync_anomaly(self) -> bool:
        """检测同步异常"""
        if not self.history['timestamps']:
            return False
            
        last_sync = self.controller.flow_manager.last_sync
        if not last_sync:
            return True
            
        sync_delay = (datetime.now() - last_sync).total_seconds()
        return sync_delay > self.thresholds.sync_delay_max
    
    async def get_health_score(self) -> float:
        """计算控制器健康分数"""
        try:
            anomalies = await self.detect_anomalies()
            # 根据不同类型的异常计算健康分数
            weights = {
                'flow_anomaly': 0.3,
                'performance_anomaly': 0.3,
                'error_anomaly': 0.2,
                'sync_anomaly': 0.2
            }
            
            score = 1.0
            for anomaly_type, weight in weights.items():
                if anomalies.get(anomaly_type, False):
                    score -= weight
                    
            return max(0.0, score)
            
        except Exception as e:
            self.logger.error(f"Error calculating health score: {str(e)}")
            return 0.0 