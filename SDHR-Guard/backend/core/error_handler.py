import logging
import traceback
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
from .exceptions import DHRBaseException

class ErrorHandler:
    """统一错误处理器"""
    
    def __init__(self):
        self.logger = logging.getLogger("error_handler")
        self.error_handlers: Dict[str, Callable] = {}
        self.error_history: List[Dict[str, Any]] = []
        self.max_history = 1000
        
        # 注册默认错误处理器
        self._register_default_handlers()
    
    def register_handler(self, error_type: str, handler: Callable):
        """注册错误处理器"""
        self.error_handlers[error_type] = handler
        self.logger.info(f"Registered handler for {error_type}")
    
    async def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> bool:
        """处理错误"""
        try:
            error_type = (
                error.error_code if isinstance(error, DHRBaseException)
                else error.__class__.__name__
            )
            
            # 记录错误
            self._record_error(error_type, error, context)
            
            # 查找对应的处理器
            handler = self.error_handlers.get(error_type)
            if handler:
                return await handler(error, context)
            
            # 使用默认处理器
            return await self._handle_default(error, context)
            
        except Exception as e:
            self.logger.error(f"Error in error handler: {str(e)}")
            return False
    
    def _record_error(self, error_type: str, error: Exception, context: Optional[Dict[str, Any]]):
        """记录错误信息"""
        error_info = {
            "type": error_type,
            "message": str(error),
            "timestamp": datetime.now().isoformat(),
            "stack_trace": traceback.format_exc(),
            "context": context or {}
        }
        
        self.error_history.append(error_info)
        
        # 维护历史记录大小
        if len(self.error_history) > self.max_history:
            self.error_history = self.error_history[-self.max_history:]
        
        # 记录日志
        self.logger.error(
            f"Error occurred: {error_type}\n"
            f"Message: {str(error)}\n"
            f"Context: {context}\n"
            f"Stack trace: {traceback.format_exc()}"
        )
    
    def _register_default_handlers(self):
        """注册默认错误处理器"""
        self.register_handler(
            "ControllerException",
            self._handle_controller_error
        )
        self.register_handler(
            "ConfigException",
            self._handle_config_error
        )
        self.register_handler(
            "SyncException",
            self._handle_sync_error
        )
    
    async def _handle_controller_error(self, error: Exception, context: Optional[Dict[str, Any]]) -> bool:
        """处理控制器错误"""
        try:
            controller = context.get('controller')
            if not controller:
                return False
            
            # 尝试重启控制器
            await controller.stop()
            success = await controller.start()
            
            if success:
                self.logger.info(f"Successfully recovered controller: {controller.controller_id}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Error handling controller error: {str(e)}")
            return False
    
    async def _handle_config_error(self, error: Exception, context: Optional[Dict[str, Any]]) -> bool:
        """处理配置错误"""
        try:
            # 尝试恢复默认配置
            config_service = context.get('config_service')
            if config_service:
                await config_service.reset_config()
                self.logger.info("Config reset to default")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Error handling config error: {str(e)}")
            return False
    
    async def _handle_sync_error(self, error: Exception, context: Optional[Dict[str, Any]]) -> bool:
        """处理同步错误"""
        try:
            sync_service = context.get('sync_service')
            if not sync_service:
                return False
            
            # 重试同步
            controller_id = context.get('controller_id')
            if controller_id:
                await sync_service.sync_config(controller_id)
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Error handling sync error: {str(e)}")
            return False
    
    async def _handle_default(self, error: Exception, context: Optional[Dict[str, Any]]) -> bool:
        """默认错误处理"""
        self.logger.warning(f"No specific handler for error type: {type(error).__name__}")
        return False
    
    def get_error_stats(self) -> Dict[str, Any]:
        """获取错误统计信息"""
        error_counts = {}
        for error in self.error_history:
            error_type = error['type']
            error_counts[error_type] = error_counts.get(error_type, 0) + 1
            
        return {
            "total_errors": len(self.error_history),
            "error_counts": error_counts,
            "recent_errors": self.error_history[-10:]  # 最近10条错误
        } 