import { getTestResults, exportTestReport } from '@/services/api/test'

const state = {
  // 测试统计
  totalTests: 0,
  successRate: 0,
  
  // 时间序列数据
  timeLabels: [],
  ryuResponseTimes: [],
  poxResponseTimes: [],
  odlResponseTimes: [],
  
  // 性能指标
  successRates: [],
  performanceScores: [],
  securityScores: [],
  
  // 差异分析
  differences: [],
  
  // 安全指标
  securityMetrics: {
    vulnerability: 0,
    errorHandling: 0,
    inputValidation: 0
  },
  
  // 详细信息
  vulnerabilityDetails: [],
  errorHandlingDetails: [],
  inputValidationDetails: [],
  
  // 建议
  recommendations: [],
  
  // 加载状态
  loading: false,
  error: null
}

const mutations = {
  SET_TEST_RESULTS(state, results) {
    // 更新测试统计
    state.totalTests = results.totalTests
    state.successRate = results.successRate
    
    // 更新时间序列数据
    state.timeLabels = results.timeLabels
    state.ryuResponseTimes = results.responseTimes.ryu
    state.poxResponseTimes = results.responseTimes.pox
    state.odlResponseTimes = results.responseTimes.odl
    
    // 更新性能指标
    state.successRates = results.performanceMetrics.successRates
    state.performanceScores = results.performanceMetrics.performanceScores
    state.securityScores = results.performanceMetrics.securityScores
    
    // 更新差异分析
    state.differences = results.differences
    
    // 更新安全指标
    state.securityMetrics = results.securityMetrics
    
    // 更新详细信息
    state.vulnerabilityDetails = results.securityDetails.vulnerability
    state.errorHandlingDetails = results.securityDetails.errorHandling
    state.inputValidationDetails = results.securityDetails.inputValidation
    
    // 更新建议
    state.recommendations = results.recommendations
  },
  
  SET_LOADING(state, loading) {
    state.loading = loading
  },
  
  SET_ERROR(state, error) {
    state.error = error
  }
}

const actions = {
  // 获取测试结果
  async fetchResults({ commit }) {
    commit('SET_LOADING', true)
    try {
      const results = await getTestResults()
      commit('SET_TEST_RESULTS', results)
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // 导出测试报告
  async exportReport({ commit }) {
    try {
      const response = await exportTestReport()
      // 处理文件下载
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', 'test_report.pdf')
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    }
  }
}

const getters = {
  // 测试结果概览
  testOverview: state => ({
    totalTests: state.totalTests,
    successRate: state.successRate,
    differences: state.differences.length
  }),
  
  // 控制器性能对比
  controllerPerformance: state => ({
    labels: ['RYU', 'POX', 'OpenDaylight'],
    successRates: state.successRates,
    performanceScores: state.performanceScores,
    securityScores: state.securityScores
  }),
  
  // 安全评估结果
  securityAssessment: state => ({
    metrics: state.securityMetrics,
    details: {
      vulnerability: state.vulnerabilityDetails,
      errorHandling: state.errorHandlingDetails,
      inputValidation: state.inputValidationDetails
    }
  }),
  
  // 关键差异
  criticalDifferences: state => 
    state.differences.filter(diff => diff.impact >= 0.8),
  
  // 优先建议
  priorityRecommendations: state =>
    state.recommendations
      .filter(rec => rec.priority === 'high')
      .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
} 