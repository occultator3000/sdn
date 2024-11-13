import pytest
import asyncio
from typing import Dict, Any
from ...controllers.manager import ControllerManager
from ...controllers.ryu.controller import RyuController
from ...controllers.opendaylight.controller import OpenDaylightController
from ...dhr.scheduler.adaptive import AdaptiveScheduler
from ...services.sync.config_synchronizer import ConfigSynchronizer
from ...core.error_handler import ErrorHandler

class TestDHRIntegration:
    """DHR系统集成测试"""
    
    @pytest.fixture
    async def setup_system(self):
        """系统初始化"""
        # 创建系统组件
        self.manager = ControllerManager()
        self.scheduler = AdaptiveScheduler()
        self.synchronizer = ConfigSynchronizer()
        self.error_handler = ErrorHandler()
        
        # 初始化控制器
        self.controllers = {
            'ryu': await self.manager.create_controller('ryu', {
                'port': 6633,
                'host': 'localhost'
            }),
            'odl': await self.manager.create_controller('opendaylight', {
                'port': 6653,
                'host': 'localhost'
            })
        }
        
        yield
        
        # 清理资源
        for controller in self.controllers.values():
            await controller.stop()
    
    @pytest.mark.asyncio
    async def test_controller_lifecycle(self, setup_system):
        """测试控制器生命周期"""
        ryu_controller = self.controllers['ryu']
        
        # 测试启动
        success = await ryu_controller.start()
        assert success, "控制器启动失败"
        assert ryu_controller.status == "active"
        
        # 测试健康检查
        health = await ryu_controller.health_check()
        assert health, "健康检查失败"
        
        # 测试停止
        success = await ryu_controller.stop()
        assert success, "控制器停止失败"
        assert ryu_controller.status == "inactive"
    
    @pytest.mark.asyncio
    async def test_dhr_scheduling(self, setup_system):
        """测试DHR调度"""
        # 启动所有控制器
        for controller in self.controllers.values():
            await controller.start()
        
        # 测试调度决策
        decision = await self.scheduler.select_controller()
        assert decision in self.controllers.keys(), "调度决策无效"
        
        # 测试控制器切换
        old_controller = self.manager.get_active_controller()
        new_controller = next(
            c for c in self.controllers.keys() if c != old_controller
        )
        
        success = await self.scheduler.switch_controller(
            old_controller,
            new_controller
        )
        assert success, "控制器切换失败"
        
        # 验证切换结果
        current = self.manager.get_active_controller()
        assert current == new_controller, "控制器切换结果不正确"
    
    @pytest.mark.asyncio
    async def test_config_synchronization(self, setup_system):
        """测试配置同步"""
        # 准备测试配置
        test_config = {
            "flow_timeout": 30,
            "priority": 100
        }
        
        # 更新配置
        ryu_controller = self.controllers['ryu']
        await ryu_controller.update_config(test_config)
        
        # 触发同步
        await self.synchronizer.sync_config()
        
        # 验证同步结果
        for controller in self.controllers.values():
            controller_config = await controller.get_config()
            assert controller_config == test_config, "配置同步失败"
    
    @pytest.mark.asyncio
    async def test_error_handling(self, setup_system):
        """测试错误处理"""
        # 模拟控制器故障
        ryu_controller = self.controllers['ryu']
        await ryu_controller.stop()
        ryu_controller.status = "error"
        
        # 验证错误处理
        handled = await self.error_handler.handle_error(
            Exception("Controller failure"),
            {"controller": ryu_controller}
        )
        assert handled, "错误处理失败"
        
        # 验证自动切换
        current = self.manager.get_active_controller()
        assert current != 'ryu', "故障切换失败"
    
    @pytest.mark.asyncio
    async def test_performance_monitoring(self, setup_system):
        """测试性能监控"""
        ryu_controller = self.controllers['ryu']
        await ryu_controller.start()
        
        # 获取性能指标
        metrics = await ryu_controller.get_metrics()
        
        # 验证指标
        assert 'response_time' in metrics, "缺少响应时间指标"
        assert 'flow_count' in metrics, "缺少流表计数指标"
        assert 'error_count' in metrics, "缺少错误计数指标"
    
    @pytest.mark.asyncio
    async def test_system_stability(self, setup_system):
        """测试系统稳定性"""
        # 启动所有控制器
        for controller in self.controllers.values():
            await controller.start()
        
        # 执行多次切换
        for _ in range(5):
            # 获取当前控制器
            current = self.manager.get_active_controller()
            
            # 选择新控制器
            new_controller = next(
                c for c in self.controllers.keys() if c != current
            )
            
            # 执行切换
            success = await self.scheduler.switch_controller(
                current,
                new_controller
            )
            assert success, "控制器切换失败"
            
            # 等待系统稳定
            await asyncio.sleep(2)
            
            # 验证系统状态
            assert self.manager.get_active_controller() == new_controller
            assert await self.synchronizer.check_sync_status() 