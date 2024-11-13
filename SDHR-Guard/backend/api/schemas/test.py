from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime

class TestMetrics(BaseModel):
    """测试指标"""
    total_tests: int
    success_rate: float
    response_times: Dict[str, List[float]]
    performance_scores: Dict[str, float]

class SecurityMetrics(BaseModel):
    """安全指标"""
    vulnerability: float
    error_handling: float
    input_validation: float
    details: Dict[str, List[Dict[str, Any]]]

class Difference(BaseModel):
    """控制器差异"""
    type: str
    controllers: List[str]
    description: str
    impact: float
    timestamp: datetime

class Recommendation(BaseModel):
    """优化建议"""
    content: str
    priority: str
    category: str
    timestamp: datetime

class TestResults(BaseModel):
    """测试结果"""
    metrics: TestMetrics
    security: SecurityMetrics
    differences: List[Difference]
    recommendations: List[Recommendation]
    timestamp: datetime

class TestReport(BaseModel):
    """测试报告"""
    id: str
    results: TestResults
    analysis: Dict[str, Any]
    generated_at: datetime 