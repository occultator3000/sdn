<template>
  <div class="scheduler-view">
    <el-card class="scheduler-card">
      <template #header>
        <div class="card-header">
          <span>调度器状态</span>
          <el-button-group>
            <el-button 
              type="primary" 
              :disabled="!canChangeStrategy"
              @click="changeStrategy"
            >
              切换策略
            </el-button>
            <el-button 
              type="warning"
              @click="forceSchedule"
            >
              强制调度
            </el-button>
          </el-button-group>
        </div>
      </template>
      
      <!-- 当前策略信息 -->
      <div class="strategy-info">
        <div class="info-item">
          <span class="label">当前策略:</span>
          <el-tag :type="getStrategyType(currentStrategy)">
            {{ getStrategyName(currentStrategy) }}
          </el-tag>
        </div>
        <div class="info-item">
          <span class="label">运行时间:</span>
          <span>{{ formatDuration(runningTime) }}</span>
        </div>
        <div class="info-item">
          <span class="label">切换次数:</span>
          <span>{{ switchCount }}</span>
        </div>
      </div>
      
      <!-- 性能指标 -->
      <div class="performance-metrics">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-card shadow="hover">
              <template #header>
                <div class="metric-header">系统负载</div>
              </template>
              <el-progress
                type="dashboard"
                :percentage="systemLoad"
                :color="getLoadColor"
              />
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card shadow="hover">
              <template #header>
                <div class="metric-header">异构度</div>
              </template>
              <el-progress
                type="dashboard"
                :percentage="diversityScore * 100"
                :color="getDiversityColor"
              />
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card shadow="hover">
              <template #header>
                <div class="metric-header">健康度</div>
              </template>
              <el-progress
                type="dashboard"
                :percentage="healthScore * 100"
                :color="getHealthColor"
              />
            </el-card>
          </el-col>
        </el-row>
      </div>
      
      <!-- 策略性能历史 -->
      <div class="strategy-history">
        <div class="chart-container">
          <v-chart :option="chartOption" autoresize />
        </div>
      </div>
      
      <!-- 调度日志 -->
      <div class="schedule-logs">
        <el-table :data="scheduleLogs" height="250">
          <el-table-column prop="timestamp" label="时间" width="180">
            <template #default="scope">
              {{ formatTime(scope.row.timestamp) }}
            </template>
          </el-table-column>
          <el-table-column prop="strategy" label="策略" width="120">
            <template #default="scope">
              <el-tag :type="getStrategyType(scope.row.strategy)">
                {{ getStrategyName(scope.row.strategy) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="action" label="操作" width="120" />
          <el-table-column prop="result" label="结果">
            <template #default="scope">
              <el-tag :type="scope.row.success ? 'success' : 'danger'">
                {{ scope.row.success ? '成功' : '失败' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>
    
    <!-- 切换策略对话框 -->
    <el-dialog
      v-model="strategyDialogVisible"
      title="切换调度策略"
      width="400px"
    >
      <el-form :model="newStrategy" label-width="100px">
        <el-form-item label="调度策略">
          <el-select v-model="newStrategy.type">
            <el-option 
              v-for="strategy in availableStrategies"
              :key="strategy.value"
              :label="strategy.label"
              :value="strategy.value"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="strategyDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmStrategyChange">
            确认
          </el-button>
        </span>
      </template>
    </el-dialog>
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
  LegendComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import { format } from 'date-fns'

use([
  CanvasRenderer,
  LineChart,
  GridComponent,
  TooltipComponent,
  LegendComponent
])

export default {
  name: 'SchedulerView',
  
  components: {
    VChart
  },
  
  setup() {
    const store = useStore()
    const strategyDialogVisible = ref(false)
    const newStrategy = ref({ type: 'health_aware' })
    const scheduleLogs = ref([])
    const updateInterval = ref(null)
    
    // 计算属性
    const currentStrategy = computed(() => 
      store.state.dhr.currentStrategy
    )
    
    const systemLoad = computed(() => 
      store.state.dhr.systemMetrics.load_level * 100
    )
    
    const diversityScore = computed(() => 
      store.state.dhr.systemMetrics.diversity_score
    )
    
    const healthScore = computed(() => 
      store.state.dhr.systemMetrics.health_score
    )
    
    const chartOption = computed(() => ({
      tooltip: {
        trigger: 'axis'
      },
      legend: {
        data: ['系统负载', '异构度', '健康度']
      },
      xAxis: {
        type: 'time',
        boundaryGap: false
      },
      yAxis: {
        type: 'value',
        min: 0,
        max: 100
      },
      series: [
        {
          name: '系统负载',
          type: 'line',
          data: store.state.dhr.metrics.loadHistory
        },
        {
          name: '异构度',
          type: 'line',
          data: store.state.dhr.metrics.diversityHistory
        },
        {
          name: '健康度',
          type: 'line',
          data: store.state.dhr.metrics.healthHistory
        }
      ]
    }))
    
    // 方法
    const updateMetrics = async () => {
      await store.dispatch('dhr/updateMetrics')
    }
    
    const changeStrategy = () => {
      strategyDialogVisible.value = true
    }
    
    const confirmStrategyChange = async () => {
      try {
        await store.dispatch('dhr/changeStrategy', newStrategy.value.type)
        strategyDialogVisible.value = false
      } catch (error) {
        console.error('Failed to change strategy:', error)
      }
    }
    
    const forceSchedule = async () => {
      try {
        await store.dispatch('dhr/forceSchedule')
      } catch (error) {
        console.error('Failed to force schedule:', error)
      }
    }
    
    // 辅助函数
    const formatTime = (timestamp) => {
      return format(new Date(timestamp), 'yyyy-MM-dd HH:mm:ss')
    }
    
    const formatDuration = (seconds) => {
      const hours = Math.floor(seconds / 3600)
      const minutes = Math.floor((seconds % 3600) / 60)
      const secs = seconds % 60
      return `${hours}h ${minutes}m ${secs}s`
    }
    
    const getStrategyName = (strategy) => {
      const names = {
        round_robin: '轮询',
        health_aware: '健康感知',
        diversity_aware: '异构感知'
      }
      return names[strategy] || strategy
    }
    
    const getStrategyType = (strategy) => {
      const types = {
        round_robin: 'info',
        health_aware: 'success',
        diversity_aware: 'warning'
      }
      return types[strategy] || 'info'
    }
    
    // 生命周期钩子
    onMounted(() => {
      updateMetrics()
      updateInterval.value = setInterval(updateMetrics, 5000)
    })
    
    onUnmounted(() => {
      if (updateInterval.value) {
        clearInterval(updateInterval.value)
      }
    })
    
    return {
      currentStrategy,
      systemLoad,
      diversityScore,
      healthScore,
      chartOption,
      scheduleLogs,
      strategyDialogVisible,
      newStrategy,
      changeStrategy,
      confirmStrategyChange,
      forceSchedule,
      formatTime,
      formatDuration,
      getStrategyName,
      getStrategyType
    }
  }
}
</script>

<style scoped>
.scheduler-view {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.strategy-info {
  margin-bottom: 20px;
}

.info-item {
  display: flex;
  align-items: center;
  margin: 10px 0;
}

.info-item .label {
  width: 100px;
  color: #606266;
}

.performance-metrics {
  margin: 20px 0;
}

.metric-header {
  text-align: center;
  font-weight: bold;
}

.chart-container {
  height: 300px;
  margin: 20px 0;
}

.schedule-logs {
  margin-top: 20px;
}
</style> 