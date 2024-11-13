import os
import subprocess
import aiohttp
import json
from typing import Dict, List, Any
from ..base import BaseController
from ..flow_manager import FlowRule

class RyuController(BaseController):
    """RYU控制器实现"""
    
    def __init__(self, controller_id: str, config: Dict[str, Any]):
        super().__init__(controller_id, config)
        self.ryu_process = None
        self.ryu_path = config.get('path', '/usr/local/bin/ryu-manager')
        self.port = config.get('port', 6634)
        self.rest_port = config.get('rest_port', 8080)
        self.apps = config.get('apps', [
            'ryu.app.simple_switch_13',
            'ryu.app.ofctl_rest'
        ])
        self.base_url = f"http://localhost:{self.rest_port}"
        
    async def get_flows(self) -> Dict[str, Any]:
        """获取流表信息"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/stats/flow/all") as response:
                    if response.status == 200:
                        flows = await response.json()
                        return self._format_flows(flows)
                    else:
                        self.logger.error(f"Failed to get flows: {response.status}")
                        return {}
        except Exception as e:
            self.logger.error(f"Error getting flows: {str(e)}")
            return {}
    
    async def install_flow(self, flow_rule: Dict[str, Any]) -> bool:
        """安装流表项"""
        try:
            flow_data = self._convert_to_ryu_format(flow_rule)
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/stats/flowentry/add"
                async with session.post(url, json=flow_data) as response:
                    return response.status == 200
        except Exception as e:
            self.logger.error(f"Error installing flow: {str(e)}")
            return False
    
    async def remove_flow(self, flow_id: str) -> bool:
        """删除流表项"""
        try:
            flow_rule = self.flow_manager.get_flow(flow_id)
            if not flow_rule:
                return False
                
            flow_data = self._convert_to_ryu_format(
                self.flow_manager.to_dict(flow_rule)
            )
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/stats/flowentry/delete"
                async with session.post(url, json=flow_data) as response:
                    return response.status == 200
        except Exception as e:
            self.logger.error(f"Error removing flow: {str(e)}")
            return False
    
    def _convert_to_ryu_format(self, flow_rule: Dict[str, Any]) -> Dict[str, Any]:
        """转换为RYU格式的流表项"""
        return {
            "dpid": int(flow_rule["switch_id"], 16),
            "priority": flow_rule["priority"],
            "match": flow_rule["match"],
            "actions": flow_rule["actions"],
            "idle_timeout": flow_rule["idle_timeout"],
            "hard_timeout": flow_rule["hard_timeout"]
        }
    
    def _format_flows(self, ryu_flows: Dict[str, Any]) -> List[Dict[str, Any]]:
        """将RYU格式的流表转换为标准格式"""
        formatted_flows = []
        for dpid, flows in ryu_flows.items():
            for flow in flows:
                formatted_flow = {
                    "flow_id": f"flow_{dpid}_{flow['priority']}",
                    "switch_id": format(int(dpid), 'x'),
                    "priority": flow["priority"],
                    "match": flow["match"],
                    "actions": flow["actions"],
                    "idle_timeout": flow.get("idle_timeout", 0),
                    "hard_timeout": flow.get("hard_timeout", 0)
                }
                formatted_flows.append(formatted_flow)
        return formatted_flows
    
    async def get_switch_stats(self) -> Dict[str, Any]:
        """获取交换机统计信息"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/stats/switches") as response:
                    if response.status == 200:
                        switches = await response.json()
                        stats = {}
                        for dpid in switches:
                            # 获取端口统计
                            async with session.get(f"{self.base_url}/stats/port/{dpid}") as port_response:
                                if port_response.status == 200:
                                    stats[format(dpid, 'x')] = await port_response.json()
                        return stats
                    return {}
        except Exception as e:
            self.logger.error(f"Error getting switch stats: {str(e)}")
            return {}
    
    async def start(self) -> bool:
        try:
            # 启动RYU控制器进程
            cmd = [
                self.ryu_path,
                '--ofp-tcp-listen-port',
                str(self.port),
                *self.apps
            ]
            
            self.ryu_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.status = "active"
            self.logger.info(f"RYU controller {self.controller_id} started on port {self.port}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start RYU controller: {str(e)}")
            return False
    
    async def stop(self) -> bool:
        try:
            if self.ryu_process:
                self.ryu_process.terminate()
                self.ryu_process.wait()
                self.ryu_process = None
                self.status = "inactive"
                self.logger.info(f"RYU controller {self.controller_id} stopped")
            return True
        except Exception as e:
            self.logger.error(f"Failed to stop RYU controller: {str(e)}")
            return False
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        try:
            metrics = {}
            
            # 获取交换机统计信息
            async with aiohttp.ClientSession() as session:
                # 获取交换机列表
                async with session.get(f"{self.base_url}/stats/switches") as response:
                    if response.status == 200:
                        switches = await response.json()
                        
                        for dpid in switches:
                            # 获取端口统计
                            port_stats = await self._get_port_stats(session, dpid)
                            # 获取流表统计
                            flow_stats = await self._get_flow_stats(session, dpid)
                            # 获取表统计
                            table_stats = await self._get_table_stats(session, dpid)
                            
                            metrics[f"switch_{dpid}"] = {
                                "ports": port_stats,
                                "flows": flow_stats,
                                "tables": table_stats
                            }
            
            return metrics
        except Exception as e:
            self.logger.error(f"Error getting performance metrics: {str(e)}")
            return {}
    
    async def _get_port_stats(self, session: aiohttp.ClientSession, dpid: int) -> Dict[str, Any]:
        """获取端口统计信息"""
        async with session.get(f"{self.base_url}/stats/port/{dpid}") as response:
            if response.status == 200:
                return await response.json()
            return {}
    
    async def _get_flow_stats(self, session: aiohttp.ClientSession, dpid: int) -> Dict[str, Any]:
        """获取流表统计信息"""
        async with session.get(f"{self.base_url}/stats/flow/{dpid}") as response:
            if response.status == 200:
                return await response.json()
            return {}
    
    async def _get_table_stats(self, session: aiohttp.ClientSession, dpid: int) -> Dict[str, Any]:
        """获取表统计信息"""
        async with session.get(f"{self.base_url}/stats/table/{dpid}") as response:
            if response.status == 200:
                return await response.json()
            return {}
 