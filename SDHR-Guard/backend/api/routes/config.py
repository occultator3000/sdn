from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from ..schemas.config import (
    DHRConfig,
    AlertConfig,
    SystemConfig,
    FullConfig
)
from ..services.config import ConfigService

router = APIRouter(prefix="/api/config")
config_service = ConfigService()

@router.get("/", response_model=FullConfig)
async def get_config():
    """获取完整配置"""
    try:
        return await config_service.get_config()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def save_config(config: FullConfig):
    """保存完整配置"""
    try:
        await config_service.save_config(config.dict())
        return {"message": "Configuration saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/dhr")
async def update_dhr_config(config: DHRConfig):
    """更新DHR配置"""
    try:
        await config_service.update_module_config("dhr", config.dict())
        return {"message": "DHR configuration updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/alert")
async def update_alert_config(config: AlertConfig):
    """更新告警配置"""
    try:
        await config_service.update_module_config("alert", config.dict())
        return {"message": "Alert configuration updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/system")
async def update_system_config(config: SystemConfig):
    """更新系统配置"""
    try:
        await config_service.update_module_config("system", config.dict())
        return {"message": "System configuration updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset")
async def reset_config():
    """重置配置"""
    try:
        await config_service.reset_config()
        return {"message": "Configuration reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/validate")
async def validate_config():
    """验证配置"""
    try:
        is_valid = await config_service.validate_config()
        return {"valid": is_valid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 