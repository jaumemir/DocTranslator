<template>
  <div
    class="page-center"
    v-loading="pageLoad"
    element-loading-text="loading..."
    element-loading-spinner="el-icon-loading"
    element-loading-background="rgba(255, 255, 255, 0.7)"
  >
    <div class="container">
      <div class="tab_box">
        <div class="tab_li actived">Mine</div>
        <div class="tab_li" @click="$router.push('/corpus/square')">Public</div>
      </div>
      <div class="content_box" v-if="true">
        <div class="flex_box flex-between phone_box">
          <el-button-group>
            <el-button
              :class="tab_active == 'terms' ? 'btn_active' : 'my_button'"
              :plain="tab_active == 'terms' ? false : true"
              :type="tab_active == 'terms' ? 'primary' : ''"
              @click="tabSelect('terms')"
            >
              My Glossaries
            </el-button>
            <el-button
              :class="tab_active == 'prompt' ? 'btn_active' : 'my_button'"
              :plain="tab_active == 'prompt' ? false : true"
              :type="tab_active == 'prompt' ? 'primary' : ''"
              @click="tabSelect('prompt')"
            >
              My Prompts
            </el-button>
          </el-button-group>

          <div class="btn_box" v-if="tab_active == 'terms'">
            <el-button type="primary" color="#055CF9" @click="openTerms">Create</el-button>
            <el-dropdown split-button type="" style="margin: 0 12px" @command="command_terms">
              <el-upload
                name="file"
                :before-upload="upload_before"
                :action="uploadUrl"
                :headers="{ token: userStore.token }"
                :show-file-list="false"
                :on-success="(response, file, fileList) => upload_success(response)"
                class="blue_color"
              >
                Import
              </el-upload>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="down">Download Template</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            <el-button type="" @click="export_terms_all">Export All</el-button>
          </div>

          <div class="btn_box" v-if="tab_active == 'prompt'">
            <el-button type="primary" color="#055CF9" @click="openPrompt">Create</el-button>
          </div>
        </div>
        <!-- Terms list -->
        <div class="term_box" v-if="tab_active == 'terms'">
          <el-row :gutter="24" v-if="termsData.length > 0">
            <el-col :xs="24" :sm="8" v-for="(item, index) in termsData" :key="index">
              <div class="term_li">
                <div class="flex_box title_box flex-between">
                  <div class="t" :title="item.title">{{ item.title }}</div>
                  <div class="des">{{ item.origin_lang }}-{{ item.target_lang }}</div>
                </div>
                <div class="btn_box flex_box flex-between">
                  <div class="left">
                    <el-button type="text" @click="openTerms(item)">Edit</el-button>
                    <el-button type="text" style="color: red" @click="delTerms(item)"
                      >Delete</el-button
                    >
                    <el-button type="text" @click="export_terms(item)">Export</el-button>
                  </div>
                  <div class="right">
                    <el-switch
                      v-model="item.share_flag"
                      active-value="Y"
                      inactive-value="N"
                      @change="share_change(item)"
                    />
                  </div>
                </div>
                <div class="table_box" v-if="item.content.length > 0">
                  <el-table
                    :data="item.content"
                    style="width: 100%"
                    max-height="340"
                    border
                    header-cell-class-name="table_title"
                    tooltip-effect="light"
                  >
                    <el-table-column
                      prop="origin"
                      :label="item.origin_lang"
                      show-overflow-tooltip
                    />
                    <el-table-column
                      prop="target"
                      :label="item.target_lang"
                      show-overflow-tooltip
                    />
                  </el-table>
                </div>
              </div>
            </el-col>
          </el-row>
          <div v-else class="no_data">
            <img src="@/assets/nodata.png" alt="" />
            <div class="text">No data available</div>
          </div>
        </div>
        <!-- Prompts list -->
        <div class="prompt_box" v-if="tab_active == 'prompt'">
          <el-row :gutter="24" v-if="promptData.length > 0">
            <el-col :xs="24" :sm="8" v-for="(item, index) in promptData" :key="index">
              <div class="term_li">
                <div class="flex_box title_box flex-between">
                  <div class="t" :title="item.title">{{ item.title }}</div>
                </div>
                <div class="btn_box flex_box flex-between" v-if="!item.undelete">
                  <div class="left">
                    <el-button type="text" @click="openPrompt(item)">Edit</el-button>
                    <el-button type="text" style="color: red" @click="delPrompt(item)"
                      >Delete</el-button
                    >
                  </div>
                  <div class="right">
                    <el-switch
                      v-model="item.share_flag"
                      active-value="Y"
                      inactive-value="N"
                      @change="share_change_prompt(item)"
                    />
                  </div>
                </div>
                <div class="btn_box" v-else></div>
                <div class="text_box">
                  <div class="text">{{ item.content }}</div>
                </div>
              </div>
            </el-col>
          </el-row>
          <div v-else class="no_data">
            <img src="@/assets/nodata.png" alt="" />
            <div class="text">No data available</div>
          </div>
        </div>
      </div>

      <!-- Filing information -->
      <Filing />
    </div>

    <!-- 术语弹窗 -->
    <TermEdit ref="termEditRef" :langs="langs" :loading="btnLoad" @confirm="handleTermConfirm" />

    <!-- 提示语弹窗 -->
    <PromptEdit ref="promptEditRef" :loading="btnLoad" @confirm="handlePromptConfirm" />
  </div>
