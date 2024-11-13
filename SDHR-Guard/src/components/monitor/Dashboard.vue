<template>
  <div class="monitor-dashboard">
    <el-row :gutter="20">
      <!-- 系统概览 -->
      <el-col :span="24">
        <el-card class="overview-card">
          <template #header>
            <div class="card-header">
              <span>系统概览</span>
              <el-button-group>
                <el-button 
                  :type="autoRefresh ? 'success' : 'info'"
                  @click="toggleAutoRefresh"
                >
                  {{ autoRefresh ? '自动刷新中' : '开启自动刷新' }}
                </el-button>
                <el-button type="primary" @click="refreshData">
                  刷新
                </el-button>
              </el-button-group>
            </div>
          </template>
          
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="stat-card">
                <div class="stat-title">控制器数量</div>
                <div class="stat-value">{{ stats.controllerCount }}</div>
                <div class="stat-footer">
                  活跃: {{ stats.activeControllers }}
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-card">
                <div class="stat-title">总流表数</div>
                <div class="stat-value">{{ stats.totalFlows }}</div>
                <div class="stat-footer">
                  活跃: {{ stats.activeFlows }}
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-card">
                <div class="stat-title">系统健康度</div>
                <div class="stat-value">
                  {{ (stats.systemHealth * 100).toFixed(1) }}%
                </div>
                <div class="stat-footer">
                  <el-progress 
                    :percentage="stats.systemHealth * 100"
                    :status="getHealthStatus(stats.systemHealth)"
                  />
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-card">
                <div class="stat-title">告警数量</div>
                <div class="stat-value">{{ stats.alertCount }}</div>
                <div class="stat-footer">
                  严重: {{ stats.criticalAlerts }}
                </div>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
      
      <!-- 性能监控图表 -->
      <el-col :span="16">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>性能监控</span>
              <el-select v-model="selectedMetric" size="small">
                <el-option 
                  v-for="metric in availableMetrics"
                  :key="metric.value"
                  :label="metric.label"
                  :value="metric.value"
                />
              </el-select>
            </div>
          </template>
          <div class="chart-container">
            <v-chart :option="chartOption" autoresize />
          </div>
        </el-card>
      </el-col>
      
      <!-- 控制器状态 -->
      <el-col :span="8">
        <el-card class="controllers-card">
          <template #header>
            <div class="card-header">
              <span>控制器状态</span>
            </div>
          </template>
          <div class="controller-list">
            <div 
              v-for="controller in controllers"
              :key="controller.id"
              class="controller-item"
            >
              <div class="controller-info">
                <div class="controller-name">
                  {{ controller.name }}
                  <el-tag 
                    size="small"
                    :type="getControllerStatusType(controller.status)"
                  >
                    {{ controller.status }}
                  </el-tag>
                </div>
                <div class="controller-metrics">
                  <div class="metric">
                    <span class="label">负载:</span>
                    <el-progress 
                      :percentage="controller.load * 100"
                      :color="getLoadColor(controller.load)"
                      :show-text="false"
                      :stroke-width="4"
                    />
                  </div>
                  <div class="metric">
                    <span class="label">延迟:</span>
                    <span>{{ controller.latency }}ms</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <!-- 最近事件 -->
      <el-col :span="24">
        <el-card class="events-card">
          <template #header>
            <div class="card-header">
              <span>最近事件</span>
              <el-button 
                type="text"
                @click="showAllEvents"
              >
                查看全部
              </el-button>
            </div>
          </template>
          <el-table :data="recentEvents" height="250">
            <el-table-column prop="timestamp" label="时间" width="180">
              <template #default="scope">
                {{ formatTime(scope.row.timestamp) }}
              </template>
            </el-table-column>
            <el-table-column prop="type" label="类型" width="120">
              <template #default="scope">
                <el-tag :type="getEventType(scope.row.type)">
                  {{ scope.row.type }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="source" label="来源" width="150" />
            <el-table-column prop="message" label="描述" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="scope">
                <el-tag :type="getStatusType(scope.row.status)">
                  {{ scope.row.status }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useStore } from 'vuex'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  DataZoomComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import { format } from 'date-fns'

use([
  CanvasRenderer,
  LineChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  DataZoomComponent
])

export default {
  name: 'MonitorDashboard',
  
  components: {
    VChart
  },
  
  setup() {
    const store = useStore()
    const autoRefresh = ref(true)
    const refreshInterval = ref(null)
    const selectedMetric = ref('load')
    
    // 可用的监控指标
    const availableMetrics = [
      { label: '系统负载', value: 'load' },
      { label: '响应时间', value: 'latency' },
      { label: '流表数量', value: 'flows' },
      { label: '错误率', value: 'errors' }
    ]
    
    // 系统统计数据
    const stats = computed(() => ({
      controllerCount: store.state.dhr.controllers.length,
      activeControllers: store.state.dhr.controllers.filter(c => c.status === 'active').length,
      totalFlows: store.getters['dhr/totalFlows'],
      activeFlows: store.getters['dhr/activeFlows'],
      systemHealth: store.state.dhr.systemMetrics.health_score,
      alertCount: store.state.monitor.alerts.length,
      criticalAlerts: store.state.monitor.alerts.filter(a => a.severity === 'critical').length
    }))
    
    // 控制器列表
    const controllers = computed(() => 
      store.state.dhr.controllers.map(c => ({
        ...c,
        load: store.getters['dhr/controllerLoad'](c.id),
        latency: store.getters['dhr/controllerLatency'](c.id)
      }))
    )
    
    // 最近事件
    const recentEvents = computed(() => 
      store.state.monitor.events.slice(0, 10)
    )
    
    // 图表配置
    const chartOption = computed(() => ({
      tooltip: {
        trigger: 'axis',
        formatter: (params) => {
          const time = format(new Date(params[0].value[0]), 'HH:mm:ss')
          const values = params.map(p => 
            `${p.seriesName}: ${p.value[1].toFixed(2)}`
          ).join('<br/>')
          return `${time}<br/>${values}`
        }
      },
      legend: {
        data: controllers.value.map(c => c.name)
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'time',
        boundaryGap: false
      },
      yAxis: {
        type: 'value',
        name: getMetricName(selectedMetric.value)
      },
      dataZoom: [
        {
          type: 'inside',
          start: 0,
          end: 100
        },
        {
          start: 0,
          end: 100
        }
      ],
      series: controllers.value.map(controller => ({
        name: controller.name,
        type: 'line',
        smooth: true,
        data: getMetricData(controller.id, selectedMetric.value)
      }))
    }))
    
    // 方法
    const refreshData = async () => {
      try {
        await Promise.all([
          store.dispatch('dhr/updateControllers'),
          store.dispatch('dhr/updateMetrics'),
          store.dispatch('monitor/updateEvents')
        ])
      } catch (error) {
        console.error('Failed to refresh data:', error)
      }
    }
    
    const toggleAutoRefresh = () => {
      autoRefresh.value = !autoRefresh.value
      if (autoRefresh.value) {
        refreshInterval.value = setInterval(refreshData, 5000)
      } else if (refreshInterval.value) {
        clearInterval(refreshInterval.value)
      }
    }
    
    const showAllEvents = () => {
      // 实现查看所有事件的逻辑
    }
    
    // 辅助函数
    const getMetricName = (metric) => {
      const names = {
        load: '负载 (%)',
        latency: '响应时间 (ms)',
        flows: '流表数量',
        errors: '错误率 (%)'
      }
      return names[metric] || metric
    }
    
    const getMetricData = (controllerId, metric) => {
      return store.getters['dhr/controllerMetricHistory'](controllerId, metric)
    }
    
    const getHealthStatus = (score) => {
      if (score >= 0.8) return 'success'
      if (score >= 0.6) return 'warning'
      return 'exception'
    }
    
    const getControllerStatusType = (status) => {
      const types = {
        active: 'success',
        inactive: 'info',
        error: 'danger'
      }
      return types[status] || 'info'
    }
    
    const getLoadColor = (load) => {
      if (load < 0.7) return '#67C23A'
      if (load < 0.9) return '#E6A23C'
      return '#F56C6C'
    }
    
    const getEventType = (type) => {
      const types = {
        info: 'info',
        warning: 'warning',
        error: 'danger',
        success: 'success'
      }
      return types[type] || 'info'
    }
    
    const formatTime = (timestamp) => {
      return format(new Date(timestamp), 'yyyy-MM-dd HH:mm:ss')
    }
    
    // 生命周期钩子
    onMounted(() => {
      refreshData()
      if (autoRefresh.value) {
        refreshInterval.value = setInterval(refreshData, 5000)
      }
    })
    
    onUnmounted(() => {
      if (refreshInterval.value) {
        clearInterval(refreshInterval.value)
      }
    })
    
    return {
      stats,
      controllers,
      recentEvents,
      autoRefresh,
      selectedMetric,
      availableMetrics,
      chartOption,
      refreshData,
      toggleAutoRefresh,
      showAllEvents,
      getHealthStatus,
      getControllerStatusType,
      getLoadColor,
      getEventType,
      formatTime
    }
  }
}
</script>

<style scoped>
.monitor-dashboard {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-card {
  padding: 20px;
  text-align: center;
  background: #f8f9fa;
  border-radius: 4px;
}

.stat-title {
  color: #606266;
  font-size: 14px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  margin: 10px 0;
}

.stat-footer {
  font-size: 12px;
  color: #909399;
}

.chart-container {
  height: 400px;
}

.controller-list {
  max-height: 400px;
  overflow-y: auto;
}

.controller-item {
  padding: 10px;
  border-bottom: 1px solid #ebeef5;
}

.controller-item:last-child {
  border-bottom: none;
}

.controller-name {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.controller-metrics {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.metric {
  display: flex;
  align-items: center;
  gap: 10px;
}

.metric .label {
  width: 50px;
  color: #909399;
}
</style> 