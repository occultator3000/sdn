from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import logging

@dataclass
class FlowRule:
    """流表项数据结构"""
    flow_id: str                  # 流表项ID
    switch_id: str               # 交换机ID
    priority: int                # 优先级
    match: Dict[str, Any]        # 匹配规则
    actions: List[Dict[str, Any]] # 动作列表
    idle_timeout: int = 0        # 空闲超时
    hard_timeout: int = 0        # 硬超时
    created_at: datetime = datetime.now()

class FlowManager:
    """流表管理器"""
    
    def __init__(self):
        self.logger = logging.getLogger("flow_manager")
        self.flows: Dict[str, FlowRule] = {}
        
    def create_flow_rule(self, 
                        switch_id: str,
                        priority: int,
                        match: Dict[str, Any],
                        actions: List[Dict[str, Any]],
                        idle_timeout: int = 0,
                        hard_timeout: int = 0) -> FlowRule:
        """创建新的流表项"""
        flow_id = f"flow_{switch_id}_{len(self.flows)}"
        
        flow_rule = FlowRule(
            flow_id=flow_id,
            switch_id=switch_id,
            priority=priority,
            match=match,
            actions=actions,
            idle_timeout=idle_timeout,
            hard_timeout=hard_timeout
        )
        
        self.flows[flow_id] = flow_rule
        self.logger.info(f"Created flow rule: {flow_id}")
        return flow_rule
    
    def get_flow(self, flow_id: str) -> Optional[FlowRule]:
        """获取指定的流表项"""
        return self.flows.get(flow_id)
    
    def get_switch_flows(self, switch_id: str) -> List[FlowRule]:
        """获取指定交换机的所有流表项"""
        return [
            flow for flow in self.flows.values()
            if flow.switch_id == switch_id
        ]
    
    def update_flow(self, flow_id: str, 
                   actions: Optional[List[Dict[str, Any]]] = None,
                   priority: Optional[int] = None) -> Optional[FlowRule]:
        """更新流表项"""
        flow = self.flows.get(flow_id)
        if not flow:
            return None
            
        if actions is not None:
            flow.actions = actions
        if priority is not None:
            flow.priority = priority
            
        self.logger.info(f"Updated flow rule: {flow_id}")
        return flow
    
    def delete_flow(self, flow_id: str) -> bool:
        """删除流表项"""
        if flow_id in self.flows:
            del self.flows[flow_id]
            self.logger.info(f"Deleted flow rule: {flow_id}")
            return True
        return False
    
    def to_dict(self, flow_rule: FlowRule) -> Dict[str, Any]:
        """将流表项转换为字典格式"""
        return {
            "flow_id": flow_rule.flow_id,
            "switch_id": flow_rule.switch_id,
            "priority": flow_rule.priority,
            "match": flow_rule.match,
            "actions": flow_rule.actions,
            "idle_timeout": flow_rule.idle_timeout,
            "hard_timeout": flow_rule.hard_timeout,
            "created_at": flow_rule.created_at.isoformat()
        }
    
    def from_dict(self, data: Dict[str, Any]) -> FlowRule:
        """从字典格式创建流表项"""
        return FlowRule(
            flow_id=data["flow_id"],
            switch_id=data["switch_id"],
            priority=data["priority"],
            match=data["match"],
            actions=data["actions"],
            idle_timeout=data["idle_timeout"],
            hard_timeout=data["hard_timeout"],
            created_at=datetime.fromisoformat(data["created_at"])
        ) 