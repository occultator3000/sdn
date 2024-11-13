from typing import Optional, Dict, Any
from datetime import datetime

class DHRBaseException(Exception):
    """DHR系统基础异常类"""
    
    def __init__(self, message: str, error_code: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }

class ControllerException(DHRBaseException):
    """控制器相关异常"""
    pass

class FlowException(DHRBaseException):
    """流表相关异常"""
    pass

class SchedulerException(DHRBaseException):
    """调度器相关异常"""
    pass

class SwitchException(DHRBaseException):
    """切换相关异常"""
    pass

class SyncException(DHRBaseException):
    """同步相关异常"""
    pass

class MonitorException(DHRBaseException):
    """监控相关异常"""
    pass 