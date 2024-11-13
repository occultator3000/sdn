import json
import os
from typing import Dict, Any
from datetime import datetime
import aiofiles
from ..core.exceptions import ConfigError
from .notification.config_notifier import ConfigNotifier

class ConfigService:
    """配置服务"""
    
    def __init__(self):
        self.config_file = "config/system_config.json"
        self.default_config = {
            "dhr": {
                "schedulerStrategy": "health_aware",
                "minControllers": 2,
                "maxControllers": 5,
                "scheduleInterval": 5,
                "switchCooldown": 30
            },
            "alert": {
                "loadThreshold": 80,
                "latencyThreshold": 1000,
                "errorThreshold": 10,
                "checkInterval": 30
            },
            "system": {
                "dataRetention": 30,
                "monitorInterval": 5,
                "logLevel": "info",
                "autoBackup": True,
                "backupInterval": 12
            }
        }
        self.notifier = ConfigNotifier()
    
    async def get_config(self) -> Dict[str, Any]:
        """获取配置"""
        try:
            if not os.path.exists(self.config_file):
                await self._save_default_config()
                return self.default_config
                
            async with aiofiles.open(self.config_file, 'r') as f:
                content = await f.read()
                return json.loads(content)
        except Exception as e:
            raise ConfigError(f"Failed to get config: {str(e)}")
    
    async def save_config(self, config: Dict[str, Any]):
        """保存配置并通知变更"""
        try:
            # 验证配置
            if not await self.validate_config(config):
                raise ConfigError("Invalid configuration")
                
            # 创建备份
            await self._backup_config()
            
            # 保存新配置
            async with aiofiles.open(self.config_file, 'w') as f:
                await f.write(json.dumps(config, indent=2))
                
            # 通知其他组件配置已更新
            await self._notify_config_update(config)
            
            # 通知各模块配置变更
            for module, module_config in config.items():
                await self.notifier.notify_change(module, module_config)
                
        except Exception as e:
            raise ConfigError(f"Failed to save and notify config: {str(e)}")
    
    async def update_module_config(self, module: str, config: Dict[str, Any]):
        """更新模块配置并通知"""
        try:
            current_config = await self.get_config()
            current_config[module].update(config)
            await self.save_config(current_config)
            
            # 通知模块配置变更
            await self.notifier.notify_change(module, config)
            
        except Exception as e:
            raise ConfigError(f"Failed to update and notify {module} config: {str(e)}")
    
    async def reset_config(self):
        """重置配置"""
        try:
            await self._save_default_config()
            return self.default_config
        except Exception as e:
            raise ConfigError(f"Failed to reset config: {str(e)}")
    
    async def validate_config(self, config: Dict[str, Any] = None) -> bool:
        """验证配置"""
        try:
            if config is None:
                config = await self.get_config()
                
            # 验证DHR配置
            dhr_config = config.get('dhr', {})
            if dhr_config['minControllers'] > dhr_config['maxControllers']:
                return False
                
            # 验证告警配置
            alert_config = config.get('alert', {})
            if not (0 <= alert_config['loadThreshold'] <= 100):
                return False
                
            # 验证系统配置
            system_config = config.get('system', {})
            if system_config['dataRetention'] < 1:
                return False
                
            return True
            
        except Exception:
            return False
    
    async def _save_default_config(self):
        """保存默认配置"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        await self.save_config(self.default_config)
    
    async def _backup_config(self):
        """备份配置"""
        if not os.path.exists(self.config_file):
            return
            
        backup_dir = "config/backups"
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{backup_dir}/config_backup_{timestamp}.json"
        
        async with aiofiles.open(self.config_file, 'r') as src, \
                  aiofiles.open(backup_file, 'w') as dst:
            content = await src.read()
            await dst.write(content)
    
    async def _notify_config_update(self, config: Dict[str, Any]):
        """通知配置更新"""
        # 实现配置更新的通知机制
        pass 
    
    async def start(self):
        """启动配置服务"""
        await self.notifier.start()
    
    async def stop(self):
        """停止配置服务"""
        await self.notifier.stop()