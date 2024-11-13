import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime
from ...core.exceptions import SyncError
from ..config import ConfigService

class ConfigSynchronizer:
    """配置同步器"""
    
    def __init__(self):
        self.logger = logging.getLogger("config_synchronizer")
        self.config_service = ConfigService()
        self.controllers = {}  # 控制器连接池
        self.sync_interval = 30  # 同步间隔（秒）
        self.last_sync = {}  # 记录每个控制器最后同步时间
        self._running = False
    
    async def start(self):
        """启动同步服务"""
        self._running = True
        asyncio.create_task(self._sync_loop())
        self.logger.info("Config synchronizer started")
    
    async def stop(self):
        """停止同步服务"""
        self._running = False
        self.logger.info("Config synchronizer stopped")
    
    async def register_controller(self, controller_id: str, controller):
        """注册控制器"""
        self.controllers[controller_id] = controller
        self.last_sync[controller_id] = None
        self.logger.info(f"Registered controller: {controller_id}")
    
    async def unregister_controller(self, controller_id: str):
        """注销控制器"""
        if controller_id in self.controllers:
            del self.controllers[controller_id]
            del self.last_sync[controller_id]
            self.logger.info(f"Unregistered controller: {controller_id}")
    
    async def sync_config(self, controller_id: str = None):
        """同步配置到指定或所有控制器"""
        try:
            config = await self.config_service.get_config()
            
            if controller_id:
                # 同步到指定控制器
                await self._sync_to_controller(controller_id, config)
            else:
                # 同步到所有控制器
                await self._sync_to_all_controllers(config)
                
        except Exception as e:
            self.logger.error(f"Config sync failed: {str(e)}")
            raise SyncError(f"Failed to sync config: {str(e)}")
    
    async def _sync_loop(self):
        """同步循环"""
        while self._running:
            try:
                await self.sync_config()
                await asyncio.sleep(self.sync_interval)
            except Exception as e:
                self.logger.error(f"Error in sync loop: {str(e)}")
                await asyncio.sleep(5)  # 错误后短暂等待
    
    async def _sync_to_controller(self, controller_id: str, config: Dict[str, Any]):
        """同步配置到指定控制器"""
        try:
            controller = self.controllers.get(controller_id)
            if not controller:
                raise SyncError(f"Controller not found: {controller_id}")
            
            # 检查配置版本
            if not await self._need_sync(controller_id, config):
                return
            
            # 执行同步
            await controller.update_config(config)
            
            # 更新同步时间
            self.last_sync[controller_id] = datetime.now()
            
            self.logger.info(f"Config synced to controller: {controller_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to sync config to {controller_id}: {str(e)}")
            raise SyncError(f"Sync failed for controller {controller_id}: {str(e)}")
    
    async def _sync_to_all_controllers(self, config: Dict[str, Any]):
        """同步配置到所有控制器"""
        sync_tasks = []
        for controller_id in self.controllers:
            task = self._sync_to_controller(controller_id, config)
            sync_tasks.append(task)
        
        if sync_tasks:
            results = await asyncio.gather(*sync_tasks, return_exceptions=True)
            
            # 检查同步结果
            for controller_id, result in zip(self.controllers.keys(), results):
                if isinstance(result, Exception):
                    self.logger.error(f"Sync failed for {controller_id}: {str(result)}")
    
    async def _need_sync(self, controller_id: str, config: Dict[str, Any]) -> bool:
        """检查是否需要同步"""
        try:
            controller = self.controllers[controller_id]
            
            # 获取控制器当前配置
            current_config = await controller.get_config()
            
            # 检查配置是否相同
            if current_config == config:
                return False
            
            # 检查最后同步时间
            last_sync_time = self.last_sync[controller_id]
            if last_sync_time:
                time_since_sync = (datetime.now() - last_sync_time).total_seconds()
                if time_since_sync < self.sync_interval / 2:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking sync need: {str(e)}")
            return True
    
    def get_sync_status(self) -> Dict[str, Any]:
        """获取同步状态"""
        return {
            controller_id: {
                "last_sync": last_sync.isoformat() if last_sync else None,
                "status": "active" if controller_id in self.controllers else "inactive"
            }
            for controller_id, last_sync in self.last_sync.items()
        } 