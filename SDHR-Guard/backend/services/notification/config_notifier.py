import asyncio
import logging
from typing import Dict, Any, Set, Callable
from datetime import datetime
from ...core.exceptions import NotificationError

class ConfigNotifier:
    """配置变更通知器"""
    
    def __init__(self):
        self.logger = logging.getLogger("config_notifier")
        self.subscribers: Dict[str, Set[Callable]] = {
            'dhr': set(),
            'alert': set(),
            'system': set()
        }
        self.notification_queue = asyncio.Queue()
        self._running = False
    
    async def start(self):
        """启动通知服务"""
        self._running = True
        asyncio.create_task(self._process_notifications())
        self.logger.info("Config notifier started")
    
    async def stop(self):
        """停止通知服务"""
        self._running = False
        self.logger.info("Config notifier stopped")
    
    def subscribe(self, module: str, callback: Callable):
        """订阅配置变更通知"""
        if module not in self.subscribers:
            self.subscribers[module] = set()
        self.subscribers[module].add(callback)
        self.logger.info(f"Subscribed to {module} config changes")
    
    def unsubscribe(self, module: str, callback: Callable):
        """取消订阅"""
        if module in self.subscribers:
            self.subscribers[module].discard(callback)
            self.logger.info(f"Unsubscribed from {module} config changes")
    
    async def notify_change(self, module: str, config: Dict[str, Any]):
        """通知配置变更"""
        try:
            notification = {
                'module': module,
                'config': config,
                'timestamp': datetime.now().isoformat()
            }
            await self.notification_queue.put(notification)
            
        except Exception as e:
            self.logger.error(f"Failed to notify config change: {str(e)}")
            raise NotificationError(f"Failed to notify config change: {str(e)}")
    
    async def _process_notifications(self):
        """处理通知队列"""
        while self._running:
            try:
                notification = await self.notification_queue.get()
                await self._dispatch_notification(notification)
                self.notification_queue.task_done()
                
            except Exception as e:
                self.logger.error(f"Error processing notification: {str(e)}")
                await asyncio.sleep(1)
    
    async def _dispatch_notification(self, notification: Dict[str, Any]):
        """分发通知"""
        module = notification['module']
        config = notification['config']
        
        if module not in self.subscribers:
            return
            
        for callback in self.subscribers[module]:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(config)
                else:
                    callback(config)
                    
            except Exception as e:
                self.logger.error(
                    f"Error in notification callback for {module}: {str(e)}"
                )
    
    def get_subscriber_stats(self) -> Dict[str, Any]:
        """获取订阅者统计信息"""
        return {
            module: len(subscribers)
            for module, subscribers in self.subscribers.items()
        } 