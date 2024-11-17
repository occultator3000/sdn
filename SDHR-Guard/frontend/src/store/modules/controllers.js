import axios from 'axios'

const state = {
  controllers: {},
  loading: false,
  error: null
}

const mutations = {
  SET_CONTROLLERS(state, controllers) {
    state.controllers = controllers
  },
  SET_LOADING(state, loading) {
    state.loading = loading
  },
  SET_ERROR(state, error) {
    state.error = error
  }
}

const actions = {
  // 获取所有控制器状态
  async fetchControllers({ commit }) {
    commit('SET_LOADING', true)
    try {
      const response = await axios.get('/api/controllers')
      commit('SET_CONTROLLERS', response.data)
    } catch (error) {
      commit('SET_ERROR', error.message)
    }
    commit('SET_LOADING', false)
  },

  // 启动控制器
  async startController({ dispatch }, controllerId) {
    try {
      await axios.post(`/api/controllers/${controllerId}/start`)
      await dispatch('fetchControllers')
    } catch (error) {
      throw error
    }
  },

  // 停止控制器
  async stopController({ dispatch }, controllerId) {
    try {
      await axios.post(`/api/controllers/${controllerId}/stop`)
      await dispatch('fetchControllers')
    } catch (error) {
      throw error
    }
  },

  // 健康检查
  async checkHealth({ commit }, controllerId) {
    try {
      const response = await axios.get(`/api/controllers/${controllerId}/health`)
      return response.data
    } catch (error) {
      throw error
    }
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions
} 