</template>

<script setup>
import Filing from '@/components/filing.vue'
import { store } from '@/store/index'
import TermEdit from './components/TermEdit.vue'
import PromptEdit from './components/PromptEdit.vue'
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  comparison_my,
  comparison,
  comparison_edit,
  comparison_del,
  comparison_share,
  prompt_add,
  prompt_edit,
  prompt_my,
  prompt_share,
  prompt_del
} from '@/api/corpus'
import { useUserStore } from '@/store/user'
const userStore = useUserStore()
const uploadUrl = ref(import.meta.env.VITE_API_URL + '/api/comparison/import')
const pageLoad = ref(false)
const termsData = ref([])
const promptData = ref([])
const termEditRef = ref(null)
const btnLoad = ref(false)
const promptEditRef = ref(null)
const tab_active = ref('terms')


// Switch tab
function tabSelect(i) {
  tab_active.value = i
}
// Get terminology data
const getTermList = async () => {
  pageLoad.value = false
  try {
    const res = await comparison_my()
    if (res.code === 200) {
      termsData.value = res.data.data
      // console.log(111, termsData.value)
      // store.setComparisonList(res.data.data)
    }
  } catch (error) {
    console.error('Failed to get terminology data:', error)
  }
  pageLoad.value = false
}

// Get prompt data
const getPromptList = async () => {
  pageLoad.value = false
  try {
    const res = await prompt_my()
    if (res.code === 200) {
      // console.log(6666, res.data)
      promptData.value = JSON.parse(JSON.stringify(res.data.data))
      if (store.prompt) {
        promptData.value.unshift({
          title: '默认提示语(无法Delete)',
          content: store.prompt,
          undelete: true
        })
      }
    }
  } catch (error) {
    console.error('Failed to get prompt data:', error)
  }
  pageLoad.value = false
}

// Translation languages
const langs = ['中文', '英语', '日语', '俄语', '阿拉伯语', '西班牙语', '韩语', '德语']

// Handle prompt dialog save logic
const handlePromptConfirm = (val) => {
  const formData = val
  btnLoad.value = true
  // Check if editing
  if (formData.id) {
    prompt_edit(formData.id, formData)
      .then((data) => {
        btnLoad.value = false
        if (data.code == 200) {
          ElMessage({ message: '保存成功', type: 'success' })
          promptEditRef.value.close()
          getPromptList()
        } else {
          ElMessage({ message: data.message, type: 'error' })
        }
      })
      .catch((err) => {
        ElMessage({ message: '接口异常', type: 'error' })
      })
  } else {
    prompt_add(formData)
      .then((data) => {
        btnLoad.value = false
        if (data.code == 200) {
          ElMessage({ message: '保存成功', type: 'success' })
          promptEditRef.value.close()
          getPromptList()
        } else {
          ElMessage({ message: data.message, type: 'error' })
        }
      })
      .catch((err) => {
        ElMessage({ message: '接口异常', type: 'error' })
      })
  }
  promptEditRef.value.close()
  btnLoad.value = false
}
// Handle terminology form dialog save logic
const handleTermConfirm = (val) => {
  const formData = val
  btnLoad.value = true
  if (formData.id) {
    // Edit operation
    comparison_edit(formData.id, formData)
      .then((data) => {
        btnLoad.value = false
        if (data.code == 200) {
          ElMessage({ message: '保存成功', type: 'success' })
          termEditRef.value.close() // Close child component dialog
          getTermList()
        } else {
          ElMessage({ message: data.message, type: 'error' })
        }
      })
      .catch((err) => {
        ElMessage({ message: '接口异常', type: 'error' })
      })
  } else {
    // Create operation
    comparison(formData)
      .then((data) => {
        btnLoad.value = false
        if (data.code == 200) {
          ElMessage({ message: '保存成功', type: 'success' })
          termEditRef.value.close() // Close child component dialog
          getTermList()
        } else {
          ElMessage({ message: data.message, type: 'error' })
        }
      })
      .catch((err) => {
        ElMessage({ message: '接口异常', type: 'error' })
      })
  }
  termEditRef.value.close()
  btnLoad.value = false
}

