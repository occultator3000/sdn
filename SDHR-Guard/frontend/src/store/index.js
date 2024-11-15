import Vue from 'vue'
import Vuex from 'vuex'
import axios from 'axios'

// 导入模块
import controllers from './modules/controllers'
import topology from './modules/topology'
import dhr from './modules/dhr'

Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    controllers,
    topology,
    dhr
  },
  state: {
    loading: false,
    error: null,
    alerts: []
  },
  mutations: {
    SET_LOADING(state, status) {
      state.loading = status
    },
    SET_ERROR(state, error) {
      state.error = error
    },
    ADD_ALERT(state, alert) {
      state.alerts.push({
        ...alert,
        id: Date.now(),
        timestamp: new Date()
      })
    },
    REMOVE_ALERT(state, alertId) {
      state.alerts = state.alerts.filter(alert => alert.id !== alertId)
    }
  },
  actions: {
    showAlert({ commit }, alert) {
      commit('ADD_ALERT', alert)
      if (alert.timeout !== 0) {
        setTimeout(() => {
          commit('REMOVE_ALERT', alert.id)
        }, alert.timeout || 3000)
      }
    }
  }
}) 