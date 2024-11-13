"""
系统配置文件
"""

from .dhr_config import DHR_CONFIG, CONTROLLER_TYPES, LOGGING_CONFIG

# 系统配置
SYSTEM_CONFIG = {
    'debug': True,
    'host': 'localhost',
    'port': 5000,
    'secret_key': 'your-secret-key-here',
    
    # 引入DHR配置
    'dhr': DHR_CONFIG,
    'controllers': CONTROLLER_TYPES,
    'logging': LOGGING_CONFIG
} 