<template>
    <v-container fluid>
      <!-- 系统状态总览 -->
      <v-row>
        <!-- 系统状态卡片 -->
        <v-col cols="12" md="4">
          <v-card class="dashboard-card">
            <v-card-title class="d-flex align-center">
              系统状态
              <v-spacer></v-spacer>
              <v-chip :color="systemHealthColor" small label>
                {{ systemHealth }}
              </v-chip>
            </v-card-title>
            <v-divider></v-divider>
            <v-card-text>
              <v-row no-gutters>
                <v-col cols="6" class="py-2">
                  <div class="text-subtitle-2 grey--text">运行时间</div>
                  <div class="text-h6">{{ uptime }}</div>
                </v-col>
                <v-col cols="6" class="py-2">
                  <div class="text-subtitle-2 grey--text">控制器状态</div>
                  <div class="text-h6">运行: {{ activeControllers }}/3</div>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
  
        <!-- 网络拓扑卡片 -->
        <v-col cols="12" md="4">
          <v-card class="dashboard-card">
            <v-card-title>网络拓扑</v-card-title>
            <v-divider></v-divider>
            <v-card-text>
              <v-row no-gutters>
                <v-col cols="4" class="py-2">
                  <div class="text-subtitle-2 grey--text">交换机</div>
                  <div class="text-h6">{{ topoStats.switch_count || 0 }}</div>
                </v-col>
                <v-col cols="4" class="py-2">
                  <div class="text-subtitle-2 grey--text">主机</div>
                  <div class="text-h6">{{ topoStats.host_count || 0 }}</div>
                </v-col>
                <v-col cols="4" class="py-2">
                  <div class="text-subtitle-2 grey--text">链路</div>
                  <div class="text-h6">{{ topoStats.link_count || 0 }}</div>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
  
        <!-- DHR状态卡片 -->
        <v-col cols="12" md="4">
          <v-card class="dashboard-card">
            <v-card-title>DHR状态</v-card-title>
            <v-divider></v-divider>
            <v-card-text>
              <v-row no-gutters>
                <v-col cols="6" class="py-2">
                  <div class="text-subtitle-2 grey--text">主控制器</div>
                  <div class="text-h6">{{ primaryController }}</div>
                </v-col>
                <v-col cols="6" class="py-2">
                  <div class="text-subtitle-2 grey--text">切换次数</div>
                  <div class="text-h6">{{ switchCount }}</div>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
  
      <!-- 流量监控图表 -->
      <v-row class="mt-4">
        <v-col cols="12">
          <v-card class="dashboard-card">
            <v-card-title>流量监控</v-card-title>
            <v-divider></v-divider>
            <v-card-text style="height: 400px">
              <traffic-chart />
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </template>
  
  <script>
  import { mapState } from 'vuex'
  import TrafficChart from '@/components/Monitor/TrafficChart.vue'
  
  export default {
    name: 'Dashboard',
  
    data() {
      return {
        uptime: '0:00:00',
        switchCount: 0,
        topoStats: {},
        uptimeInterval: null
      }
    },
  
    computed: {
      ...mapState('controllers', ['controllers']),
  
      activeControllers() {
        return Object.values(this.controllers).filter(c => c.status === 'running').length
      },
  
      systemHealth() {
        return this.activeControllers > 0 ? '正常' : '异常'
      },
  
      systemHealthColor() {
        return this.activeControllers > 0 ? 'success' : 'error'
      },
  
      primaryController() {
        const running = Object.entries(this.controllers).find(([_, c]) => c.status === 'running')
        return running ? running[0] : '无'
      }
    },
  
    methods: {
      async fetchTopoStats() {
        try {
          const response = await this.$axios.get('/api/topology/stats')
          this.topoStats = response.data
        } catch (error) {
          console.error('获取拓扑统计失败:', error)
        }
      },
  
      updateUptime() {
        // 更新运行时间逻辑
        const start = this.$store.state.startTime || Date.now()
        const diff = Date.now() - start
        const hours = Math.floor(diff / 3600000)
        const minutes = Math.floor((diff % 3600000) / 60000)
        const seconds = Math.floor((diff % 60000) / 1000)
        this.uptime = `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
      }
    },
  
    mounted() {
      // 初始化数据
      this.fetchTopoStats()
      this.updateUptime()
  
      // 设置定时更新
      this.uptimeInterval = setInterval(this.updateUptime, 1000)
      setInterval(this.fetchTopoStats, 5000)
    },
  
    beforeDestroy() {
      if (this.uptimeInterval) {
        clearInterval(this.uptimeInterval)
      }
    }
  }
  </script>
  
  <style scoped>
  .dashboard-card {
    height: 100%;
    border-radius: 8px;
  }
  
  .v-card__title {
    font-size: 1.25rem;
    font-weight: 500;
    padding: 16px;
  }
  
  .v-card__text {
    padding: 16px;
  }
  
  .text-h6 {
    font-weight: 500;
    margin-top: 4px;
  }
  
  .v-chip {
    font-weight: 500;
  }
  </style>