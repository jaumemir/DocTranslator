<script lang="ts" setup>
import { reactive, ref, watch } from "vue"
import { getToken } from "@/utils/cache/cookies"
import { getTranslateDataApi, deleteTranslateDataApi, deleteMoreTranslateDataApi } from "@/api/translate"
import { type GetTranslateData } from "@/api/translate/types/translate"
import { type FormInstance, ElMessage, ElMessageBox } from "element-plus"
import { Search, Refresh, Download, Delete } from "@element-plus/icons-vue"
import { usePagination } from "@/hooks/usePagination"
const BASE_URL = import.meta.env.VITE_BASE_API
defineOptions({
  // Name the current component
  name: "Translate"
})

const loading = ref<boolean>(false)
const { paginationData, handleCurrentChange, handleSizeChange } = usePagination()

//#region Delete
const handleDelete = (row: GetTranslateData) => {
  ElMessageBox.confirm(`Confirm deleting the current document?`, "Prompt", {
    confirmButtonText: "Confirm",
    cancelButtonText: "Cancel",
    type: "warning"
  }).then(() => {
    deleteTranslateDataApi(row.id).then(() => {
      ElMessage.success("Deleted successfully")
      getTableData()
    })
  })
}

// Get selected items
const selectedItems = ref<number[]>([])
const handleSelectionChange = (selection: any[]) => {
  selectedItems.value = selection.map((item) => item.id)
  console.log(selectedItems.value)
}

//#region Batch delete
const handleMoreDelete = () => {
  if (selectedItems.value.length === 0) {
    ElMessage.warning("Please select documents to delete")
    return
  }
  ElMessageBox.confirm(`Batch deleting selected documents, confirm deletion?`, "Prompt", {
    confirmButtonText: "Confirm",
    cancelButtonText: "Cancel",
    type: "warning"
  }).then(() => {
    deleteMoreTranslateDataApi({ ids: selectedItems.value }).then(() => {
      ElMessage.success("Deleted successfully")
      getTableData()
    })
  })
}

//#region Batch download
const handleMoreDownload = () => {
  if (selectedItems.value.length === 0) {
    ElMessage.warning("Please select documents to download")
    return
  }

  const ids = selectedItems.value
  const url = `${BASE_URL}/api/admin/translates/download/batch`
  const token = getToken()
  fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      token: token
    },
    body: JSON.stringify({ ids })
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok")
      }
      return response.blob()
    })
    .then((blob) => {
      const currentDate = new Date().toISOString().split("T")[0] // Get current date in YYYY-MM-DD format
      const filename = `downloads_${currentDate}.zip`
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      a.remove()
      window.URL.revokeObjectURL(url)
    })
    .catch((error) => {
      console.log(error)
      ElMessage.error("Download failed, please try again later")
    })
}
//#endregion

//#region Query
const translateData = ref<GetTranslateData[]>([])
const searchFormRef = ref<FormInstance | null>(null)
const searchData = reactive({
  keyword: ""
})
const getTableData = () => {
  loading.value = true
  getTranslateDataApi({
    page: paginationData.currentPage,
    limit: paginationData.pageSize,
    keyword: searchData.keyword || undefined
  })
    .then(({ data }) => {
      paginationData.total = data.total
      translateData.value = data.data
    })
    .catch(() => {
      translateData.value = []
    })
    .finally(() => {
      loading.value = false
    })
}
const handleSearch = () => {
  paginationData.currentPage === 1 ? getTableData() : (paginationData.currentPage = 1)
}
const resetSearch = () => {
  searchFormRef.value?.resetFields()
  handleSearch()
}
//#endregion

/** Watch pagination parameter changes */
watch([() => paginationData.currentPage, () => paginationData.pageSize], getTableData, { immediate: true })
</script>

<template>
  <div class="app-container">
    <el-card v-loading="loading" shadow="never">
      <el-form ref="searchFormRef" :inline="true" :model="searchData">
        <el-form-item prop="keyword" label="" style="width: 320px; max-width: 100%">
          <el-input v-model="searchData.keyword" placeholder="Enter search query" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">Search</el-button>
          <el-button :icon="Refresh" @click="resetSearch">Reset</el-button>
          <el-button :icon="Delete" @click="handleMoreDelete">Delete</el-button>
          <el-button :icon="Download" @click="handleMoreDownload">Download</el-button>
        </el-form-item>
      </el-form>
      <div class="table-wrapper">
        <el-table :data="translateData" @selection-change="handleSelectionChange">
          <el-table-column type="selection" width="40" align="left" />
          <el-table-column prop="customer_no" width="70" label="User ID" align="left" />
          <el-table-column prop="customer_email" label="User Email" width="150" align="left" />
          <el-table-column prop="origin_filename" label="Document Name" align="left" />
          <el-table-column prop="status" label="Task Status" align="left" width="120">
            <template #default="scope">
              <el-tag v-if="scope.row.status == 'none'" type="primary" effect="plain">Incomplete</el-tag>
              <el-tag v-else-if="scope.row.status == 'process'" type="warning" effect="plain">In Progress</el-tag>
              <el-tag v-else-if="scope.row.status == 'failed'" type="danger" effect="plain">Failed</el-tag>
              <el-tag v-else type="success" effect="plain">Completed</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="start_at" label="Task Start Time" align="left" />
          <el-table-column prop="spend_time" label="Time Spent" width="100" align="left" />
          <el-table-column prop="deleted_flag" label="User Deleted" align="left" width="120">
            <template #default="scope">
              <el-tag v-if="scope.row.deleted_flag == 'Y'" type="primary" effect="plain">Yes</el-tag>
              <el-tag v-else-if="scope.row.deleted_flag == 'N'" type="warning" effect="plain">No</el-tag>
            </template>
          </el-table-column>
          <el-table-column fixed="right" label="Actions" width="100" align="left">
            <template #default="scope">
              <el-link
                style="color: #409eff; margin-right: 12px"
                v-if="scope.row.target_filepath"
                :href="BASE_URL + '/api/admin/translate/download/' + scope.row.id"
                >Download</el-link
              >
              <el-button type="danger" text size="small" @click="handleDelete(scope.row)">Delete</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <div class="pager-wrapper">
        <el-pagination
          background
          :layout="paginationData.layout"
          :page-sizes="paginationData.pageSizes"
          :total="paginationData.total"
          :page-size="paginationData.pageSize"
          :currentPage="paginationData.currentPage"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<style lang="scss" scoped>
.search-wrapper {
  margin-bottom: 10px;
  :deep(.el-card__body) {
    padding-bottom: 2px;
  }
}

.toolbar-wrapper {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.table-wrapper {
  margin-bottom: 20px;
}

.pager-wrapper {
  display: flex;
  justify-content: flex-end;
}
</style>
