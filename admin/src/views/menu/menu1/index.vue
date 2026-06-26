<template>
  <div class="app-container">
    <h4>
      Level-3 and above route caching is disabled by default. To enable it, go to this configuration file:
      <el-link
        type="primary"
        href="https://github.com/un-pany/v3-admin-vite/blob/main/src/config/route.ts"
        target="_blank"
      >
        src/config/route.ts
      </el-link>
    </h4>
    <el-card header="Level-2 Route - menu1">
      <router-view />
    </el-card>
  </div>
</template>

<style lang="scss" scoped>
.el-link {
  font-size: 18px;
}
</style>
