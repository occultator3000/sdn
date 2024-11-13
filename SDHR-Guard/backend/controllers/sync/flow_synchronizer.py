from typing import Dict, List, Any
import asyncio
import logging
from datetime import datetime
from ..base import BaseController

class FlowSynchronizer:
    """控制器间流表同步器"""
    
    def __init__(self):
        self.logger = logging.getLogger("flow_synchronizer")
        self.controllers: Dict[str, BaseController] = {}
        self.sync_interval = 5  # 同步间隔（秒）
        self._running = False
        self.last_sync = {}  # 记录每个控制器最后同步时间
    
    def add_controller(self, controller_id: str, controller: BaseController):
        """添加需要同步的控制器"""
        self.controllers[controller_id] = controller
        self.last_sync[controller_id] = datetime.now()
        self.logger.info(f"Added controller {controller_id} to synchronizer")
    
    def remove_controller(self, controller_id: str):
        """移除控制器"""
        if controller_id in self.controllers:
            del self.controllers[controller_id]
            del self.last_sync[controller_id]
            self.logger.info(f"Removed controller {controller_id} from synchronizer")
    
    async def start_sync(self):
        """启动同步进程"""
        self._running = True
        while self._running:
            try:
                await self._sync_all_controllers()
                await asyncio.sleep(self.sync_interval)
            except Exception as e:
                self.logger.error(f"Error in sync process: {str(e)}")
    
    async def stop_sync(self):
        """停止同步进程"""
        self._running = False
    
    async def _sync_all_controllers(self):
        """同步所有控制器的流表"""
        if len(self.controllers) < 2:
            return
            
        # 获取所有控制器的流表
        flow_tables = {}
        for controller_id, controller in self.controllers.items():
            flows = await controller.get_flows()
            flow_tables[controller_id] = flows
        
        # 比较和同步流表
        await self._sync_flow_tables(flow_tables)
    
    async def _sync_flow_tables(self, flow_tables: Dict[str, Dict[str, Any]]):
        """同步流表差异"""
        try:
            # 获取所有流表项的并集
            all_flows = set()
            for flows in flow_tables.values():
                all_flows.update(flows.keys())
            
            # 对每个控制器进行同步
            for controller_id, controller in self.controllers.items():
                current_flows = flow_tables[controller_id]
                
                # 找出需要添加和删除的流表项
                missing_flows = all_flows - set(current_flows.keys())
                
                # 同步缺失的流表项
                for flow_id in missing_flows:
                    # 从其他控制器获取流表项
                    flow_rule = None
                    for other_flows in flow_tables.values():
                        if flow_id in other_flows:
                            flow_rule = other_flows[flow_id]
                            break
                    
                    if flow_rule:
                        success = await controller.install_flow(flow_rule)
                        if success:
                            self.logger.info(
                                f"Synchronized flow {flow_id} to controller {controller_id}"
                            )
                        else:
                            self.logger.error(
                                f"Failed to sync flow {flow_id} to controller {controller_id}"
                            )
            
            # 更新同步时间
            current_time = datetime.now()
            for controller_id in self.controllers:
                self.last_sync[controller_id] = current_time
                
        except Exception as e:
            self.logger.error(f"Error during flow table sync: {str(e)}")
    
    async def force_sync(self, source_controller_id: str, target_controller_id: str):
        """强制两个控制器之间的同步"""
        try:
            if (source_controller_id not in self.controllers or 
                target_controller_id not in self.controllers):
                return False
            
            source = self.controllers[source_controller_id]
            target = self.controllers[target_controller_id]
            
            # 获取源控制器的流表
            source_flows = await source.get_flows()
            
            # 同步到目标控制器
            for flow_id, flow_rule in source_flows.items():
                await target.install_flow(flow_rule)
            
            self.last_sync[target_controller_id] = datetime.now()
            return True
            
        except Exception as e:
            self.logger.error(
                f"Error during force sync between {source_controller_id} "
                f"and {target_controller_id}: {str(e)}"
            )
            return False
    
    def get_sync_status(self) -> Dict[str, Any]:
        """获取同步状态"""
        return {
            controller_id: {
                "last_sync": last_sync.isoformat(),
                "status": "active" if controller.status == "active" else "inactive"
            }
            for controller_id, (controller, last_sync) in 
            zip(self.controllers.items(), self.last_sync.items())
        } 