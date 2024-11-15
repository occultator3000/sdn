<template>
  <v-app>
    <!-- 左侧导航栏 -->
    <v-navigation-drawer app permanent dark>
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title class="text-h6">
            SDN DHR防御系统
          </v-list-item-title>
          <v-list-item-subtitle>
            控制器异构冗余防御
          </v-list-item-subtitle>
        </v-list-item-content>
      </v-list-item>

      <v-divider></v-divider>

      <v-list dense nav>
        <v-list-item to="/" exact>
          <v-list-item-icon>
            <v-icon>mdi-view-dashboard</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>仪表盘</v-list-item-title>
          </v-list-item-content>
        </v-list-item>

        <v-list-item to="/controllers">
          <v-list-item-icon>
            <v-icon>mdi-server-network</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>控制器管理</v-list-item-title>
          </v-list-item-content>
        </v-list-item>

        <v-list-item to="/topology">
          <v-list-item-icon>
            <v-icon>mdi-graph-outline</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>网络拓扑</v-list-item-title>
          </v-list-item-content>
        </v-list-item>

        <v-list-item to="/dhr">
          <v-list-item-icon>
            <v-icon>mdi-shield-check</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>DHR防御</v-list-item-title>
          </v-list-item-content>
        </v-list-item>

        <v-list-item to="/monitor">
          <v-list-item-icon>
            <v-icon>mdi-chart-line</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>流量监控</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>

    <!-- 顶部工具栏 -->
    <v-app-bar app color="primary" dark>
      <v-app-bar-nav-icon></v-app-bar-nav-icon>
      <v-toolbar-title>{{ getCurrentPageTitle }}</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn icon>
        <v-icon>mdi-refresh</v-icon>
      </v-btn>
      <v-btn icon>
        <v-icon>mdi-cog</v-icon>
      </v-btn>
    </v-app-bar>

    <!-- 主要内容区域 -->
    <v-main>
      <v-container fluid>
        <router-view></router-view>
      </v-container>
    </v-main>

    <!-- 底部状态栏 -->
    <v-footer app>
      <span>&copy; {{ new Date().getFullYear() }} SDN DHR Defense System</span>
    </v-footer>
  </v-app>
</template>

<script>
export default {
  name: 'App',
  
  computed: {
    getCurrentPageTitle() {
      const route = this.$route.path
      const titles = {
        '/': '系统仪表盘',
        '/controllers': '控制器管理',
        '/topology': '网络拓扑',
        '/dhr': 'DHR防御配置',
        '/monitor': '流量监控'
      }
      return titles[route] || 'SDN DHR防御系统'
    }
  }
}
</script>

<style>
.v-application {
  font-family: "Helvetica Neue", Helvetica, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "微软雅黑", Arial, sans-serif;
}
</style> 