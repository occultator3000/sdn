<template>
    <v-card class="mx-auto" max-width="344">
      <!-- 控制器标题和状态 -->
      <v-card-title class="d-flex justify-space-between">
        {{ controllerId }}
        <v-chip :color="statusColor" small>
          {{ controller.status }}
        </v-chip>
      </v-card-title>
  
      <!-- 控制器信息 -->
      <v-card-text>
        <v-list-item>
          <v-list-item-content>
            <v-list-item-subtitle>
              端口: {{ controller.port }}
            </v-list-item-subtitle>
            <v-list-item-subtitle>
              健康状态: {{ healthStatus }}
            </v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
      </v-card-text>
  
      <!-- 控制按钮 -->
      <v-card-actions>
        <v-btn
          color="primary"
          :loading="loading"
          :disabled="isRunning"
          @click="startController"
        >
          启动
        </v-btn>
        <v-btn
          color="error"
          :loading="loading"
          :disabled="!isRunning"
          @click="stopController"
        >
          停止
        </v-btn>
      </v-card-actions>
    </v-card>
  </template>
  
  <script>
  export default {
    name: 'ControllerCard',
    
    props: {
      controllerId: {
        type: String,
        required: true
      },
      controller: {
        type: Object,
        required: true
      }
    },
  
    data() {
      return {
        loading: false,
        healthStatus: '检查中...',
        healthCheckInterval: null
      }
    },
  
    created() {
      this.healthStatus = this.controller.health
    },
  
    computed: {
      isRunning() {
        return this.controller.status === 'running' || this.controller.status === 'starting'
      },
      
      statusColor() {
        const colors = {
          'running': 'success',
          'stopped': 'grey',
          'error': 'error',
          'starting': 'warning'
        }
        return colors[this.controller.status] || 'grey'
      }
    },
  
    methods: {
      async startController() {
        this.loading = true
        try {
          await this.$store.dispatch('controllers/startController', this.controllerId)
          this.checkHealth()
        } catch (error) {
          console.error('启动控制器失败:', error)
        }
        this.loading = false
      },
  
      async stopController() {
        this.loading = true
        try {
          await this.$store.dispatch('controllers/stopController', this.controllerId)
        } catch (error) {
          console.error('停止控制器失败:', error)
        }
        this.loading = false
      },
  
      async checkHealth() {
        try {
          const response = await this.$axios.get(`/api/controllers/${this.controllerId}/health`)
          this.$emit('update:health', response.data.health)
          this.healthStatus = response.data.health
        } catch (error) {
          console.error('健康检查失败:', error)
        }
      }
    },
  
    watch: {
      'controller.health'(newVal) {
        this.healthStatus = newVal
      },
      'controller.status'(newVal) {
        this.healthStatus = newVal
      }
    },
  
    mounted() {
      this.healthCheckInterval = setInterval(async () => {
        if (this.controller.status === 'running') {
          try {
            const response = await this.$axios.get(`/api/controllers/${this.controllerId}/health`)
            this.$emit('update:health', response.data.health)
          } catch (error) {
            console.error('健康检查失败:', error)
          }
        }
      }, 5000)
    },
  
    beforeDestroy() {
      if (this.healthCheckInterval) {
        clearInterval(this.healthCheckInterval)
      }
    }
  }
  </script> 