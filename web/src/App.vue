<template>
  <el-container style="min-height: 100vh">
    <el-aside width="220px" style="background: #304156">
      <div class="sidebar-header">
        <el-icon size="24" color="#409EFF"><Monitor /></el-icon>
        <span class="sidebar-title">水质监测系统</span>
      </div>
      <el-menu
        :default-active="$route.path"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/">
          <el-icon><Monitor /></el-icon>
          <span>首页看板</span>
        </el-menu-item>
        <el-menu-item index="/data">
          <el-icon><DataBoard /></el-icon>
          <span>数据管理</span>
        </el-menu-item>
        <el-menu-item index="/predict">
          <el-icon><TrendCharts /></el-icon>
          <span>水质预测</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header style="background: #fff; border-bottom: 1px solid #e6e6e6; display: flex; align-items: center; justify-content: space-between">
        <div class="header-left">
          <h2 style="margin: 0; font-size: 18px; font-weight: 500; color: #303133">{{ $route.meta.title }}</h2>
        </div>
        <div class="header-right">
          <span style="color: #909399; font-size: 13px">基于大数据与机器学习的水质监测与预测系统</span>
        </div>
      </el-header>
      <el-main style="background: #f0f2f5; padding: 20px">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { Monitor, DataBoard, TrendCharts } from '@element-plus/icons-vue'
</script>

<style>
body {
  margin: 0;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Microsoft YaHei', sans-serif;
}
.sidebar-header {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}
.sidebar-title {
  color: #fff;
  font-size: 16px;
  font-weight: 600;
}
.el-menu {
  border-right: none;
}
</style>
