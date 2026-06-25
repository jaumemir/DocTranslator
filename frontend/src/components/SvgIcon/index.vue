<template>
  <svg aria-hidden="true" class="svg-icon" :style="'width:' + size + ';height:' + size">
    <use :xlink:href="symbolId" :fill="color" />
  </svg>
</template>

<script setup lang="ts">
const props = defineProps({
  prefix: {
    type: String,
    default: 'icon'
  },
  iconClass: {
    type: String,
    required: false,
    default: ''
  },
  color: {
    type: String,
    default: ''
  },
  size: {
    type: String,
    default: '1em'
  }
})
import { computed } from 'vue'
const symbolId = computed(() => `#${props.prefix}-${props.iconClass}`)
</script>

<style scoped>
.svg-icon {
  display: inline-block;
  width: 1em;
  height: 1em;
  overflow: hidden;
  vertical-align: -0.15em; /* Since the icon size is set to match the font size, and the bottom edge of span tags aligns with the font baseline, set a downward offset to correct visual misalignment */
  outline: none;
  fill: currentcolor; /* Define the element's color; currentColor is a variable representing the current element's color value, inherited from parent if not set */
}
</style>