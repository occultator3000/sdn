from dotenv import load_dotenv
import os
from typing import Dict

class Settings:
    def __init__(self):
        # 从 .env 文件加载环境变量
        load_dotenv()
        
        # 读取环境变量
        self.RYU_PATH = os.getenv("RYU_PATH")
        self.POX_PATH = os.getenv("POX_PATH")
        self.ODL_PATH = os.getenv("ODL_PATH")
        
        # 控制器端口配置
        self.RYU_PORT = int(os.getenv("RYU_PORT", 6653))
        self.POX_PORT = int(os.getenv("POX_PORT", 6633))
        self.ODL_PORT = int(os.getenv("ODL_PORT", 6633))
        
        # 控制器应用配置
        self.RYU_APP = os.getenv("RYU_APP", "ryu.app.simple_switch_13")
        self.POX_APP = os.getenv("POX_APP", "forwarding.l2_learning")
        self.ODL_APP = os.getenv("ODL_APP", "")
        
        # 系统配置
        self.MININET_ENABLED = os.getenv("MININET_ENABLED", "true").lower() == "true"
        self.DEBUG = os.getenv("DEBUG", "true").lower() == "true"
        
        # API配置
        self.API_V1_STR = os.getenv("API_V1_STR", "/api/v1")
        self.HOST = os.getenv("HOST", "0.0.0.0")
        self.PORT = int(os.getenv("PORT", 8000))
        
        # 日志配置
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        
        # 控制器配置
        self.CONTROLLERS: Dict[str, dict] = {
            'ryu': {
                'path': self.RYU_PATH,
                'port': self.RYU_PORT,
                'app': self.RYU_APP
            },
            'pox': {
                'path': self.POX_PATH,
                'port': self.POX_PORT,
                'app': self.POX_APP
            },
            'odl': {
                'path': self.ODL_PATH,
                'port': self.ODL_PORT,
                'app': self.ODL_APP
            }
        }

# 创建全局设置实例
settings = Settings()