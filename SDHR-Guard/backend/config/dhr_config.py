"""DHR配置文件"""

DHR_CONFIG = {
    # 控制器配置
    'min_controllers': 2,  # 最小控制器数量
    'max_controllers': 5,  # 最大控制器数量
    
    # 调度配置
    'schedule_interval': 5,    # 调度检查间隔(秒)
    'sync_interval': 30,       # 配置同步间隔(秒)
    'switch_cooldown': 10,     # 切换冷却时间(秒)
    
    # 性能阈值
    'thresholds': {
        'cpu_load': 0.8,       # CPU负载阈值
        'memory_usage': 0.8,   # 内存使用阈值
        'response_time': 1000, # 响应时间阈值(ms)
        'error_rate': 0.1      # 错误率阈值
    },
    
    # 调度策略配置
    'scheduler': {
        'default_strategy': 'health_aware',  # 默认调度策略
        'strategies': [
            'round_robin',     # 轮询调度
            'health_aware',    # 健康感知调度
            'diversity_aware'  # 异构感知调度
        ],
        'weights': {
            'health_score': 0.4,    # 健康度权重
            'diversity_score': 0.3,  # 异构度权重
            'load_score': 0.3       # 负载权重
        }
    },
    
    # 监控��置
    'monitoring': {
        'metrics_interval': 5,     # 指标收集间隔(秒)
        'health_check_interval': 10 # 健康检查间隔(秒)
    },
    
    # 安全配置
    'security': {
        'max_retry_attempts': 3,    # 最大重试次数
        'block_threshold': 5,       # 阻断阈值
        'alert_threshold': 3        # 告警阈值
    }
}

# 控制器类型配置
CONTROLLER_TYPES = {
    'ryu': {
        'class': 'RyuController',
        'default_port': 6633,
        'features': ['openflow', 'rest-api']
    },
    'pox': {
        'class': 'POXController',
        'default_port': 6634,
        'features': ['openflow']
    },
    'opendaylight': {
        'class': 'OpenDaylightController',
        'default_port': 6653,
        'features': ['openflow', 'rest-api', 'clustering']
    }
}

# 日志配置
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'handlers': ['file', 'console']
} 