import { createStore } from 'vuex'
import config from './modules/config'
import dhr from './modules/dhr'
import monitor from './modules/monitor'

export default createStore({
  modules: {
    config,
    dhr,
    monitor
  },
  
  state: {
    // 全局状态
  },
  
  mutations: {
    // 全局mutations
  },
  
  actions: {
    // 全局actions
  }
})
