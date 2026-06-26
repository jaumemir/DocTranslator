<script lang="ts" setup>
import { nextTick, reactive, ref } from "vue"
import { type ElMessageBoxOptions, ElMessageBox, ElMessage } from "element-plus"
import { deleteTableDataApi, getTableDataApi } from "@/api/table"
import { type GetTableResponseData } from "@/api/table/types/table"
import RoleColumnSolts from "./tsx/RoleColumnSolts"
import StatusColumnSolts from "./tsx/StatusColumnSolts"
import {
  type VxeGridInstance,
  type VxeGridProps,
  type VxeModalInstance,
  type VxeModalProps,
  type VxeFormInstance,
  type VxeFormProps
} from "vxe-table"

defineOptions({
  // Name the current component
  name: "VxeTable"
})

//#region vxe-grid
interface RowMeta {
  id: string
  username: string
  roles: string
  phone: string
  email: string
  status: boolean
  createTime: string
  /** Attribute automatically added by vxe-table */
  _VXE_ID?: string
}
const xGridDom = ref<VxeGridInstance>()
const xGridOpt: VxeGridProps = reactive({
  loading: true,
  autoResize: true,
  /** Pagination configuration */
  pagerConfig: {
    align: "right"
  },
  /** Form configuration */
  formConfig: {
    items: [
      {
        field: "username",
        itemRender: {
          name: "$input",
          props: { placeholder: "Username", clearable: true }
        }
      },
      {
        field: "phone",
        itemRender: {
          name: "$input",
          props: { placeholder: "Phone", clearable: true }
        }
      },
      {
        itemRender: {
          name: "$buttons",
          children: [
            {
              props: { type: "submit", content: "Search", status: "primary" }
            },
            {
              props: { type: "reset", content: "Reset" }
            }
          ]
        }
      }
    ]
  },
  /** Toolbar configuration */
  toolbarConfig: {
    refresh: true,
    custom: true,
    slots: { buttons: "toolbar-btns" }
  },
  /** Custom column configuration */
  customConfig: {
    /** Whether to allow column selection */
    checkMethod: ({ column }) => !["username"].includes(column.field)
  },
  /** Column configuration */
  columns: [
    {
      type: "checkbox",
      width: "50px"
    },
    {
      field: "username",
      title: "Username"
    },
    {
      field: "roles",
      title: "Role",
      /** Using custom columns with type: "html" columns together will cause errors, so use TSX implementation */
      slots: RoleColumnSolts
    },
    {
      field: "phone",
      title: "Phone"
    },
    {
      field: "email",
      title: "Email"
    },
    {
      field: "status",
      title: "Status",
      slots: StatusColumnSolts
    },
    {
      field: "createTime",
      title: "Create Time"
    },
    {
      title: "Actions",
      width: "150px",
      fixed: "right",
      showOverflow: false,
      slots: { default: "row-operate" }
    }
  ],
  /** Data proxy configuration (based on Promise API) */
  proxyConfig: {
    /** Enable dynamic sequence proxy */
    seq: true,
    /** Whether to proxy form */
    form: true,
    /** Whether to auto load, default is true */
    // autoLoad: false,
    props: {
      total: "total"
    },
    ajax: {
      query: ({ page, form }) => {
        xGridOpt.loading = true
        crudStore.clearTable()
        return new Promise((resolve) => {
          let total = 0
          let result: RowMeta[] = []
          /** Load data */
          const callback = (res: GetTableResponseData) => {
            if (res?.data) {
              // Total
              total = res.data.total
              // List data
              result = res.data.list
            }
            xGridOpt.loading = false
            // Return value has format requirements, see vxe-table official documentation for details
            resolve({ total, result })
          }

          /** Parameters required by API */
          const params = {
            username: form.username || undefined,
            phone: form.phone || undefined,
            size: page.pageSize,
            currentPage: page.currentPage
          }
          /** Call API */
          getTableDataApi(params).then(callback).catch(callback)
        })
      }
    }
  }
})
//#endregion

//#region vxe-modal
const xModalDom = ref<VxeModalInstance>()
const xModalOpt: VxeModalProps = reactive({
  title: "",
  showClose: true,
  escClosable: true,
  maskClosable: true,
  beforeHideMethod: () => {
    xFormDom.value?.clearValidate()
    return Promise.resolve()
  }
})
//#endregion

