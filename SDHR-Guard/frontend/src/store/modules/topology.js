export default {
  namespaced: true,
  state: {
    nodes: [],
    links: []
  },
  mutations: {
    SET_TOPOLOGY(state, { nodes, links }) {
      state.nodes = nodes
      state.links = links
    }
  },
  actions: {
    async fetchTopology({ commit }) {
      try {
        const response = await this._vm.$axios.get('/api/topology')
        commit('SET_TOPOLOGY', response.data)
      } catch (error) {
        console.error('获取拓扑失败:', error)
      }
    }
  }
} 