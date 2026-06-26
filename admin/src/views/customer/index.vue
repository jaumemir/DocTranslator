<script lang="ts" setup>
import { reactive, ref, watch } from "vue"
import { changeCustomerStatusApi, updateCustomerDataApi, getCustomerDataApi } from "@/api/customer"
import { type CreateOrUpdateCustomerRequestData, type GetCustomerData } from "@/api/customer/types/customer"
import { type FormInstance, type FormRules, ElMessage } from "element-plus"
import { Search, Refresh, CirclePlus } from "@element-plus/icons-vue"
import { usePagination } from "@/hooks/usePagination"
import { cloneDeep } from "lodash-es"
import Register from "./components/register.vue"

defineOptions({
  // Name the current component
  name: "ElementPlus"
})

const loading = ref<boolean>(false)
const { paginationData, handleCurrentChange, handleSizeChange } = usePagination()

//#region Create
const DEFAULT_FORM_DATA: CreateOrUpdateCustomerRequestData = {
  id: undefined,
  email: "",
  password: "",
  level: "common",
  add_storage: 0
  // status: true
  // storage: 0
}

const dialogVisible = ref<boolean>(false)
const formRef = ref<FormInstance | null>(null)
const formData = ref<CreateOrUpdateCustomerRequestData>(cloneDeep(DEFAULT_FORM_DATA))
const formRules: FormRules<CreateOrUpdateCustomerRequestData> = {
  email: [{ required: true, trigger: "blur", message: "Please enter registration email" }],
  password: [{ min: 6, max: 16, message: "Length must be between 6 and 16 characters", trigger: "blur" }],
  level: [{ required: true, trigger: "blur", message: "Please select user level" }]
}
const handleCreateOrUpdate = () => {
  formRef.value?.validate((valid: boolean, fields) => {
    if (!valid) return console.error("Form validation failed", fields)
    loading.value = true
    // const api = formData.value.id === undefined ? createTableDataApi : updateTableDataApi
    updateCustomerDataApi(formData.value)
      .then(() => {
        ElMessage.success("Operation successful")
        dialogVisible.value = false
        getCustomerData()
      })
      .finally(() => {
        loading.value = false
      })
  })
}
const resetForm = () => {
  formRef.value?.clearValidate()
  formData.value = cloneDeep(DEFAULT_FORM_DATA)
  dialogVisible.value = false
}
//#endregion

//#region Delete
const handleStatus = (id: number, status: string) => {
  changeCustomerStatusApi(id, status).then(() => {
    ElMessage.success("Status changed successfully")
    getCustomerData()
  })
}
//#endregion

//#region Update
const handleUpdate = (row: GetCustomerData) => {
  dialogVisible.value = true
  // formData.value = cloneDeep(row)
  formData.value = Object.assign(cloneDeep(row), { password: "" })
}
//#endregion

//#region Query
const customerData = ref<GetCustomerData[]>([])
const searchFormRef = ref<FormInstance | null>(null)
const searchData = reactive({
  keyword: ""
})
const getCustomerData = () => {
  loading.value = true
  getCustomerDataApi({
    page: paginationData.currentPage,
    limit: paginationData.pageSize,
    keyword: searchData.keyword || undefined
  })
    .then(({ data }) => {
      paginationData.total = data.total
      customerData.value = data.data
    })
    .catch(() => {
      customerData.value = []
    })
    .finally(() => {
      loading.value = false
    })
}
const handleSearch = () => {
  paginationData.currentPage === 1 ? getCustomerData() : (paginationData.currentPage = 1)
}

const resetSearch = () => {
  searchData.keyword = ""
  handleSearch()
}
//#endregion
// Add new user
const registerVisible = ref<boolean>(false)
const newUser = () => {
  registerVisible.value = true
}

const registerSuccess = () => {
  registerVisible.value = false
  getCustomerData()
}

