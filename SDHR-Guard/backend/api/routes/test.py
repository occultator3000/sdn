from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
from ..schemas.test import (
    TestResults,
    TestReport,
    SecurityMetrics
)
from ..services.test import TestService
from ..core.error_handler import ErrorHandler

router = APIRouter(prefix="/api/test")
test_service = TestService()
error_handler = ErrorHandler()

@router.get("/results", response_model=TestResults)
async def get_test_results():
    """获取测试结果"""
    try:
        results = await test_service.get_results()
        return results
    except Exception as e:
        await error_handler.handle_error(e)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/results/latest", response_model=TestResults)
async def get_latest_results():
    """获取最新测试结果"""
    try:
        results = await test_service.get_latest_results()
        return results
    except Exception as e:
        await error_handler.handle_error(e)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/security", response_model=SecurityMetrics)
async def get_security_metrics():
    """获取安全指标"""
    try:
        metrics = await test_service.get_security_metrics()
        return metrics
    except Exception as e:
        await error_handler.handle_error(e)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/report")
async def generate_report(background_tasks: BackgroundTasks):
    """生成测试报告"""
    try:
        # 在后台生成报告
        background_tasks.add_task(test_service.generate_report)
        return {"message": "Report generation started"}
    except Exception as e:
        await error_handler.handle_error(e)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/report/{report_id}")
async def get_report(report_id: str):
    """获取测试报告"""
    try:
        report = await test_service.get_report(report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        return report
    except Exception as e:
        await error_handler.handle_error(e)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/differences")
async def get_differences():
    """获取控制器差异"""
    try:
        differences = await test_service.get_differences()
        return differences
    except Exception as e:
        await error_handler.handle_error(e)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommendations")
async def get_recommendations():
    """获取优化建议"""
    try:
        recommendations = await test_service.get_recommendations()
        return recommendations
    except Exception as e:
        await error_handler.handle_error(e)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/export")
async def export_results():
    """导出测试结果"""
    try:
        file_path = await test_service.export_results()
        return {"file_path": file_path}
    except Exception as e:
        await error_handler.handle_error(e)
        raise HTTPException(status_code=500, detail=str(e)) 