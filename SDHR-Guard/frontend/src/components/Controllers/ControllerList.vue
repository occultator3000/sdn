<template>
    <div class="controller-list">
      <!-- 加载状态 -->
      <v-overlay :value="loading">
        <v-progress-circular indeterminate size="64"></v-progress-circular>
      </v-overlay>
  
      <!-- 错误提示 -->
      <v-alert
        v-if="error"
        type="error"
        dismissible
        @click="error = null"
      >
        {{ error }}
      </v-alert>
  
      <!-- 控制器列表 -->
      <v-row>
        <v-col
          v-for="(controller, id) in controllers"
          :key="id"
          cols="12"
          sm="6"
          md="4"
        >
          <controller-card
            :controller-id="id"
            :controller="controller"
          />
        </v-col>
      </v-row>
    </div>
  </template>
  
  <script>
  import { mapState } from 'vuex'
  import ControllerCard from './ControllerCard.vue'
  
  export default {
    name: 'ControllerList',
    
    components: {
      ControllerCard
    },
  
    computed: {
      ...mapState('controllers', {
        controllers: state => state.controllers,
        loading: state => state.loading,
        error: state => state.error
      })
    },
  
    methods: {
      async fetchControllers() {
        await this.$store.dispatch('controllers/fetchControllers')
      }
    },
  
    mounted() {
      // 组件挂载时获取控制器状态
      this.fetchControllers()
      
      // 每5秒刷新一次状态
      this.timer = setInterval(this.fetchControllers, 5000)
    },
  
    beforeDestroy() {
      // 组件销毁时清除定时器
      if (this.timer) {
        clearInterval(this.timer)
      }
    }
  }
  </script>