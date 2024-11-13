<template>
  <div class="system-config">
    <el-card class="config-card">
      <template #header>
        <div class="card-header">
          <span>系统配置</span>
          <el-button-group>
            <el-button 
              type="primary"
              @click="saveConfig"
              :loading="saving"
            >
              保存配置
            </el-button>
            <el-button 
              type="warning"
              @click="resetConfig"
            >
              重置
            </el-button>
          </el-button-group>
        </div>
      </template>
      
      <el-tabs v-model="activeTab">
        <!-- DHR配置 -->
        <el-tab-pane label="DHR配置" name="dhr">
          <el-form 
            ref="dhrForm"
            :model="config.dhr"
            label-width="140px"
          >
            <el-form-item label="调度策略">
              <el-select v-model="config.dhr.schedulerStrategy">
                <el-option label="轮询调度" value="round_robin" />
                <el-option label="健康感知调度" value="health_aware" />
                <el-option label="异构感知调度" value="diversity_aware" />
                <el-option label="自适应调度" value="adaptive" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="最小控制器数量">
              <el-input-number
                v-model="config.dhr.minControllers"
                :min="1"
                :max="config.dhr.maxControllers"
              />
            </el-form-item>
            
            <el-form-item label="最大控制器数量">
              <el-input-number
                v-model="config.dhr.maxControllers"
                :min="config.dhr.minControllers"
                :max="10"
              />
            </el-form-item>
            
            <el-form-item label="调度间隔(秒)">
              <el-input-number
                v-model="config.dhr.scheduleInterval"
                :min="1"
                :max="60"
              />
            </el-form-item>
            
            <el-form-item label="切换冷却时间(秒)">
              <el-input-number
                v-model="config.dhr.switchCooldown"
                :min="0"
                :max="300"
              />
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <!-- 告警配置 -->
        <el-tab-pane label="告警配置" name="alert">
          <el-form 
            ref="alertForm"
            :model="config.alert"
            label-width="140px"
          >
            <el-form-item label="负载告警阈值">
              <el-slider
                v-model="config.alert.loadThreshold"
                :format-tooltip="formatPercentage"
                :marks="{
                  70: '70%',
                  80: '80%',
                  90: '90%'
                }"
              />
            </el-form-item>
            
            <el-form-item label="响应时间阈值(ms)">
              <el-input-number
                v-model="config.alert.latencyThreshold"
                :min="100"
                :max="5000"
                :step="100"
              />
            </el-form-item>
            
            <el-form-item label="错误率阈值">
              <el-slider
                v-model="config.alert.errorThreshold"
                :format-tooltip="formatPercentage"
                :marks="{
                  5: '5%',
                  10: '10%',
                  20: '20%'
                }"
              />
            </el-form-item>
            
            <el-form-item label="告警检查间隔(秒)">
              <el-input-number
                v-model="config.alert.checkInterval"
                :min="5"
                :max="300"
                :step="5"
              />
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <!-- 系统参数 -->
        <el-tab-pane label="系统参数" name="system">
          <el-form 
            ref="systemForm"
            :model="config.system"
            label-width="140px"
          >
            <el-form-item label="数据保留时间(天)">
              <el-input-number
                v-model="config.system.dataRetention"
                :min="1"
                :max="90"
              />
            </el-form-item>
            
            <el-form-item label="监控刷新间隔(秒)">
              <el-input-number
                v-model="config.system.monitorInterval"
                :min="1"
                :max="60"
              />
            </el-form-item>
            
            <el-form-item label="日志级别">
              <el-select v-model="config.system.logLevel">
                <el-option label="DEBUG" value="debug" />
                <el-option label="INFO" value="info" />
                <el-option label="WARNING" value="warning" />
                <el-option label="ERROR" value="error" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="自动备份">
              <el-switch v-model="config.system.autoBackup" />
            </el-form-item>
            
            <el-form-item 
              label="备份间隔(小时)"
              v-if="config.system.autoBackup"
            >
              <el-input-number
                v-model="config.system.backupInterval"
                :min="1"
                :max="24"
              />
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useStore } from 'vuex'
import { ElMessage } from 'element-plus'

