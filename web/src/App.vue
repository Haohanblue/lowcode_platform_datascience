<script setup lang="ts">
import { ElMenu, ElMenuItem } from 'element-plus'
import { RouterLink } from 'vue-router'
import Home from './components/Home.vue'
import Image from './components/Image.vue'
</script>

<template>
  <el-menu default-active="/" mode="horizontal">
    <el-menu-item index="/">
      <router-link to="/">Home</router-link>
    </el-menu-item>
    <el-menu-item index="/image">
      <router-link to="/image">Image</router-link>
    </el-menu-item>
  </el-menu>
  
  <router-view></router-view>
</template>

<style scoped>
/* 可以在这里进行自定义样式 */
</style>