export default {
  namespaced: true,
  state: {
    config: {},
    status: 'inactive'
  },
  mutations: {
    SET_CONFIG(state, config) {
      state.config = config
    },
    SET_STATUS(state, status) {
      state.status = status
    }
  },
  actions: {
    // DHR相关actions将在后续实现
  }
} 