<script lang="ts" setup>
import ErrorPageLayout from "./components/ErrorPageLayout.vue"
import Svg404 from "@/assets/error-page/404.svg?component" // vite-svg-loader plugin feature
</script>

<template>
  <ErrorPageLayout>
    <Svg404 />
  </ErrorPageLayout>
</template>