// Open terminology dialog - edit
function openTerms(item) {
  termEditRef.value.open() // Open child component dialog
  if (item) {
    termEditRef.value.updateForm(JSON.parse(JSON.stringify(item))) // Update data to child component
  } else {
    termEditRef.value.updateForm({
      title: '', // Title
      share_flag: 'N',
      origin_lang: '',
      target_lang: '',
      content: [{ origin: '', target: '' }]
    })
  }
}
// Open prompt
function openPrompt(item) {
  promptEditRef.value.open()
  if (item) {
    promptEditRef.value.updateForm(JSON.parse(JSON.stringify(item)))
  } else {
    promptEditRef.value.updateForm({
      title: '', // Title
      share_flag: 'N',
      content: ''
    })
  }
}

// Delete terminology
function delTerms(item) {
  ElMessageBox.confirm('确定要Delete？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    pageLoad.value = true
    comparison_del(item.id).then((data) => {
      if (data.code == 200) {
        ElMessage({ message: 'Delete成功', type: 'success' })
        getTermList()
      } else {
        ElMessage({ message: data.message, type: 'error' })
      }
    })
  })
}

// Terminology share status modification
function share_change(item) {
  pageLoad.value = true
  comparison_share(item.id, { share_flag: item.share_flag })
    .then((data) => {
      pageLoad.value = false
      if (data.code == 200) {
        ElMessage({ message: '操作成功', type: 'success' })
      } else {
        ElMessage({ message: data.message, type: 'error' })
        item.share_flag == 'Y' ? (item.share_flag = 'N') : (item.share_flag = 'Y')
      }
    })
    .catch((err) => {
      ElMessage({ message: '接口异常', type: 'error' })
      item.share_flag == 'Y' ? (item.share_flag = 'N') : (item.share_flag = 'Y')
    })
}

// Export single terminology
async function export_terms(item) {
  try {
    // Initiate fetch request
    const response = await fetch(
      `${import.meta.env.VITE_API_URL}/api/comparison/export/${item.id}`,
      {
        headers: {
          token: `${userStore.token}`
        }
      }
    )

    // Check response status
    if (!response.ok) {
      throw new Error('文件下载失败')
    }

    // Get file content
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)

    // Create <a> tag and trigger download
    const a = document.createElement('a')
    a.href = url
    a.download = `${item.title}.xlsx` // Set download filename
    document.body.appendChild(a)
    a.click()
    // Clean up resources
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url) // Release URL object
  } catch (error) {
    console.error('Download failed:', error)
    ElMessage.error('文件下载失败，请稍后重试')
  }
}

// Export all terminology
async function export_terms_all() {
  try {
    const response = await fetch(import.meta.env.VITE_API_URL + '/api/comparison/export/all', {
      headers: {
        token: `${userStore.token}`
      }
    })

    if (!response.ok) {
      throw new Error('术语表Export失败')
    }

    // Get file content
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)

    // Create <a> tag and trigger download
    const a = document.createElement('a')
    a.href = url
    a.download = `all_terms_${new Date().toISOString().slice(0, 10)}.zip` // Set download filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url) // Release URL object
  } catch (error) {
    console.error('Export failed:', error)
    ElMessage.error('术语表Export失败，请稍后重试')
  }
}

