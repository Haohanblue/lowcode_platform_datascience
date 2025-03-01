import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';
import axios from 'axios';
const app = createApp(App);
import router from './router'  // 引入路由
// 将 axios 作为全局实例注入到 Vue 实例中
app.config.globalProperties.$axios = axios;
app.use(router)  // 使用路由
// 使用 ElementPlus 插件
app.use(ElementPlus);
app.mount('#app')
