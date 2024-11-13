import sys
import types
import inspect
from typing import Dict, Any, Callable, Set
from functools import wraps
import logging

class Instrumentor:
    """白盒插桩器"""
    
    def __init__(self):
        self.logger = logging.getLogger("instrumentor")
        self.probes: Dict[str, Dict[str, Callable]] = {}
        self.collected_data: Dict[str, list] = {}
        self.instrumented_modules: Set[str] = set()
    
    def instrument_module(self, module_name: str, target_functions: list = None):
        """对模块进行插桩"""
        try:
            module = sys.modules.get(module_name)
            if not module:
                self.logger.error(f"Module not found: {module_name}")
                return
            
            # 获取目标函数
            functions = self._get_target_functions(module, target_functions)
            
            # 对每个函数进行插桩
            for func_name, func in functions:
                self._instrument_function(module_name, func_name, func)
            
            self.instrumented_modules.add(module_name)
            self.logger.info(f"Instrumented module: {module_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to instrument module {module_name}: {str(e)}")
    
    def _get_target_functions(self, module, target_functions: list = None):
        """获取需要插桩的函数"""
        functions = []
        for name, obj in inspect.getmembers(module):
            # 如果指定了目标函数，只处理这些函数
            if target_functions and name not in target_functions:
                continue
                
            # 检查是否是函数或方法
            if inspect.isfunction(obj) or inspect.ismethod(obj):
                functions.append((name, obj))
        return functions
    
    def _instrument_function(self, module_name: str, func_name: str, func: Callable):
        """对函数进行插桩"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 记录函数调用
            call_data = {
                'timestamp': datetime.now().isoformat(),
                'args': str(args),
                'kwargs': str(kwargs)
            }
            
            try:
                # 执行前探针
                if probe := self.probes.get(f"{module_name}.{func_name}.before"):
                    await probe(call_data)
                
                # 执行函数
                result = await func(*args, **kwargs)
                
                # 记录返回值
                call_data['result'] = str(result)
                call_data['status'] = 'success'
                
                # 执行后探针
                if probe := self.probes.get(f"{module_name}.{func_name}.after"):
                    await probe(call_data)
                
                return result
                
            except Exception as e:
                # 记录异常
                call_data['error'] = str(e)
                call_data['status'] = 'error'
                
                # 执行异常探针
                if probe := self.probes.get(f"{module_name}.{func_name}.error"):
                    await probe(call_data)
                
                raise
                
            finally:
                # 保存调用数据
                key = f"{module_name}.{func_name}"
                if key not in self.collected_data:
                    self.collected_data[key] = []
                self.collected_data[key].append(call_data)
        
        # 替换原函数
        setattr(sys.modules[module_name], func_name, wrapper)
    
    def add_probe(self, target: str, probe: Callable):
        """添加探针"""
        self.probes[target] = probe
        self.logger.info(f"Added probe for {target}")
    
    def get_collected_data(self, module_name: str = None,
                          func_name: str = None) -> Dict[str, list]:
        """获取收集的数据"""
        if module_name and func_name:
            key = f"{module_name}.{func_name}"
            return {key: self.collected_data.get(key, [])}
        elif module_name:
            return {k: v for k, v in self.collected_data.items()
                   if k.startswith(module_name)}
        return self.collected_data
    
    def clear_data(self):
        """清除收集的数据"""
        self.collected_data.clear() 