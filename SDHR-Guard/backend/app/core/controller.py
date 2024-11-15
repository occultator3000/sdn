import asyncio
import logging
import os
from typing import Dict
from config.settings import settings

logger = logging.getLogger(__name__)

class ControllerManager:
    def __init__(self):
        self.controllers: Dict[str, dict] = {
            'ryu': {
                'status': 'uninit',  # 初始状态为 uninit
                'health': 'uninit',  # 健康状态为 uninit
                'path': settings.CONTROLLERS['ryu']['path'],
                'port': settings.CONTROLLERS['ryu']['port'],
                'app': settings.CONTROLLERS['ryu']['app'],
                'process': None
            },
            'pox': {
                'status': 'uninit',
                'health': 'uninit',
                'path': settings.CONTROLLERS['pox']['path'],
                'port': settings.CONTROLLERS['pox']['port'],
                'app': settings.CONTROLLERS['pox']['app'],
                'process': None
            },
            'odl': {
                'status': 'uninit',
                'health': 'uninit',
                'path': settings.CONTROLLERS['odl']['path'],
                'port': settings.CONTROLLERS['odl']['port'],
                'app': settings.CONTROLLERS['odl']['app'],
                'process': None
            }
        }

    def get_all_status(self):
        """获取所有控制器的状态"""
        return {
            controller_id: {
                'status': controller['status'],
                'port': controller['port'],
                'health': controller['health']
            }
            for controller_id, controller in self.controllers.items()
        }

    async def validate_paths(self):
        """验证所有控制器路径"""
        for controller_id, controller in self.controllers.items():
            if not await self._check_path(controller['path']):
                logger.warning(f"控制器 {controller_id} 路径不存在: {controller['path']}")

    async def start_controller(self, controller_id: str):
        """启动指定控制器"""
        if controller_id not in self.controllers:
            raise ValueError(f"未知的控制器: {controller_id}")
        
        controller = self.controllers[controller_id]
        if controller['status'] == 'running':
            logger.info(f"控制器 {controller_id} 已经在运行")
            return {"status": "already_running"}
        
        try:
            # 构建启动命令
            cmd = f"{controller['path']}"
            if controller['app']:
                cmd += f" {controller['app']}"
                
            # 异步启动控制器进程
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            controller['process'] = process
            controller['status'] = 'running'
            
            # 等待控制器初始化
            await asyncio.sleep(2)
            
            # 启动后立即进行健康检查
            try:
                reader, writer = await asyncio.open_connection('127.0.0.1', controller['port'])
                writer.close()
                await writer.wait_closed()
                controller['health'] = 'healthy'
                logger.info(f"控制器 {controller_id} 已启动且健康")
            except Exception as e:
                controller['health'] = 'unhealthy'
                logger.warning(f"控制器 {controller_id} 已启动但无法通过健康检查: {str(e)}")
            
            return {"status": "started", "health": controller['health']}
        except Exception as e:
            logger.error(f"启动控制器 {controller_id} 失败: {str(e)}")
            controller['health'] = 'unhealthy'
            return {"status": "error", "message": str(e)}

    async def stop_controller(self, controller_id: str):
        """停止指定控制器"""
        if controller_id not in self.controllers:
            raise ValueError(f"未知的控制器: {controller_id}")
        
        controller = self.controllers[controller_id]
        if controller['status'] == 'stopped':
            logger.info(f"控制器 {controller_id} 已经停止")
            return {"status": "already_stopped"}
        
        try:
            if controller_id == 'odl':
                # ODL 特殊处理：使用 karaf 的 stop 命令
                stop_cmd = f"{os.path.dirname(controller['path'])}/stop"
                process = await asyncio.create_subprocess_shell(
                    stop_cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await process.wait()
            else:
                # 其他控制器的常规停止方式
                if controller['process']:
                    controller['process'].terminate()
                    await controller['process'].wait()
                
            controller['status'] = 'stopped'
            controller['health'] = 'uninit'  # 停止时重置为 uninit
            controller['process'] = None
            logger.info(f"控制器 {controller_id} 已停止")
            return {"status": "stopped"}
        except Exception as e:
            logger.error(f"停止控制器 {controller_id} 失败: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def _check_path(self, path: str) -> bool:
        """检查文件路径是否存在"""
        try:
            process = await asyncio.create_subprocess_shell(
                f"test -f {path}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.wait()
            return process.returncode == 0
        except Exception:
            return False

    async def health_check(self, controller_id: str):
        """检查控制器健康状态"""
        if controller_id not in self.controllers:
            raise ValueError(f"未知的控制器: {controller_id}")
        
        controller = self.controllers[controller_id]
        if controller['status'] == 'stopped':
            return {"status": "stopped", "health": "uninit"}
        
        try:
            # 检查端口是否可访问
            try:
                reader, writer = await asyncio.open_connection('127.0.0.1', controller['port'])
                writer.close()
                await writer.wait_closed()
                controller['health'] = 'healthy'
                return {"status": controller['status'], "health": "healthy"}
            except Exception as e:
                controller['health'] = 'unhealthy'
                return {"status": controller['status'], "health": "unhealthy", "message": f"端口不可访问: {str(e)}"}
        except Exception as e:
            logger.error(f"控制器 {controller_id} 健康检查失败: {str(e)}")
            controller['health'] = 'unhealthy'
            return {"status": controller['status'], "health": "unhealthy", "message": str(e)}