// Terminology template download
function command_terms(type) {
  if (type == 'down') {
    window.open(import.meta.env.VITE_API_URL + '/api/comparison/template')
  }
}

// Upload file success
function upload_success(response) {
  if (response.code == 200) {
    ElMessage({ message: '导入成功', type: 'success' })
    getTermList()
  } else {
    ElMessage({ message: data.message, type: 'error' })
  }
}
// Upload file validation
function upload_before(file) {
  const fileType = file.name.substring(file.name.lastIndexOf('.') + 1)
  const isXlsx = fileType === 'xlsx'
  if (!isXlsx) {
    ElMessage({ message: '请上传模板格式的文件', type: 'error' })
    return false
  }
  return isXlsx
}

// Prompt share status modification
function share_change_prompt(item) {
  pageLoad.value = true
  if (item.id) {
    prompt_share(item.id, { share_flag: item.share_flag })
      .then((data) => {
        pageLoad.value = false
        if (data.code == 200) {
          ElMessage({ message: '操作成功', type: 'success' })
        } else {
          ElMessage({ message: data.message, type: 'error' })
          item.share_flag == 'Y' ? (item.share_flag = 'N') : (item.share_flag = 'Y')
        }
      })
      .catch((err) => {
        ElMessage({ message: '接口异常', type: 'error' })
        item.share_flag == 'Y' ? (item.share_flag = 'N') : (item.share_flag = 'Y')
      })
  }
}

// Delete prompt
function delPrompt(item) {
  ElMessageBox.confirm('确定要Delete？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    pageLoad.value = true
    prompt_del(item.id).then((data) => {
      if (data.code == 200) {
        ElMessage({ message: 'Delete成功', type: 'success' })
        getPromptList()
      } else {
        ElMessage({ message: data.message, type: 'error' })
      }
    })
  })
}
onMounted(() => {
  getTermList()
  getPromptList()
})
</script>

