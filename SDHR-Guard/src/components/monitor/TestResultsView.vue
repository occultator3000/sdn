<template>
  <div class="test-results-view">
    <el-card class="results-card">
      <template #header>
        <div class="card-header">
          <span>测试结果分析</span>
          <el-button-group>
            <el-button 
              type="primary"
              @click="refreshResults"
              :loading="loading"
            >
              刷新
            </el-button>
            <el-button 
              type="success"
              @click="exportReport"
            >
              导出报告
            </el-button>
          </el-button-group>
        </div>
      </template>
      
      <!-- 测试概览 -->
      <el-row :gutter="20" class="overview-section">
        <el-col :span="8" v-for="stat in overviewStats" :key="stat.label">
          <div class="stat-card">
            <div class="stat-icon">
              <el-icon :size="24">
                <component :is="stat.icon" />
              </el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-label">{{ stat.label }}</div>
            </div>
          </div>
        </el-col>
      </el-row>
      
      <!-- 性能分析图表 -->
      <div class="charts-section">
        <el-tabs v-model="activeChart">
          <el-tab-pane label="响应时间分布" name="response-time">
            <div class="chart-container">
              <v-chart :option="responseTimeChartOption" autoresize />
            </div>
          </el-tab-pane>
          <el-tab-pane label="控制器对比" name="controller-comparison">
            <div class="chart-container">
              <v-chart :option="comparisonChartOption" autoresize />
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
      
      <!-- 差异分析 -->
      <div class="difference-section">
        <h3>控制器差异分析</h3>
        <el-table :data="differenceAnalysis" height="300">
          <el-table-column prop="type" label="类型" width="120">
            <template #default="scope">
              <el-tag :type="getDifferenceType(scope.row.type)">
                {{ scope.row.type }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="controllers" label="相关控制器" width="200" />
          <el-table-column prop="description" label="差异描述" />
          <el-table-column prop="impact" label="影响程度" width="120">
            <template #default="scope">
              <el-progress
                :percentage="scope.row.impact * 100"
                :status="getImpactStatus(scope.row.impact)"
              />
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <!-- 安全分析 -->
      <div class="security-section">
        <h3>安全性分析</h3>
        <el-collapse v-model="activeSecurityItems">
          <el-collapse-item
            v-for="item in securityAnalysis"
            :key="item.category"
            :title="item.category"
            :name="item.category"
          >
            <div class="security-item">
              <div class="security-score">
                <el-progress
                  type="dashboard"
                  :percentage="item.score * 100"
                  :color="getSecurityColor(item.score)"
                />
              </div>
              <div class="security-details">
                <div v-for="detail in item.details" :key="detail.id">
                  <el-alert
                    :title="detail.title"
                    :type="detail.level"
                    :description="detail.description"
                    show-icon
                  />
                </div>
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
      
      <!-- 建议 -->
      <div class="recommendations-section">
        <h3>优化建议</h3>
        <el-timeline>
          <el-timeline-item
            v-for="(recommendation, index) in recommendations"
            :key="index"
            :type="recommendation.type"
            :timestamp="recommendation.timestamp"
          >
            {{ recommendation.content }}
          </el-timeline-item>
        </el-timeline>
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  DataZoomComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import {
  CircleCheckFilled,
  Warning,
  DataLine
} from '@element-plus/icons-vue'

use([
  CanvasRenderer,
  LineChart,
  BarChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  DataZoomComponent
])

export default {
  name: 'TestResultsView',
  
  components: {
    VChart,
    CircleCheckFilled,
    Warning,
    DataLine
  },
  
  setup() {
    const store = useStore()
    const loading = ref(false)
    const activeChart = ref('response-time')
    const activeSecurityItems = ref(['vulnerability'])
    
    // 概览统计
    const overviewStats = computed(() => [
      {
        label: '测试用例总数',
        value: store.state.test.totalTests,
        icon: 'DataLine'
      },
      {
        label: '成功率',
        value: `${(store.state.test.successRate * 100).toFixed(1)}%`,
        icon: 'CircleCheckFilled'
      },
      {
        label: '发现差异',
        value: store.state.test.differences.length,
        icon: 'Warning'
      }
    ])
    
    // 响应时间分布图配置
    const responseTimeChartOption = computed(() => ({
      tooltip: {
        trigger: 'axis'
      },
      legend: {
        data: ['RYU', 'POX', 'OpenDaylight']
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: store.state.test.timeLabels
      },
      yAxis: {
        type: 'value',
        name: '响应时间 (ms)'
      },
      series: [
        {
          name: 'RYU',
          type: 'line',
          smooth: true,
          data: store.state.test.ryuResponseTimes
        },
        {
          name: 'POX',
          type: 'line',
          smooth: true,
          data: store.state.test.poxResponseTimes
        },
        {
          name: 'OpenDaylight',
          type: 'line',
          smooth: true,
          data: store.state.test.odlResponseTimes
        }
      ]
    }))
    
    // 控制器对比图配置
    const comparisonChartOption = computed(() => ({
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      legend: {
        data: ['成功率', '性能分数', '安全分数']
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: ['RYU', 'POX', 'OpenDaylight']
      },
      yAxis: {
        type: 'value',
        max: 100
      },
      series: [
        {
          name: '成功率',
          type: 'bar',
          data: store.state.test.successRates
        },
        {
          name: '性能分数',
          type: 'bar',
          data: store.state.test.performanceScores
        },
        {
          name: '安全分数',
          type: 'bar',
          data: store.state.test.securityScores
        }
      ]
    }))
    
    // 差异分析数据
    const differenceAnalysis = computed(() => 
      store.state.test.differences.map(diff => ({
        type: diff.type,
        controllers: diff.controllers.join(' vs '),
        description: diff.description,
        impact: diff.impact
      }))
    )
    
    // 安全性分析数据
    const securityAnalysis = computed(() => [
      {
        category: '漏洞检测',
        score: store.state.test.securityMetrics.vulnerability,
        details: store.state.test.vulnerabilityDetails
      },
      {
        category: '错误处理',
        score: store.state.test.securityMetrics.errorHandling,
        details: store.state.test.errorHandlingDetails
      },
      {
        category: '输入验证',
        score: store.state.test.securityMetrics.inputValidation,
        details: store.state.test.inputValidationDetails
      }
    ])
    
    // 优化建议
    const recommendations = computed(() => 
      store.state.test.recommendations.map(rec => ({
        content: rec.content,
        type: rec.priority,
        timestamp: rec.timestamp
      }))
    )
    
    // 方法
    const refreshResults = async () => {
      loading.value = true
      try {
        await store.dispatch('test/fetchResults')
      } catch (error) {
        console.error('Failed to fetch test results:', error)
      } finally {
        loading.value = false
      }
    }
    
    const exportReport = async () => {
      try {
        await store.dispatch('test/exportReport')
      } catch (error) {
        console.error('Failed to export report:', error)
      }
    }
    
    // 辅助函数
    const getDifferenceType = (type) => {
      const types = {
        'flow': 'warning',
        'performance': 'info',
        'security': 'danger'
      }
      return types[type] || 'info'
    }
    
    const getImpactStatus = (impact) => {
      if (impact >= 0.8) return 'exception'
      if (impact >= 0.5) return 'warning'
      return 'success'
    }
    
    const getSecurityColor = (score) => {
      if (score >= 0.8) return '#67C23A'
      if (score >= 0.6) return '#E6A23C'
      return '#F56C6C'
    }
    
    // 生命周期钩子
    onMounted(() => {
      refreshResults()
    })
    
    return {
      loading,
      activeChart,
      activeSecurityItems,
      overviewStats,
      responseTimeChartOption,
      comparisonChartOption,
      differenceAnalysis,
      securityAnalysis,
      recommendations,
      refreshResults,
      exportReport,
      getDifferenceType,
      getImpactStatus,
      getSecurityColor
    }
  }
}
</script>

<style scoped>
.test-results-view {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.overview-section {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.stat-icon {
  margin-right: 15px;
}

.stat-info {
  flex-grow: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
}

.stat-label {
  color: #909399;
  font-size: 14px;
}

.chart-container {
  height: 400px;
  margin: 20px 0;
}

.difference-section,
.security-section,
.recommendations-section {
  margin-top: 20px;
}

.security-item {
  display: flex;
  align-items: flex-start;
  gap: 20px;
}

.security-score {
  width: 200px;
}

.security-details {
  flex-grow: 1;
}
</style> 