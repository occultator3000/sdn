import Vue from 'vue'
import VueRouter from 'vue-router'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { title: '系统仪表盘' }
  },
  {
    path: '/controllers',
    name: 'Controllers',
    component: () => import('@/views/Controllers.vue'),
    meta: { title: '控制器管理' }
  },
  {
    path: '/topology',
    name: 'Topology',
    component: () => import('@/views/Topology.vue'),
    meta: { title: '网络拓扑' }
  },
  {
    path: '/dhr',
    name: 'DHR',
    component: () => import('@/views/Dhr.vue'),
    meta: { title: 'DHR防御配置' }
  },
  {
    path: '/monitor',
    name: 'Monitor',
    component: () => import('@/views/Monitor.vue'),
    meta: { title: '流量监控' }
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title || 'SDN DHR防御系统'
  next()
})

export default router 