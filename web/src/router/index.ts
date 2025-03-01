import { createRouter, createWebHistory } from 'vue-router'
import Home from '../components/Home.vue'
import Image from '../components/Image.vue'

// 配置路由
const routes = [
  {
    path: '/',
    name: 'home',
    component: Home,
  },
  {
    path: '/image',
    name: 'image',
    component: Image,
  }
]

// 创建 Vue Router 实例
const router = createRouter({
  history: createWebHistory('/'),
  routes, // 路由配置
})

export default router