<style scoped lang="scss">
.page-center {
  flex: 1;
  overflow-y: auto;
}
.container {
  max-width: 1240px;
  margin: 0 auto;
  padding: 0 20px;
  padding-bottom: 20px;
}
// Tab labels
.tab_box {
  width: 100%;
  height: 68px;
  display: flex;
  align-items: center;
  .tab_li {
    width: 80px;
    height: 36px;
    box-sizing: border-box;
    border-radius: 4px;
    text-align: center;
    line-height: 34px;
    cursor: pointer;
    font-size: 16px;
    color: #284272;
    box-shadow: 0px 2px 4px 0px rgba(5, 92, 249, 0.1);
    border-radius: 4px;
    border: 1px solid #e0e5ed;
    margin-right: 16px;
    background: #fff;
    &.actived {
      background: #055cf9;
      border-color: #055cf9;
      color: #ffffff;
      font-weight: bold;
    }
  }
}
// Main content area
.content_box {
  background: #fff;
  padding: 28px;
  padding-bottom: 8px;
  .term_box {
    margin-top: 20px;
  }
  .prompt_box {
    margin-top: 20px;
  }
  .term_li {
    width: 100%;
    background: #ffffff;
    border-radius: 4px;
    border: 1px solid #b8d3ff;
    overflow: hidden;
    margin-bottom: 20px;
    .title_box {
      height: 40px;
      background: #f1f6ff;
      border-bottom: 1px solid #b8d3ff;
      padding: 0 20px;
      .t {
        flex: 1;
        margin-right: 20px;
        font-weight: bold;
        font-size: 14px;
        color: #055cf9;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
      .des {
        font-size: 14px;
        color: #111111;
      }
    }
    .btn_box {
      padding: 0 20px;
      height: 50px;
    }
    .table_box {
      height: 364px;
      padding: 0 20px;
    }
    .text_box {
      padding: 0 20px;
      padding-bottom: 22px;
      .text {
        box-sizing: border-box;
        height: 340px;
        border: 1px solid #dcdee2;
        padding: 10px 20px;
        font-size: 14px;
        color: #111111;
        line-height: 28px;
        word-break: break-word;
        overflow-y: auto;
        &.disabled {
          color: #284272;
          background: #b8d3ff;
        }
      }
      // Scrollbar styles
      .text::-webkit-scrollbar {
        width: 4px;
      }
      .text::-webkit-scrollbar-thumb {
        border-radius: 10px;
        -webkit-box-shadow: inset 0 0 5px rgba(0, 0, 0, 0.2);
        opacity: 0.2;
        background: fade(#d8d8d8, 60%);
      }
      .text::-webkit-scrollbar-track {
        -webkit-box-shadow: inset 0 0 5px rgba(0, 0, 0, 0.2);
        border-radius: 0;
        background: fade(#d8d8d8, 30%);
      }
    }
  }
}

.no_data {
  text-align: center;
  img {
    margin-top: 50px;
    max-width: 100%;
  }
  .text {
    font-size: 16px;
    color: #8b8c9f;
    margin-top: 30px;
    margin-bottom: 120px;
  }
}

::v-deep {
  // Dialog
  .term_dialog {
    padding-top: 20px;
    .el-dialog {
      max-width: 740px;
      padding: 30px 50px;
    }
    .el-dialog__header {
      font-weight: bold;
      font-size: 18px;
      color: #111;
      padding: 0 20px;
      margin-bottom: 16px;
      .title {
        display: inline-block;
        line-height: 32px;
        margin-right: 30px;
      }
      .flag_tips {
        display: inline-block;
        line-height: 32px;
        font-size: 14px;
        color: #111;
        font-weight: normal;
        margin-left: 10px;
      }
    }
    .el-dialog__headerbtn {
      font-size: 20px;
      right: 10px;
      top: 10px;
      i {
        color: #111;
      }
    }
    .el-dialog__body {
      padding: 0px 20px;
      max-height: 450px;
      overflow-y: auto;
    }
    .el-form-item {
      .el-form-item__label {
        justify-content: flex-start;
        color: #111111;
      }
      .el-input-number .el-input__inner {
        text-align: left;
      }
    }
    .btn_box {
      position: relative;
      text-align: center;
    }

    .term_custom {
      width: 100%;
      .label {
        line-height: 22px;
        margin-bottom: 8px;
      }
      .el-button {
        height: auto;
        margin-bottom: 10px;
        padding: 0;
        margin-right: 20px;
      }
      .button_box {
        display: flex;
      }
      .icon_add {
        font-size: 14px;
        color: #ffffff;
        width: 20px;
        height: 20px;
        line-height: 20px;
        background: #055cf9;
        border-radius: 3px;
        text-align: center;
      }
    }
    .term_set_li {
      width: 100%;
      align-items: flex-start;
      .form {
        flex: 1;
        margin-right: 20px;
      }
      .icon_del {
        font-size: 14px;
        color: #ffffff;
        width: 20px;
        height: 20px;
        line-height: 20px;
        background: #ed4014;
        border-radius: 3px;
        text-align: center;
        margin-top: 5px;
      }
    }
    .tips {
      font-size: 14px;
      color: #111111;
      line-height: 24px;
      margin-bottom: 10px;
    }
    .el-switch__core .el-switch__action {
      top: 1px;
    }
  }

  .table_title {
    color: #111111;
  }
  .btn_active {
    background: #eff5ff;
    border-color: #eff5ff;
    color: #055cf9;
  }
  .my_button {
    border-color: #eef3fa;
  }
  tbody {
    outline: none;
  }

  .el-popper {
    max-width: 300px;
  }
}
@media screen and (max-width: 767px) {
  .phone_box {
    flex-direction: column;
    align-items: flex-start;
    .btn_box {
      margin-top: 12px;
    }
  }
  ::v-deep {
    .term_dialog {
      .el-dialog {
        padding: 20px !important;
      }
      .el-dialog__body {
        max-height: 300px;
      }
    }
  }
  .table_box {
    height: auto !important;
    margin-bottom: 20px;
  }
  .no_data {
    .text {
      margin-bottom: 20px;
    }
  }

  /*手机端布局调整*/
  .container {
    padding: 0 16px;
  }
  .content_box {
    padding: 20px 14px;
  }
  .term_box {
    margin-top: 16px;
  }
  .term_li .title_box {
    padding: 0 13px !important;
  }
  .term_li .table_box {
    padding: 0 13px !important;
  }
  .term_li .text_box {
    padding: 0 13px !important;
    padding-bottom: 20px !important;
  }
  .term_li .btn_box {
    padding: 0 13px !important;
  }
  .term_box .el-col:last-child .term_li {
    margin-bottom: 0;
  }
}
</style>
