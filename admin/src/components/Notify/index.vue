<script lang="ts" setup>
import { ref, computed } from "vue"
import { ElMessage } from "element-plus"
import { Bell } from "@element-plus/icons-vue"
import NotifyList from "./NotifyList.vue"
import { type ListItem, notifyData, messageData, todoData } from "./data"

type TabName = "Notifications" | "Messages" | "Todo"

interface DataItem {
  name: TabName
  type: "primary" | "success" | "warning" | "danger" | "info"
  list: ListItem[]
}

/** Badge current value */
const badgeValue = computed(() => {
  return data.value.reduce((sum, item) => sum + item.list.length, 0)
})
/** Badge max value */
const badgeMax = 99
/** Popover width */
const popoverWidth = 350
/** Current Tab */
const activeName = ref<TabName>("Notifications")
/** All data */
const data = ref<DataItem[]>([
  // Notification data
  {
    name: "Notifications",
    type: "primary",
    list: notifyData
  },
  // Message data
  {
    name: "Messages",
    type: "danger",
    list: messageData
  },
  // Todo data
  {
    name: "Todo",
    type: "warning",
    list: todoData
  }
])

const handleHistory = () => {
  ElMessage.success(`Navigate to ${activeName.value} history page`)
}
</script>

<template>
  <div class="notify">
    <el-popover placement="bottom" :width="popoverWidth" trigger="click">
      <template #reference>
        <el-badge :value="badgeValue" :max="badgeMax" :hidden="badgeValue === 0">
          <el-tooltip effect="dark" content="Message Notifications" placement="bottom">
            <el-icon :size="20">
              <Bell />
            </el-icon>
          </el-tooltip>
        </el-badge>
      </template>
      <template #default>
        <el-tabs v-model="activeName" class="demo-tabs" stretch>
          <el-tab-pane v-for="(item, index) in data" :name="item.name" :key="index">
            <template #label>
              {{ item.name }}
              <el-badge :value="item.list.length" :max="badgeMax" :type="item.type" />
            </template>
            <el-scrollbar height="400px">
              <NotifyList :list="item.list" />
            </el-scrollbar>
          </el-tab-pane>
        </el-tabs>
        <div class="notify-history">
          <el-button link @click="handleHistory">View {{ activeName }} History</el-button>
        </div>
      </template>
    </el-popover>
  </div>
</template>

<style lang="scss" scoped>
.notify {
  margin-right: 10px;
}

.notify-history {
  text-align: center;
  padding-top: 12px;
  border-top: 1px solid var(--el-border-color);
}
</style>