export default {
  name: 'SystemConfig',
  
  setup() {
    const store = useStore()
    const activeTab = ref('dhr')
    const saving = ref(false)
    
    // 表单引用
    const dhrForm = ref(null)
    const alertForm = ref(null)
    const systemForm = ref(null)
    
    // 配置数据
    const config = reactive({
      dhr: {
        schedulerStrategy: 'health_aware',
        minControllers: 2,
        maxControllers: 5,
        scheduleInterval: 5,
        switchCooldown: 30
      },
      alert: {
        loadThreshold: 80,
        latencyThreshold: 1000,
        errorThreshold: 10,
        checkInterval: 30
      },
      system: {
        dataRetention: 30,
        monitorInterval: 5,
        logLevel: 'info',
        autoBackup: true,
        backupInterval: 12
      }
    })
    
    // 加载配置
    const loadConfig = async () => {
      try {
        const savedConfig = await store.dispatch('config/fetchConfig')
        Object.assign(config.dhr, savedConfig.dhr || {})
        Object.assign(config.alert, savedConfig.alert || {})
        Object.assign(config.system, savedConfig.system || {})
      } catch (error) {
        ElMessage.error('加载配置失败')
        console.error('Failed to load config:', error)
      }
    }
    
    // 保存配置
    const saveConfig = async () => {
      try {
        saving.value = true
        
        // 验证表单
        await Promise.all([
          dhrForm.value?.validate(),
          alertForm.value?.validate(),
          systemForm.value?.validate()
        ])
        
        // 保存配置
        await store.dispatch('config/saveConfig', {
          dhr: config.dhr,
          alert: config.alert,
          system: config.system
        })
        
        // 应用配置
        await applyConfig()
        
        ElMessage.success('配置保存成功')
      } catch (error) {
        ElMessage.error('保存配置失败')
        console.error('Failed to save config:', error)
      } finally {
        saving.value = false
      }
    }
    
    // 重置配置
    const resetConfig = async () => {
      try {
        await store.dispatch('config/resetConfig')
        await loadConfig()
        ElMessage.success('配置已重置')
      } catch (error) {
        ElMessage.error('重置配置失败')
        console.error('Failed to reset config:', error)
      }
    }
    
    // 应用配置
    const applyConfig = async () => {
      try {
        // 应用DHR配置
        await store.dispatch('dhr/updateSchedulerConfig', config.dhr)
        
        // 应用告警配置
        await store.dispatch('monitor/updateAlertConfig', config.alert)
        
        // 应用系统配置
        await store.dispatch('system/updateConfig', config.system)
      } catch (error) {
        console.error('Failed to apply config:', error)
        throw error
      }
    }
    
    // 辅助函数
    const formatPercentage = (val) => {
      return `${val}%`
    }
    
    // 验证规则
    const validateDHR = (rule, value, callback) => {
      if (value.minControllers > value.maxControllers) {
        callback(new Error('最小控制器数量不能大于最大数量'))
      } else {
        callback()
      }
    }
    
    // 配置变更处理
    const handleConfigChange = async (key, value) => {
      try {
        switch (key) {
          case 'schedulerStrategy':
            await store.dispatch('dhr/changeSchedulerStrategy', value)
            break
          case 'logLevel':
            await store.dispatch('system/updateLogLevel', value)
            break
          // 其他配置项的处理...
        }
      } catch (error) {
        console.error('Failed to handle config change:', error)
      }
    }
    
    // 监听配置变更
    watch(
      () => config.dhr.schedulerStrategy,
      (newVal) => handleConfigChange('schedulerStrategy', newVal)
    )
    
    watch(
      () => config.system.logLevel,
      (newVal) => handleConfigChange('logLevel', newVal)
    )
    
    // 生命周期钩子
    onMounted(() => {
      loadConfig()
    })
    
    return {
      activeTab,
      config,
      saving,
      dhrForm,
      alertForm,
      systemForm,
      saveConfig,
      resetConfig,
      formatPercentage
    }
  }
}
</script>

<style scoped>
.system-config {
  padding: 20px;
}

.config-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.el-form {
  max-width: 600px;
  margin: 20px auto;
}

.el-slider {
  width: 100%;
}
</style> 