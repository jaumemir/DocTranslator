<script lang="ts" setup>
import { ref } from "vue"
import { useWatermark } from "@/hooks/useWatermark"

const localRef = ref<HTMLElement | null>(null)
const { setWatermark, clearWatermark } = useWatermark(localRef)
const { setWatermark: setGlobalWatermark, clearWatermark: clearGlobalWatermark } = useWatermark()
</script>

<template>
  <div class="app-container">
    <h4>
      This example demonstrates: Enabling or disabling watermarks by calling a hook,
      supporting local, global, and custom styles (color, transparency, font size, font, tilt angle, etc.), with built-in defense (anti-delete, anti-hide) and adaptive functionality
    </h4>
    <div ref="localRef" class="local" />
    <el-button-group>
      <el-button type="primary" @click="setWatermark('Local Watermark', { color: '#409eff' })">Create Local Watermark</el-button>
      <el-button type="warning" @click="setWatermark('Local watermark without defense', { color: '#e6a23c', defense: false })">
        Disable Defense
      </el-button>
      <el-button type="danger" @click="clearWatermark">Clear Local Watermark</el-button>
    </el-button-group>
    <el-button-group>
      <el-button type="primary" @click="setGlobalWatermark('Global Watermark', { color: '#409eff' })">Create Global Watermark</el-button>
      <el-button
        type="warning"
        @click="setGlobalWatermark('Global watermark without defense', { color: '#e6a23c', defense: false })"
      >
        Disable Defense
      </el-button>
      <el-button type="danger" @click="clearGlobalWatermark">Clear Global Watermark</el-button>
    </el-button-group>
  </div>
</template>

<style lang="scss" scoped>
.local {
  height: 30vh;
  border: 2px dashed var(--el-color-primary);
  margin-bottom: 20px;
}

.el-button-group {
  margin-right: 12px;
}
</style>
