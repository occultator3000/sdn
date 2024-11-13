from typing import Dict, Any, Optional
import asyncio
import logging
from datetime import datetime
from ...controllers.base import BaseController
from ...controllers.sync.flow_synchronizer import FlowSynchronizer

class ControllerSwitcher:
    """控制器切换器"""
    
    def __init__(self, flow_synchronizer: FlowSynchronizer):
        self.logger = logging.getLogger("controller_switcher")
        self.flow_synchronizer = flow_synchronizer
        self.switch_history = []
        self.max_history = 10
        self.switching = False  # 切换锁
    
    async def switch_controller(self, 
                              from_controller: BaseController,
                              to_controller: BaseController) -> bool:
        """执行控制器切换"""
        if self.switching:
            self.logger.warning("Another switch operation is in progress")
            return False
            
        self.switching = True
        try:
            switch_start = datetime.now()
            
            # 1. 准备切换
            success = await self._prepare_switch(from_controller, to_controller)
            if not success:
                raise Exception("Switch preparation failed")
            
            # 2. 同步流表
            success = await self.flow_synchronizer.force_sync(
                from_controller.controller_id,
                to_controller.controller_id
            )
            if not success:
                raise Exception("Flow table synchronization failed")
            
            # 3. 执行切换
            success = await self._execute_switch(from_controller, to_controller)
            if not success:
                raise Exception("Switch execution failed")
            
            # 4. 验证切换
            success = await self._verify_switch(to_controller)
            if not success:
                raise Exception("Switch verification failed")
            
            # 记录切换历史
            switch_duration = (datetime.now() - switch_start).total_seconds()
            self._record_switch(from_controller, to_controller, True, switch_duration)
            
            self.logger.info(
                f"Successfully switched from {from_controller.controller_id} "
                f"to {to_controller.controller_id}"
            )
            return True
            
        except Exception as e:
            self.logger.error(f"Switch operation failed: {str(e)}")
            self._record_switch(from_controller, to_controller, False, 0)
            # 尝试回滚
            await self._rollback_switch(from_controller, to_controller)
            return False
            
        finally:
            self.switching = False
    
    async def _prepare_switch(self,
                            from_controller: BaseController,
                            to_controller: BaseController) -> bool:
        """准备切换操作"""
        try:
            # 检查目标控制器状态
            if not await to_controller.health_check():
                self.logger.error("Target controller health check failed")
                return False
            
            # 确保目标控制器已启动
            if to_controller.status != "active":
                success = await to_controller.start()
                if not success:
                    self.logger.error("Failed to start target controller")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Switch preparation failed: {str(e)}")
            return False
    
    async def _execute_switch(self,
                            from_controller: BaseController,
                            to_controller: BaseController) -> bool:
        """执行切换操作"""
        try:
            # 更新控制器角色
            await from_controller.set_role("slave")
            await to_controller.set_role("master")
            
            # 等待角色切换生效
            await asyncio.sleep(1)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Switch execution failed: {str(e)}")
            return False
    
    async def _verify_switch(self, to_controller: BaseController) -> bool:
        """验证切换结果"""
        try:
            # 验证新控制器是否正常工作
            if not await to_controller.health_check():
                return False
            
            # 验证流表是否正确同步
            flows = await to_controller.get_flows()
            if not flows:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Switch verification failed: {str(e)}")
            return False
    
    async def _rollback_switch(self,
                             from_controller: BaseController,
                             to_controller: BaseController):
        """回滚切换操作"""
        try:
            self.logger.info("Attempting to rollback switch operation")
            
            # 恢复原控制器角色
            await from_controller.set_role("master")
            await to_controller.set_role("slave")
            
            # 重新同步原控制器的流表
            await self.flow_synchronizer.force_sync(
                from_controller.controller_id,
                to_controller.controller_id
            )
            
        except Exception as e:
            self.logger.error(f"Rollback failed: {str(e)}")
    
    def _record_switch(self,
                      from_controller: BaseController,
                      to_controller: BaseController,
                      success: bool,
                      duration: float):
        """记录切换历史"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "from_controller": from_controller.controller_id,
            "to_controller": to_controller.controller_id,
            "success": success,
            "duration": duration
        }
        
        self.switch_history.append(record)
        if len(self.switch_history) > self.max_history:
            self.switch_history.pop(0)
    
    def get_switch_history(self) -> List[Dict[str, Any]]:
        """获取切换历史"""
        return self.switch_history 