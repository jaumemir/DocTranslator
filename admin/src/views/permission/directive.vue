<script lang="ts" setup>
import { checkPermission } from "@/utils/permission"
import SwitchRoles from "./components/SwitchRoles.vue"
</script>

<template>
  <div class="app-container">
    <SwitchRoles />
    <!-- v-permission example -->
    <div class="margin-top-30">
      <div>
        <el-tag v-permission="['admin']" type="success" size="large" effect="plain">
          This uses v-permission="['admin']" so only admin can see this sentence
        </el-tag>
      </div>
      <div>
        <el-tag v-permission="['editor']" type="success" size="large" effect="plain">
          This uses v-permission="['editor']" so only editor can see this sentence
        </el-tag>
      </div>
      <div class="margin-top-15">
        <el-tag v-permission="['admin', 'editor']" type="success" size="large" effect="plain">
          This uses v-permission="['admin', 'editor']" so both admin and editor can see this sentence
        </el-tag>
      </div>
    </div>
    <!-- checkPermission example -->
    <div class="margin-top-30">
      <el-tag type="warning" size="large">
        For example, Element Plus's el-tab-pane or el-table-column and other dynamically rendered DOM scenarios are not suitable for
        v-permission. In this case, you can use v-if and checkPermission:
      </el-tag>
      <el-tabs type="border-card" class="margin-top-15">
        <el-tab-pane v-if="checkPermission(['admin'])" label="admin">
          This uses <el-tag>v-if="checkPermission(['admin'])"</el-tag> so only admin can see this sentence
        </el-tab-pane>
        <el-tab-pane v-if="checkPermission(['editor'])" label="editor">
          This uses <el-tag>v-if="checkPermission(['editor'])"</el-tag> so only editor can see this sentence
        </el-tab-pane>
        <el-tab-pane v-if="checkPermission(['admin', 'editor'])" label="admin and editor">
          This uses <el-tag>v-if="checkPermission(['admin', 'editor'])"</el-tag> so both admin and editor can see this sentence
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.margin-top-15 {
  margin-top: 15px;
}

.margin-top-30 {
  margin-top: 30px;
}
</style>
