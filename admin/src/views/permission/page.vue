<script lang="ts" setup>
import SwitchRoles from "./components/SwitchRoles.vue"
</script>

<template>
  <div class="app-container">
    <SwitchRoles />
    <el-tag type="warning" size="large">This page is only visible to admin role. After switching roles, you will not be able to access this page</el-tag>
  </div>
</template>

<style lang="scss" scoped>
.el-tag {
  margin-top: 15px;
}
</style>
