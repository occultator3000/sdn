import json
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, Any, List
from datetime import datetime
import seaborn as sns
from pathlib import Path

class TestResultAnalyzer:
    """测试结果分析器"""
    
    def __init__(self, results_dir: str = "test_results"):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
        self.analysis_results = {}
    
    def analyze_differential_results(self, test_results: List[Dict[str, Any]]):
        """分析差模测试结果"""
        try:
            # 基础统计
            basic_stats = self._calculate_basic_stats(test_results)
            
            # 性能分析
            performance_analysis = self._analyze_performance(test_results)
            
            # 行为差异分析
            behavior_analysis = self._analyze_behavior_differences(test_results)
            
            # 安全性分析
            security_analysis = self._analyze_security_aspects(test_results)
            
            # 保存分析结果
            self.analysis_results = {
                "basic_stats": basic_stats,
                "performance": performance_analysis,
                "behavior": behavior_analysis,
                "security": security_analysis,
                "timestamp": datetime.now().isoformat()
            }
            
            # 生成报告
            self._generate_report()
            
        except Exception as e:
            print(f"Analysis failed: {str(e)}")
            raise
    
    def _calculate_basic_stats(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算基础统计信息"""
        stats = {
            "total_tests": len(results),
            "success_rate": {},
            "error_rate": {},
            "response_times": {}
        }
        
        for result in results:
            for controller, data in result["results"].items():
                if controller not in stats["success_rate"]:
                    stats["success_rate"][controller] = 0
                    stats["error_rate"][controller] = 0
                    stats["response_times"][controller] = []
                
                # 统计成功率
                if "error" not in data:
                    stats["success_rate"][controller] += 1
                else:
                    stats["error_rate"][controller] += 1
                
                # 记录响应时间
                if "timing" in data:
                    stats["response_times"][controller].append(data["timing"])
        
        # 计算百分比
        total = len(results)
        for controller in stats["success_rate"]:
            stats["success_rate"][controller] = (
                stats["success_rate"][controller] / total * 100
            )
            stats["error_rate"][controller] = (
                stats["error_rate"][controller] / total * 100
            )
        
        return stats
    
    def _analyze_performance(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析性能数据"""
        performance_data = {
            "response_times": {},
            "throughput": {},
            "resource_usage": {}
        }
        
        for result in results:
            for controller, data in result["results"].items():
                if "timing" in data:
                    if controller not in performance_data["response_times"]:
                        performance_data["response_times"][controller] = []
                    performance_data["response_times"][controller].append(data["timing"])
        
        # 生成性能图表
        self._generate_performance_charts(performance_data)
        
        return performance_data
    
    def _analyze_behavior_differences(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析行为差异"""
        differences = {
            "flow_handling": [],
            "error_handling": [],
            "protocol_compliance": []
        }
        
        for result in results:
            test_id = result["test_id"]
            controller_results = result["results"]
            
            # 分析流表处理差异
            flow_diff = self._compare_flow_handling(controller_results)
            if flow_diff:
                differences["flow_handling"].append({
                    "test_id": test_id,
                    "differences": flow_diff
                })
            
            # 分析错误处理差异
            error_diff = self._compare_error_handling(controller_results)
            if error_diff:
                differences["error_handling"].append({
                    "test_id": test_id,
                    "differences": error_diff
                })
        
        return differences
    
    def _analyze_security_aspects(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析安全性方面"""
        security_analysis = {
            "vulnerability_detection": [],
            "error_handling_security": [],
            "input_validation": []
        }
        
        for result in results:
            if result["test_id"].startswith("security_"):
                self._analyze_security_test_result(
                    result,
                    security_analysis
                )
        
        return security_analysis
    
    def _generate_performance_charts(self, performance_data: Dict[str, Any]):
        """生成性能图表"""
        # 响应时间分布图
        plt.figure(figsize=(10, 6))
        for controller, times in performance_data["response_times"].items():
            sns.kdeplot(data=times, label=controller)
        plt.title("Response Time Distribution")
        plt.xlabel("Time (ms)")
        plt.ylabel("Density")
        plt.legend()
        plt.savefig(self.results_dir / "response_time_distribution.png")
        plt.close()
        
        # 箱线图
        plt.figure(figsize=(10, 6))
        data = []
        labels = []
        for controller, times in performance_data["response_times"].items():
            data.extend(times)
            labels.extend([controller] * len(times))
        df = pd.DataFrame({"Controller": labels, "Response Time": data})
        sns.boxplot(x="Controller", y="Response Time", data=df)
        plt.title("Response Time Comparison")
        plt.savefig(self.results_dir / "response_time_boxplot.png")
        plt.close()
    
    def _generate_report(self):
        """生成分析报告"""
        report = {
            "summary": self._generate_summary(),
            "detailed_analysis": self.analysis_results,
            "recommendations": self._generate_recommendations()
        }
        
        # 保存JSON报告
        with open(self.results_dir / "analysis_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # 生成HTML报告
        self._generate_html_report(report)
    
    def _generate_html_report(self, report: Dict[str, Any]):
        """生成HTML格式的报告"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>DHR Test Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .section {{ margin-bottom: 20px; }}
                .chart {{ margin: 10px 0; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>DHR Test Analysis Report</h1>
            <div class="section">
                <h2>Summary</h2>
                {self._format_summary_html(report["summary"])}
            </div>
            <div class="section">
                <h2>Performance Analysis</h2>
                <img src="response_time_distribution.png" class="chart">
                <img src="response_time_boxplot.png" class="chart">
            </div>
            <div class="section">
                <h2>Recommendations</h2>
                {self._format_recommendations_html(report["recommendations"])}
            </div>
        </body>
        </html>
        """
        
        with open(self.results_dir / "analysis_report.html", "w") as f:
            f.write(html_content)
    
    def _generate_summary(self) -> Dict[str, Any]:
        """生成总结"""
        basic_stats = self.analysis_results["basic_stats"]
        return {
            "test_coverage": {
                "total_tests": basic_stats["total_tests"],
                "success_rates": basic_stats["success_rate"]
            },
            "key_findings": self._extract_key_findings(),
            "performance_summary": self._summarize_performance()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """生成建议"""
        recommendations = []
        
        # 基于性能分析的建议
        performance = self.analysis_results["performance"]
        for controller, times in performance["response_times"].items():
            avg_time = sum(times) / len(times)
            if avg_time > 100:  # 100ms阈值
                recommendations.append(
                    f"Consider optimizing {controller} controller's response time"
                )
        
        # 基于行为差异的建议
        behavior = self.analysis_results["behavior"]
        if len(behavior["flow_handling"]) > 0:
            recommendations.append(
                "Standardize flow handling across controllers"
            )
        
        # 基于安全性分析的建议
        security = self.analysis_results["security"]
        if len(security["vulnerability_detection"]) > 0:
            recommendations.append(
                "Enhance security measures for detected vulnerabilities"
            )
        
        return recommendations 