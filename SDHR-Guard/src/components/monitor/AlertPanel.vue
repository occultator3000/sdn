<template>
  <div class="alert-panel">
    <el-card class="alert-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="title">告警面板</span>
            <el-tag 
              v-if="activeAlerts.length > 0"
              :type="getAlertLevelType(highestSeverity)"
              effect="dark"
            >
              {{ activeAlerts.length }} 个活跃告警
            </el-tag>
          </div>
          <div class="header-right">
            <el-button-group>
              <el-button 
                type="primary" 
                :icon="Refresh"
                @click="refreshAlerts"
              >
                刷新
              </el-button>
              <el-button 
                type="danger" 
                :icon="Bell"
                :disabled="!hasUnacknowledged"
                @click="acknowledgeAll"
              >
                确认全部
              </el-button>
            </el-button-group>
          </div>
        </div>
      </template>
      
      <!-- 告警统计 -->
      <el-row :gutter="20" class="alert-stats">
        <el-col :span="6" v-for="level in alertLevels" :key="level.value">
          <div class="stat-card" :class="level.value">
            <div class="stat-icon">
              <el-icon :size="24">
                <component :is="level.icon" />
              </el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ getAlertCount(level.value) }}</div>
              <div class="stat-label">{{ level.label }}</div>
            </div>
          </div>
        </el-col>
      </el-row>
      
      <!-- 告警过滤器 -->
      <div class="alert-filters">
        <el-form :inline="true" :model="filterForm">
          <el-form-item label="严重性">
            <el-select v-model="filterForm.severity" multiple collapse-tags>
              <el-option
                v-for="level in alertLevels"
                :key="level.value"
                :label="level.label"
                :value="level.value"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="filterForm.status" multiple collapse-tags>
              <el-option label="未确认" value="unacknowledged" />
              <el-option label="已确认" value="acknowledged" />
              <el-option label="已解决" value="resolved" />
            </el-select>
          </el-form-item>
          <el-form-item label="来源">
            <el-select v-model="filterForm.source" multiple collapse-tags>
              <el-option
                v-for="source in alertSources"
                :key="source"
                :label="source"
                :value="source"
              />
            </el-select>
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 告警列表 -->
      <el-table
        :data="filteredAlerts"
        style="width: 100%"
        :max-height="500"
        @row-click="handleAlertClick"
      >
        <el-table-column type="expand">
          <template #default="props">
            <div class="alert-detail">
              <pre>{{ JSON.stringify(props.row.details, null, 2) }}</pre>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="timestamp" label="时间" width="180">
          <template #default="scope">
            {{ formatTime(scope.row.timestamp) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="severity" label="严重性" width="100">
          <template #default="scope">
            <el-tag
              :type="getAlertLevelType(scope.row.severity)"
              effect="dark"
            >
              {{ scope.row.severity }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="source" label="来源" width="150" />
        
        <el-table-column prop="message" label="描述" />
        
        <el-table-column prop="status" label="状态" width="120">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusLabel(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button-group>
              <el-button
                size="small"
                :type="scope.row.status === 'unacknowledged' ? 'primary' : 'info'"
                :disabled="scope.row.status !== 'unacknowledged'"
                @click.stop="acknowledgeAlert(scope.row)"
              >
                确认
              </el-button>
              <el-button
                size="small"
                type="success"
                :disabled="scope.row.status === 'resolved'"
                @click.stop="resolveAlert(scope.row)"
              >
                解决
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { format } from 'date-fns'
import {
  Refresh,
  Bell,
  Warning,
  InfoFilled,
  CircleCheckFilled,
  CircleCloseFilled
} from '@element-plus/icons-vue'

export default {
  name: 'AlertPanel',
  
  components: {
    Refresh,
    Bell,
    Warning,
    InfoFilled,
    CircleCheckFilled,
    CircleCloseFilled
  },
  
  setup() {
    const store = useStore()
    
    // 过滤表单
    const filterForm = ref({
      severity: [],
      status: [],
      source: []
    })
    
    // 告警级别定义
    const alertLevels = [
      { 
        value: 'critical', 
        label: '严重', 
        icon: CircleCloseFilled,
        color: '#F56C6C' 
      },
      { 
        value: 'warning', 
        label: '警告', 
        icon: Warning,
        color: '#E6A23C' 
      },
      { 
        value: 'info', 
        label: '信息', 
        icon: InfoFilled,
        color: '#409EFF' 
      },
      { 
        value: 'success', 
        label: '正常', 
        icon: CircleCheckFilled,
        color: '#67C23A' 
      }
    ]
    
    // 计算属性
    const alerts = computed(() => store.state.monitor.alerts)
    
    const activeAlerts = computed(() => 
      alerts.value.filter(alert => alert.status !== 'resolved')
    )
    
    const filteredAlerts = computed(() => {
      return alerts.value.filter(alert => {
        const severityMatch = filterForm.value.severity.length === 0 || 
          filterForm.value.severity.includes(alert.severity)
        const statusMatch = filterForm.value.status.length === 0 || 
          filterForm.value.status.includes(alert.status)
        const sourceMatch = filterForm.value.source.length === 0 || 
          filterForm.value.source.includes(alert.source)
        return severityMatch && statusMatch && sourceMatch
      })
    })
    
    const highestSeverity = computed(() => {
      const severityOrder = ['critical', 'warning', 'info', 'success']
      return activeAlerts.value.reduce((highest, alert) => {
        const currentIndex = severityOrder.indexOf(alert.severity)
        const highestIndex = severityOrder.indexOf(highest)
        return currentIndex < highestIndex ? alert.severity : highest
      }, 'success')
    })
    
    const hasUnacknowledged = computed(() =>
      alerts.value.some(alert => alert.status === 'unacknowledged')
    )
    
    const alertSources = computed(() => {
      const sources = new Set(alerts.value.map(alert => alert.source))
      return Array.from(sources)
    })
    
    // 方法
    const refreshAlerts = async () => {
      try {
        await store.dispatch('monitor/fetchAlerts')
      } catch (error) {
        console.error('Failed to refresh alerts:', error)
      }
    }
    
    const acknowledgeAlert = async (alert) => {
      try {
        await store.dispatch('monitor/acknowledgeAlert', alert.id)
      } catch (error) {
        console.error('Failed to acknowledge alert:', error)
      }
    }
    
    const resolveAlert = async (alert) => {
      try {
        await store.dispatch('monitor/resolveAlert', alert.id)
      } catch (error) {
        console.error('Failed to resolve alert:', error)
      }
    }
    
    const acknowledgeAll = async () => {
      try {
        const unacknowledgedAlerts = alerts.value
          .filter(alert => alert.status === 'unacknowledged')
          .map(alert => alert.id)
        await store.dispatch('monitor/acknowledgeAlerts', unacknowledgedAlerts)
      } catch (error) {
        console.error('Failed to acknowledge all alerts:', error)
      }
    }
    
    const handleAlertClick = (row) => {
      // 处理告警点击事件，可以显示详细信息
    }
    
    const getAlertCount = (severity) => {
      return alerts.value.filter(alert => 
        alert.severity === severity && alert.status !== 'resolved'
      ).length
    }
    
    // 辅助函数
    const getAlertLevelType = (severity) => {
      const types = {
        critical: 'danger',
        warning: 'warning',
        info: 'info',
        success: 'success'
      }
      return types[severity] || 'info'
    }
    
    const getStatusType = (status) => {
      const types = {
        unacknowledged: 'danger',
        acknowledged: 'warning',
        resolved: 'success'
      }
      return types[status] || 'info'
    }
    
    const getStatusLabel = (status) => {
      const labels = {
        unacknowledged: '未确认',
        acknowledged: '已确认',
        resolved: '已解决'
      }
      return labels[status] || status
    }
    
    const formatTime = (timestamp) => {
      return format(new Date(timestamp), 'yyyy-MM-dd HH:mm:ss')
    }
    
    // 生命周期钩子
    onMounted(() => {
      refreshAlerts()
    })
    
    return {
      filterForm,
      alertLevels,
      alerts,
      activeAlerts,
      filteredAlerts,
      highestSeverity,
      hasUnacknowledged,
      alertSources,
      refreshAlerts,
      acknowledgeAlert,
      resolveAlert,
      acknowledgeAll,
      handleAlertClick,
      getAlertCount,
      getAlertLevelType,
      getStatusType,
      getStatusLabel,
      formatTime,
      // 图标组件
      Refresh,
      Bell
    }
  }
}
</script>

<style scoped>
.alert-panel {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.alert-stats {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 15px;
  border-radius: 4px;
  color: white;
}

.stat-card.critical {
  background-color: #F56C6C;
}

.stat-card.warning {
  background-color: #E6A23C;
}

.stat-card.info {
  background-color: #409EFF;
}

.stat-card.success {
  background-color: #67C23A;
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
  font-size: 14px;
  opacity: 0.8;
}

.alert-filters {
  margin: 20px 0;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.alert-detail {
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.alert-detail pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style> 