//#region vxe-form
const xFormDom = ref<VxeFormInstance>()
const xFormOpt: VxeFormProps = reactive({
  span: 24,
  titleWidth: "100px",
  loading: false,
  /** Whether to display title colon */
  titleColon: false,
  /** Form data */
  data: {
    username: "",
    password: ""
  },
  /** Item list */
  items: [
    {
      field: "username",
      title: "Username",
      itemRender: { name: "$input", props: { placeholder: "Please enter" } }
    },
    {
      field: "password",
      title: "Password",
      itemRender: { name: "$input", props: { placeholder: "Please enter" } }
    },
    {
      align: "right",
      itemRender: {
        name: "$buttons",
        children: [
          { props: { content: "Cancel" }, events: { click: () => xModalDom.value?.close() } },
          {
            props: { type: "submit", content: "Confirm", status: "primary" },
            events: { click: () => crudStore.onSubmitForm() }
          }
        ]
      }
    }
  ],
  /** Validation rules */
  rules: {
    username: [
      {
        required: true,
        validator: ({ itemValue }) => {
          switch (true) {
            case !itemValue:
              return new Error("Please enter")
            case !itemValue.trim():
              return new Error("Spaces are invalid")
          }
        }
      }
    ],
    password: [
      {
        required: true,
        validator: ({ itemValue }) => {
          switch (true) {
            case !itemValue:
              return new Error("Please enter")
            case !itemValue.trim():
              return new Error("Spaces are invalid")
          }
        }
      }
    ]
  }
})
//#endregion

//#region CRUD operations
const crudStore = reactive({
  /** Form type, true means update, false means create */
  isUpdate: true,
  /** Load table data */
  commitQuery: () => xGridDom.value?.commitProxy("query"),
  /** Clear table data */
  clearTable: () => xGridDom.value?.reloadData([]),
  /** Click to show modal */
  onShowModal: (row?: RowMeta) => {
    if (row) {
      crudStore.isUpdate = true
      xModalOpt.title = "Edit User"
      // Assign values
      xFormOpt.data.username = row.username
    } else {
      crudStore.isUpdate = false
      xModalOpt.title = "Add User"
    }
    // Disable form item
    const props = xFormOpt.items?.[0]?.itemRender?.props
    props && (props.disabled = crudStore.isUpdate)
    xModalDom.value?.open()
    nextTick(() => {
      !crudStore.isUpdate && xFormDom.value?.reset()
      xFormDom.value?.clearValidate()
    })
  },
  /** Confirm and save */
  onSubmitForm: () => {
    if (xFormOpt.loading) return
    xFormDom.value?.validate((errMap) => {
      if (errMap) return
      xFormOpt.loading = true
      const callback = () => {
        xFormOpt.loading = false
        xModalDom.value?.close()
        ElMessage.success("Operation successful")
        !crudStore.isUpdate && crudStore.afterInsert()
        crudStore.commitQuery()
      }
      if (crudStore.isUpdate) {
        // Simulate successful update API call
        setTimeout(() => callback(), 1000)
      } else {
        // Simulate successful create API call
        setTimeout(() => callback(), 1000)
      }
    })
  },
  /** Whether to jump to last page after insert */
  afterInsert: () => {
    const pager = xGridDom.value?.getProxyInfo()?.pager
    if (pager) {
      const currentTotal = pager.currentPage * pager.pageSize
      if (currentTotal === pager.total) {
        ++pager.currentPage
      }
    }
  },
  /** Delete */
  onDelete: (row: RowMeta) => {
    const tip = `Confirm <strong style="color: var(--el-color-danger);"> delete </strong> user <strong style="color: var(--el-color-primary);"> ${row.username} </strong>?`
    const config: ElMessageBoxOptions = {
      type: "warning",
      showClose: true,
      closeOnClickModal: true,
      closeOnPressEscape: true,
      cancelButtonText: "Cancel",
      confirmButtonText: "Confirm",
      dangerouslyUseHTMLString: true
    }
    ElMessageBox.confirm(tip, "Confirm", config).then(() => {
      deleteTableDataApi(row.id).then(() => {
        ElMessage.success("Delete successful")
        crudStore.afterDelete()
        crudStore.commitQuery()
      })
    })
  },
  /** Whether to return to previous page after delete */
  afterDelete: () => {
    const tableData: RowMeta[] = xGridDom.value!.getData()
    const pager = xGridDom.value?.getProxyInfo()?.pager
    if (pager && pager.currentPage > 1 && tableData.length === 1) {
      --pager.currentPage
    }
  },
  /** More custom methods */
  moreFn: () => {}
})
//#endregion
</script>

<template>
  <div class="app-container">
    <!-- Table -->
    <vxe-grid ref="xGridDom" v-bind="xGridOpt">
      <!-- Left button list -->
      <template #toolbar-btns>
        <vxe-button status="primary" icon="vxe-icon-add" @click="crudStore.onShowModal()">Add User</vxe-button>
        <vxe-button status="danger" icon="vxe-icon-delete">Batch Delete</vxe-button>
      </template>
      <!-- Actions -->
      <template #row-operate="{ row }">
        <el-button link type="primary" @click="crudStore.onShowModal(row)">Edit</el-button>
        <el-button link type="danger" @click="crudStore.onDelete(row)">Delete</el-button>
      </template>
    </vxe-grid>
    <!-- Modal -->
    <vxe-modal ref="xModalDom" v-bind="xModalOpt">
      <!-- Form -->
      <vxe-form ref="xFormDom" v-bind="xFormOpt" />
    </vxe-modal>
  </div>
</template>
