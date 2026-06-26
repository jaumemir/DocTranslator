<script lang="ts" setup>
import { useFetchSelect } from "@/hooks/useFetchSelect"
import { getSelectDataApi } from "@/api/hook-demo/use-fetch-select"

const { loading, options, value } = useFetchSelect({
  api: getSelectDataApi
})
</script>

<template>
  <div class="app-container">
    <h4>This example demonstrates: Automatically calling an API through a hook to get data required by the Select component and pass it to the Select component</h4>
    <h5>Select Example</h5>
    <el-select :loading="loading" v-model="value" filterable>
      <el-option v-for="(item, index) in options" v-bind="item" :key="index" placeholder="Please select" />
    </el-select>
    <h5>Select V2 Example (Choose this component if data volume is large)</h5>
    <el-select-v2 :loading="loading" v-model="value" :options="options" filterable placeholder="Please select" />
  </div>
</template>
