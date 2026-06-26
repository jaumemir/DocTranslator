<script lang="ts" setup>
import { useTheme } from "@/hooks/useTheme"
// Set Element Plus language to Chinese
import zhCn from "element-plus/es/locale/lang/zh-cn"

const { initTheme } = useTheme()

/** Initialize theme */
initTheme()
</script>

<template>
  <el-config-provider :locale="zhCn">
    <router-view />
  </el-config-provider>
</template>
