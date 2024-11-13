<template>
  <div class="controller-pool">
    <el-card class="controller-list">
      <template #header>
        <div class="card-header">
          <span>控制器池</span>
          <el-button type="primary" @click="addController">添加控制器</el-button>
        </div>
      </template>
      
      <!-- 控制器列表 -->
      <div class="controllers">
        <el-card 
          v-for="controller in controllers" 
          :key="controller.id"
          :class="['controller-card', controller.status]"
        >
          <div class="controller-header">
            <span class="controller-name">{{ controller.name }}</span>
            <el-tag :type="getStatusType(controller.status)">
              {{ controller.status }}
            </el-tag>
          </div>
          
          <!-- 控制器指标 -->
          <div class="controller-metrics">
            <div class="metric-item">
              <span class="label">健康分数</span>
              <el-progress 
                :percentage="controller.healthScore * 100"
                :status="getHealthStatus(controller.healthScore)"
              />
            </div>
            <div class="metric-item">
              <span class="label">流表数量</span>
              <span class="value">{{ controller.flowCount }}</span>
            </div>
            <div class="metric-item">
              <span class="label">响应时间</span>
              <span class="value">{{ controller.responseTime }}ms</span>
            </div>
          </div>
          
          <!-- 控制器操作 -->
          <div class="controller-actions">
            <el-button-group>
              <el-button 
                type="primary" 
                :disabled="controller.status !== 'inactive'"
                @click="startController(controller.id)"
              >
                启动
              </el-button>
              <el-button 
                type="danger" 
                :disabled="controller.status !== 'active'"
                @click="stopController(controller.id)"
              >
                停止
              </el-button>
              <el-button 
                type="warning"
                @click="showDetails(controller)"
              >
                详情
              </el-button>
            </el-button-group>
          </div>
        </el-card>
      </div>
    </el-card>
    
    <!-- 添加控制器对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="添加控制器"
      width="500px"
    >
      <el-form :model="newController" label-width="100px">
        <el-form-item label="控制器类型">
          <el-select v-model="newController.type">
            <el-option label="POX" value="pox" />
            <el-option label="RYU" value="ryu" />
            <el-option label="OpenDaylight" value="odl" />
          </el-select>
        </el-form-item>
        <el-form-item label="控制器名称">
          <el-input v-model="newController.name" />
        </el-form-item>
        <el-form-item label="端口">
          <el-input-number v-model="newController.port" :min="1" :max="65535" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmAdd">确认</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 控制器详情对话框 -->
    <el-dialog
      v-model="detailsVisible"
      title="控制器详情"
      width="800px"
    >
      <controller-details 
        v-if="selectedController"
        :controller="selectedController"
      />
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useStore } from 'vuex'
import ControllerDetails from './ControllerDetails.vue'

export default {
  name: 'ControllerPool',
  
  components: {
    ControllerDetails
  },
  
  setup() {
    const store = useStore()
    const controllers = ref([])
    const dialogVisible = ref(false)
    const detailsVisible = ref(false)
    const selectedController = ref(null)
    const newController = ref({
      type: 'ryu',
      name: '',
      port: 6633
    })
    
    // 获取控制器列表
    const fetchControllers = async () => {
      try {
        const response = await store.dispatch('dhr/fetchControllers')
        controllers.value = response
      } catch (error) {
        console.error('Failed to fetch controllers:', error)
      }
    }
    
    // 添加控制器
    const addController = () => {
      dialogVisible.value = true
    }
    
    const confirmAdd = async () => {
      try {
        await store.dispatch('dhr/addController', newController.value)
        dialogVisible.value = false
        await fetchControllers()
      } catch (error) {
        console.error('Failed to add controller:', error)
      }
    }
    
    // 控制器操作
    const startController = async (id) => {
      try {
        await store.dispatch('dhr/startController', id)
        await fetchControllers()
      } catch (error) {
        console.error('Failed to start controller:', error)
      }
    }
    
    const stopController = async (id) => {
      try {
        await store.dispatch('dhr/stopController', id)
        await fetchControllers()
      } catch (error) {
        console.error('Failed to stop controller:', error)
      }
    }
    
    const showDetails = (controller) => {
      selectedController.value = controller
      detailsVisible.value = true
    }
    
    // 辅助函数
    const getStatusType = (status) => {
      const types = {
        active: 'success',
        inactive: 'info',
        error: 'danger'
      }
      return types[status] || 'info'
    }
    
    const getHealthStatus = (score) => {
      if (score >= 0.8) return 'success'
      if (score >= 0.6) return 'warning'
      return 'exception'
    }
    
    onMounted(() => {
      fetchControllers()
    })
    
    return {
      controllers,
      dialogVisible,
      detailsVisible,
      selectedController,
      newController,
      addController,
      confirmAdd,
      startController,
      stopController,
      showDetails,
      getStatusType,
      getHealthStatus
    }
  }
}
</script>

<style scoped>
.controller-pool {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.controllers {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.controller-card {
  border: 1px solid #ebeef5;
}

.controller-card.active {
  border-left: 4px solid #67c23a;
}

.controller-card.inactive {
  border-left: 4px solid #909399;
}

.controller-card.error {
  border-left: 4px solid #f56c6c;
}

.controller-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.controller-metrics {
  margin: 15px 0;
}

.metric-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 8px 0;
}

.controller-actions {
  margin-top: 15px;
  display: flex;
  justify-content: flex-end;
}
</style> 