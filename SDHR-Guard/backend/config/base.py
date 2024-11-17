"""基础配置"""
import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 安全配置
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

# 数据库配置
DATABASE = {
    'default': {
        'ENGINE': 'sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 控制器配置
CONTROLLER_SETTINGS = {
    'POX': {
        'enabled': True,
        'path': os.getenv('POX_PATH', '/opt/pox'),
        'port': 6633,
    },
    'RYU': {
        'enabled': True,
        'path': os.getenv('RYU_PATH', '/opt/ryu'),
        'port': 6634,
    },
    'ODL': {
        'enabled': True,
        'path': os.getenv('ODL_PATH', '/opt/opendaylight'),
        'port': 6635,
    }
}

# DHR配置
DHR_SETTINGS = {
    'scheduler_interval': 5,  # 调度间隔（秒）
    'monitor_interval': 1,    # 监控间隔（秒）
    'max_controllers': 5,     # 最大控制器数量
    'min_controllers': 2      # 最小控制器数量
}

# 日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.FileHandler',
            'filename': 'logs/app.log',
        }
    },
    'loggers': {
        '': {
            'handlers': ['default', 'file'],
            'level': 'INFO',
            'propagate': True
        }
    }
} 