/** Watch pagination parameter changes */
watch([() => paginationData.currentPage, () => paginationData.pageSize], getCustomerData, { immediate: true })
</script>
<template>
  <div class="app-container">
    <el-card v-loading="loading" shadow="never">
      <el-form ref="searchFormRef" :inline="true" :model="searchData">
        <el-form-item prop="username" label="" style="width: 320px; max-width: 100%">
          <el-input v-model="searchData.keyword" placeholder="Enter search query" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">Search</el-button>
          <el-button :icon="Refresh" @click="resetSearch">Reset</el-button>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="CirclePlus" @click="newUser">Add User</el-button>
        </el-form-item>
      </el-form>

      <div class="table-wrapper">
        <el-table :data="customerData">
          <!-- <el-table-column type="selection" width="50" align="center" /> -->
          <el-table-column prop="id" label="User ID" align="left" width="100" />
          <el-table-column prop="email" label="Email" align="left" />
          <el-table-column prop="level" label="User Level" align="left" width="100">
            <template #default="scope">
              <el-tag v-if="scope.row.level == 'vip'" type="primary" effect="plain">VIP User</el-tag>
              <el-tag v-else type="warning" effect="plain">Regular User</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="storage" label="Used Storage" align="left" width="120">
            <template #default="{ row }"> {{ (row.storage / (1024 * 1024)).toFixed(2) }} MB </template>
          </el-table-column>
          <el-table-column prop="storage" label="Total Storage" align="left" width="120">
            <template #default="{ row }"> {{ (row.total_storage / (1024 * 1024)).toFixed(2) }} MB </template>
          </el-table-column>

          <!-- <el-table-column prop="storage" label="Used Storage" align="left" /> -->
          <el-table-column prop="status" label="Account Status" align="left" width="80">
            <template #default="scope">
              <el-tag v-if="scope.row.status == 'enabled'" type="success" effect="plain">Enabled</el-tag>
              <el-tag v-else type="danger" effect="plain">Disabled</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="Registration Time" align="left" />
          <el-table-column fixed="right" label="Actions" width="100" align="left">
            <template #default="scope">
              <el-button type="primary" text size="small" @click="handleUpdate(scope.row)">Edit</el-button>
              <el-button
                type="danger"
                v-if="scope.row.status == 'enabled'"
                text
                size="small"
                @click="handleStatus(scope.row.id, 'disabled')"
                >Disable</el-button
              >
              <el-button type="success" v-else text size="small" @click="handleStatus(scope.row.id, 'enabled')"
                >Enable</el-button
              >
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
    <!-- Add/Edit -->
    <el-dialog modal-class="custom_dialog" v-model="dialogVisible" :show-close="false">
      <template #header>
        <div class="dialog_head">
          <div class="title">{{ formData.id === undefined ? "Add User" : "Edit User Information" }}</div>
          <el-icon @click="resetForm"><Close /></el-icon>
        </div>
      </template>
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="150px" label-position="left">
        <el-form-item prop="email" label="Email">
          <el-input v-model="formData.email" placeholder="Please enter registration email" />
        </el-form-item>
        <el-form-item prop="level" label="User Level">
          <el-select v-model="formData.level" placeholder="">
            <el-option label="VIP User" value="vip" />
            <el-option label="Regular User" value="common" />
          </el-select>
        </el-form-item>
        <!-- Additional storage space field -->
        <el-form-item prop="storage" label="Add Storage (MB)">
          <el-input-number
            style="width: 80%"
            :precision="0"
            v-model="formData.add_storage"
            :step="5"
            placeholder="Please enter storage space to add (MB)"
          />
          <span class="ml-2">MB</span>
        </el-form-item>
        <el-form-item prop="password" label="Password">
          <el-input type="password" v-model="formData.password" placeholder="Please enter" />
        </el-form-item>
      </el-form>
      <div class="btn_box">
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="handleCreateOrUpdate" :loading="loading">Confirm</el-button>
      </div>
    </el-dialog>
    <!-- Registration dialog -->
    <el-dialog
      v-model="registerVisible"
      center
      width="90%"
      modal-class="custom_dialog login_dialog"
      :show-close="false"
    >
      <template #header> Add User </template>
      <Register @success="registerSuccess" />
    </el-dialog>
  </div>
</template>

<style lang="scss" scoped>
.search-wrapper {
  margin-bottom: 20px;
  :deep(.el-card__body) {
    padding-bottom: 2px;
  }
}

.toolbar-wrapper {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.table-wrapper {
  margin-bottom: 20px;
}

.pager-wrapper {
  display: flex;
  justify-content: flex-end;
}
:deep(.custom_dialog) {
  .el-dialog {
    padding: 30px 50px;
    width: 90%;
    max-width: 600px;
    .el-form-item__label {
      justify-content: right;
    }
  }
  .btn_box {
    text-align: right;
  }
  .dialog_head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 10px;
    .title {
      font-weight: bold;
      font-size: 16px;
      color: #333333;
    }
    .el-icon {
      font-size: 20px;
    }
  }
  @media screen and (max-width: 750px) {
    .el-dialog {
      padding: 20px;
    }
  }
}
</style>
