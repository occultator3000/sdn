import { getConfig, saveConfig, resetConfig } from '@/services/api/config'

const state = {
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
  },
  lastUpdate: null,
  initialized: false
}

const mutations = {
  SET_CONFIG(state, { module, config }) {
    state[module] = { ...state[module], ...config }
  },
  
  SET_FULL_CONFIG(state, config) {
    Object.keys(config).forEach(module => {
      if (state[module]) {
        state[module] = { ...state[module], ...config[module] }
      }
    })
    state.lastUpdate = new Date().toISOString()
  },
  
  SET_INITIALIZED(state, value) {
    state.initialized = value
  }
}

const actions = {
  // 初始化配置
  async initializeConfig({ commit, dispatch }) {
    try {
      const config = await dispatch('fetchConfig')
      commit('SET_FULL_CONFIG', config)
      commit('SET_INITIALIZED', true)
      return true
    } catch (error) {
      console.error('Failed to initialize config:', error)
      return false
    }
  },
  
  // 获取配置
  async fetchConfig({ commit }) {
    try {
      const config = await getConfig()
      commit('SET_FULL_CONFIG', config)
      return config
    } catch (error) {
      console.error('Failed to fetch config:', error)
      throw error
    }
  },
  
  // 保存配置
  async saveConfig({ commit }, config) {
    try {
      await saveConfig(config)
      commit('SET_FULL_CONFIG', config)
      return true
    } catch (error) {
      console.error('Failed to save config:', error)
      throw error
    }
  },
  
  // 重置配置
  async resetConfig({ commit }) {
    try {
      const config = await resetConfig()
      commit('SET_FULL_CONFIG', config)
      return true
    } catch (error) {
      console.error('Failed to reset config:', error)
      throw error
    }
  },
  
  // 更新模块配置
  async updateModuleConfig({ commit, state }, { module, config }) {
    try {
      const newConfig = {
        ...state[module],
        ...config
      }
      commit('SET_CONFIG', { module, config: newConfig })
      await saveConfig({ [module]: newConfig })
      return true
    } catch (error) {
      console.error(`Failed to update ${module} config:`, error)
      throw error
    }
  }
}

const getters = {
  // DHR配置
  dhrConfig: state => state.dhr,
  schedulerStrategy: state => state.dhr.schedulerStrategy,
  controllerLimits: state => ({
    min: state.dhr.minControllers,
    max: state.dhr.maxControllers
  }),
  
  // 告警配置
  alertConfig: state => state.alert,
  alertThresholds: state => ({
    load: state.alert.loadThreshold,
    latency: state.alert.latencyThreshold,
    error: state.alert.errorThreshold
  }),
  
  // 系统配置
  systemConfig: state => state.system,
  logLevel: state => state.system.logLevel,
  
  // 配置状态
  isInitialized: state => state.initialized,
  lastUpdateTime: state => state.lastUpdate
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
} 