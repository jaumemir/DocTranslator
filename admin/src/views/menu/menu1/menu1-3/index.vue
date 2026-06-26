<script lang="ts" setup>
import { ref } from "vue"

defineOptions({
  name: "Menu1-3"
})

const text = ref("")
</script>

<template>
  <div class="app-container">
    <el-card header="Level-3 Route Cache - menu1-3">
      <el-input v-model="text" />
    </el-card>
  </div>
</template>
