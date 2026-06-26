<template>
  <div class="page-center">
    <div class="container">
      <div class="upload-container">
        <el-upload
          ref="uploadRef"
          class="dropzone"
          drag
          multiple
          :action="upload_url"
          :accept="accepts"
          auto-upload
          :limit="5"
          :on-success="uploadSuccess"
          :on-error="uploadError"
          :headers="{ token: userStore.token }"
          :before-upload="beforeUpload"
          :before-remove="delUploadFile"
          :on-change="(file, fileList) => flhandleFileListChange(file, fileList)"
        >
          <div class="left_box pc_show">
            <div class="icon_box" v-if="!fileListShow">
              <img src="@/assets/icon_a.png" />
              <img src="@/assets/icon_w.png" />
              <img src="@/assets/icon_p.png" />
              <img src="@/assets/icon_x.png" />
            </div>
          </div>
          <div class="right_box">
            <div class="title pc_show">Drag & drop or click to select documents</div>
            <button class="upload_btn" type="button">
              <img :src="uploadPng" />
              <span>Upload Document</span>
            </button>
            <div class="title phone_show">Click button to select documents</div>
            <div class="tips">Supported formats: {{ accpet_tip }}, recommended file size ≤50MB</div>
          </div>
        </el-upload>
      </div>
      <!-- Translation list table display -->
      <div class="list_box">
        <div class="title_box">
          <div class="t">
            <div class="t_left">
              <span>Translation Task List</span>
              <div class="tips" v-if="false">
                <el-icon><SuccessFilled /></el-icon>
                Successfully translated
                <span>{{ transCount }}</span>
                files
              </div>
            </div>

            <div class="t_right">
              <el-button
                type="text"
                class="phone_show"
                @click="downAllTransFile"
                v-if="editionInfo !== 'community' && translatesData.length > 0"
              >
                Download All
              </el-button>
              <el-button
                type="text"
                class="phone_show"
                @click="delAllTransFile"
                v-if="translatesData && translatesData.length > 0"
              >
                Delete All
              </el-button>
            </div>
          </div>
          <!-- Storage space display -->
          <div class="t_right">
            <span class="storage">Storage Space ({{ storageTotal }}M)</span>
            <el-progress
              class="translated-process"
              :percentage="storagePercentage"
              color="#055CF9"
            />
            <el-button
              class="pc_show all_down"
              @click="downAllTransFile"
              v-if="translatesData.length > 0"
            >
              Download All
            </el-button>
            <el-button class="pc_show" @click="delAllTransFile" v-if="translatesData.length > 0"
              >Delete All</el-button
            >
          </div>
          <!-- <div class="t_right">
            <el-button class="pc_show" @click="delAllTransFile" v-if="translatesData.length > 0"
              >全部删除</el-button
            >
          </div> -->
        </div>
        <!-- Translation list table data -->
        <div class="table_box" v-loading="isLoadingData" element-loading-text="Loading...">
          <div class="table_row table_top pc_show">
            <div class="table_li">Document Name</div>
            <div class="table_li">Task Status</div>
            <div class="table_li">Duration</div>
            <div class="table_li">Completion Time</div>
            <div class="table_li">Language</div>
            <div class="table_li">Actions</div>
          </div>
          <div class="table_row phone_row" v-for="(res, index) in result" :key="index">
            <div class="table_li">
              <img v-if="res.file_type == 'pptx' || res.file_type == 'PPT'" src="@assets/PPT.png" alt="" />
              <img v-else-if="res.file_type == 'docx' || res.file_type == 'Word'" src="@assets/DOC.png" alt="" />
              <img v-else-if="res.file_type == 'xlsx' || res.file_type == 'Excel'" src="@assets/Excel.png" alt="" />
              <img v-else-if="res.file_type == 'html' || res.file_type == 'HTML'" src="@assets/DOC.png" alt="" />
              <img v-else src="@assets/PDF.png" alt="" />
              <span class="file_name">{{ res.file_name }}</span>
            </div>
            <div class="table_li status">
              <el-progress
                class="translated-process"
                :percentage="res['percentage']"
                color="#055CF9"
              >
                <template #default="{ percentage }">
                  <span class="percentage">{{ percentage }}%</span>
                </template>
              </el-progress>
              <img src="@assets/waring.gif" alt="" />
              <span class="process">Translating</span>
            </div>
            <div class="table_li pc_show">--</div>
            <div class="table_li pc_show">--</div>
            <div class="table_li pc_show">{{ res.lang }}</div>
            <div class="table_li pc_show">
              <img src="@assets/icon_no_down.png" alt="" />
            </div>
          </div>

          <div class="table_row phone_row" v-for="(item, index) in translatesData" :key="index">
            <div class="table_li">
              <img v-if="item.file_type == 'pptx' || item.file_type == 'PPT'" src="@assets/PPT.png" alt="" />
              <img v-else-if="item.file_type == 'docx' || item.file_type == 'Word'" src="@assets/DOC.png" alt="" />
              <img v-else-if="item.file_type == 'xlsx' || item.file_type == 'Excel'" src="@assets/Excel.png" alt="" />
              <img v-else-if="item.file_type == 'html' || item.file_type == 'HTML'" src="@assets/DOC.png" alt="" />
              <img v-else src="@assets/PDF.png" alt="" />
              <span class="file_name">{{ item.origin_filename }}</span>
            </div>
            <div :class="item.status == 'done' ? 'pc_show table_li status' : 'table_li status'">
              <el-progress class="translated-process" :percentage="item.process" color="#055CF9" />
              <img v-if="item.status == 'none'" src="@assets/waring.png" alt="Not Started" />
              <img v-if="item.status == 'done'" src="@assets/success.png" alt="Completed" />
              <img v-if="item.status == 'process'" src="@assets/waring.png" alt="In Progress" />
              <img v-if="item.status == 'failed'" src="@assets/waring.png" alt="Failed" />
              <span :class="item.status">{{ item.status_name }}</span>
            </div>
            <div :class="item.status == 'done' ? 'table_li' : 'table_li pc_show'">
              <span class="phone_show">Duration:</span>
              {{ item.spend_time ? item.spend_time : '--' }}
            </div>
            <div :class="item.status == 'done' ? 'table_li' : 'table_li pc_show'">
              <span class="phone_show">Completion Time:</span>
              {{ item.end_at ? item.end_at : '--' }}
            </div>
            <div :class="item.status == 'done' ? 'table_li' : 'table_li pc_show'">
              <span class="phone_show">Language:</span>
              {{ item.lang ? item.lang : '--' }}
            </div>
            <!-- Actions -->
            <div class="table_li">
              <!-- Translation success icon -->
              <template v-if="item.status == 'done'">
                <el-button
                  type="text"
                  class="icon_down"
                  @click.stop="downloadTranslateFile(item.id, item.origin_filename)"
                >
                  <span class="icon_handle">
                    <DownloadIcon />
                  </span>
                </el-button>
              </template>
              <!-- Retry icon for failed -->
              <template v-if="item.status == 'failed' || item.status == 'none'">
                <span class="icon_handle" @click="retryTranslate(item)">
                  <RetryIcon />
                </span>
              </template>

              <!-- Delete icon -->
              <span class="icon_handle" @click="delTransFile(item.id, index)">
                <DeleteIcon />
              </span>
            </div>
          </div>
          <div
            v-if="no_data"
            class="table_row no_data"
            style="border: none; padding-top: 15px; justify-content: center; color: #c4c4c4"
          >
            No data available
          </div>
        </div>
      </div>

      <!-- Filing information -->
      <Filing />
    </div>

    <!-- PC translate button -->
    <div class="fixed_bottom">
      <el-button
        type="primary"
        :disabled="upload_load"
        size="large"
        color="#055CF9"
        class="translate-btn"
        @click="handleTranslate(transform)"
      >
        Translate Now
      </el-button>
    </div>
  </div>
</template>
<script setup>
import Filing from '@/components/filing.vue'
import RetryIcon from '@/components/icons/RetryIcon.vue'
import DeleteIcon from '../../components/icons/DeleteIcon.vue'
import DownloadIcon from '../../components/icons/DownloadIcon.vue'
import { ref, computed, onMounted, onUnmounted } from 'vue'
const API_URL = import.meta.env.VITE_API_URL
import {
  checkPdf,
  transalteFile,
  transalteProcess,
  delFile,
  translates,
  delTranslate,
  delAllTranslate,
  downAllTranslate,
  doc2xStartService,
  doc2xQueryStatusService,
  getFinishCount
} from '@/api/trans'
import { storage } from '@/api/account'
import uploadPng from '@assets/upload.png'
import { ElMessage, ElMessageBox, ElLoading } from 'element-plus'
import { useTranslateStore } from '@/store/translate'
import { useUserStore } from '@/store/user'
const userStore = useUserStore()
const translateStore = useTranslateStore()

// Current translation service computed
const currentServiceType = computed(() => translateStore.currentService)

// Translation data table loading state
const isLoadingData = ref(true)
const upload_load = ref(false)
const no_data = ref(true)

const accepts = '.docx,.xlsx,.pptx,.pdf,.txt,.csv,.md,.html,.htm'
const fileListShow = ref(false)
// Store UUIDs of tasks currently being polled
const pollingTasks = ref(new Set())
const upload_url = API_URL + '/api/upload'
const translatesData = ref([])
const translatesTotal = ref(0)
const translatesLimit = ref(100)
const storageTotal = ref(0)
const storageUsed = ref(0)
const storagePercentage = ref(0.0)

// Version status information
const editionInfo = ref(false)
// Cumulative translation count
const transCount = ref(0)
const uploadRef = ref(null)

const form = ref({
  files: [],
  file_name: '',
  api_url: 'https://api.openai.com',
  api_key: null,
  app_key: null,
  app_id: null,
  model: '',
  backup_model: '',
  langs: [],
  lang: '',
  to_lang: null,
  type: [],
  uuid: '',
  prompt:
    'You are a document translation assistant. Please translate the following text, words, or phrases directly into {target_lang} without returning the original text. If the text contains {target_lang} text, special terms (such as email addresses, brand names, unit nouns like mm, px, ℃, etc.), or untranslatable content, return the original text without explanation. Return the original content for untranslatable text. Preserve extra spaces.',
  threads: 10,
  size: 0,
  scanned: false,
  origin_lang: '',
  comparison_id: '',
  prompt_id: '',
  translate_id: null,
  doc2x_secret_key: '',
  doc2x_flag: 'N'
})

// Download translated file
const downloadTranslateFile = async (id, filename) => {
  try {
    const loading = ElLoading.service({
      lock: true,
      text: 'Downloading file...',
      background: 'rgba(0, 0, 0, 0.1)'
    })

    const response = await fetch(`${API_URL}/api/translate/download/${id}`, {
      method: 'GET',
      headers: {
        token: userStore.token
      }
    })

    if (!response.ok) {
      let errorMessage = 'Download failed'
      if (response.status === 401) {
        errorMessage = 'Login expired, please login again'
      } else if (response.status === 403) {
        errorMessage = 'No download permission'
      } else if (response.status === 404) {
        errorMessage = 'File does not exist'
      }
      throw new Error(errorMessage)
    }

    // Prioritize using the passed filename parameter
    let downloadFilename = filename

    // If no filename passed, try to get it from server
    if (!downloadFilename) {
      const contentDisposition = response.headers.get('content-disposition')
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
        if (filenameMatch && filenameMatch[1]) {
          downloadFilename = filenameMatch[1].replace(/['"]/g, '')
        }
      }
    }

    // If still no filename, use default value
    if (!downloadFilename) {
      downloadFilename = `translated_file_${id}`
    }

    // Clean filename (remove special chars but keep extension)
    const cleanFilename = downloadFilename.replace(/[<>:"/\\|?*]/g, '_')

    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)

    const a = document.createElement('a')
    a.href = url
    a.download = cleanFilename
    a.style.display = 'none'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)

    loading.close()
    ElMessage.success('File downloaded successfully')
  } catch (error) {
    console.error('Download failed:', error)
    ElMessage.error(error.message || '文件Download failed，请稍后重试')
  }
}

const accpet_tip = computed(() => {
  return accepts.split(',').join('/')
})

// Get translation count
function getCount() {
  getFinishCount().then((data) => {
    if (data.code == 200) {
      transCount.value = data.data.total
    }
  })
}

function flhandleFileListChange(file, fileList) {
  fileListShow.value = fileList.length > 0 ? true : false
}

// Progress query status: "done"
function process(uuid) {
  // Check if task is still in progress
  if (!pollingTasks.value.has(uuid)) {
    return
  }

  // Call translation processing function
  transalteProcess({ uuid })
    .then((res) => {
      if (res.code == 200) {
        // Find and update corresponding task in translatesData
        const taskIndex = translatesData.value.findIndex((item) => item.uuid === uuid)

        if (taskIndex !== -1) {
          // Update task progress
          translatesData.value[taskIndex].process = res.data.progress
          translatesData.value[taskIndex].status = res.data.status
          translatesData.value[taskIndex].status_name =
            res.data.status === 'process'
              ? 'Translating'
              : res.data.status === 'done'
                ? 'Completed'
                : res.data.status === 'failed'
                  ? 'Failed'
                  : 'Not Started'
        }

        // If returned field explicitly indicates task failure
        if (res.data.status === 'failed') {
          // Handle task failure
          ElMessage({
            message: res.data.message || 'Translation failed',
            type: 'error',
            duration: 5000
          })
          // Remove from polling tasks
          pollingTasks.value.delete(uuid)
          // Update translation task list
          getTranslatesData(1)
          return // Return directly, don't continue querying
        }

        // When task completes
        if (res.data.progress == 100) {
          // When task completes，更新翻译任务列表
          ElMessage.success({
            message: 'File translated successfully!'
          })
          // Remove from polling tasks
          pollingTasks.value.delete(uuid)
          getTranslatesData(1)
        } else {
          // If not complete, continue calling process function
          setTimeout(() => process(uuid), 10000) // Request once every 10 seconds
        }
      } else {
        // Handle error cases (res.code != 200)
        ElMessage({
          message: res.message || 'Failed to query task progress',
          type: 'error',
          duration: 5000
        })
        // Remove from polling tasks
        pollingTasks.value.delete(uuid)
        // When task fails, update translation task list
        getTranslatesData(1)
      }
    })
    .catch((error) => {
      // 处理网络错误或Other异常
      ElMessage({
        message: 'Translation process failed.',
        type: 'error',
        duration: 5000
      })
      // Remove from polling tasks
      pollingTasks.value.delete(uuid)
      // When task fails, update translation task list
      getTranslatesData(1)
    })
}

// doc2x progress query
const doc2xStatusQuery = async (data) => {
  const res = await doc2xQueryStatusService(data)
  if (res.code == 200) {
    console.log('doc2x progress query', res.data)
    // If returned field explicitly indicates task failure
    if (res.data.status === 'failed') {
      // Handle task failure
      ElMessage({
        message: 'Translation failed' || 'Unknown error',
        type: 'error',
        duration: 5000
      })
      // Update translation task list
      getTranslatesData(1)
      return // Return directly, don't continue querying
    } else if (res.data.status == 'done') {
      // When task completes，更新翻译任务列表
      ElMessage.success({
        message: 'File translated successfully!'
      })
      getTranslatesData(1)
    } else {
      // If not complete, continue calling process function
      setTimeout(() => doc2xStatusQuery(data), 10000)
    }
  } else {
    // Handle error cases (res.code != 200)
    ElMessage({
      message: res.message || 'Failed to query task progress',
      type: 'error',
      duration: 5000
    })
    // When task fails, update translation task list
    getTranslatesData(1)
  }
}

// 启动翻译-----立即翻译-------
async function handleTranslate(transform) {
  // 首先再次赋值，防止没有更新
  form.value = { ...form.value, ...translateStore.getCurrentServiceForm }

  const file_suffix = form.value.files[0].file_name.split('.').pop().toLowerCase()

  // 先判断是不是pdf文件和是否启用doc2x
  if (
    file_suffix == 'pdf' &&
    translateStore.common.doc2x_flag == 'Y' &&
    translateStore.common.doc2x_secret_key !== ''
  ) {
    form.value.server = 'doc2x'

    // 1.启动doc2x翻译
    const res = await doc2xStartService(form.value)
    if (res.code == 200) {
      ElMessage({
        message: 'doc2x translation task submitted successfully!',
        type: 'success'
      })
      // 更新uuid
      form.value.uuid = res.data.uuid
      // 刷新翻译列表
      getTranslatesData(1)
      // 启动任务查询
      doc2xStatusQuery({ translate_id: form.value.translate_id })
    } else {
      ElMessage({
        message: 'Failed to submit translation task',
        type: 'error'
      })
    }
    // 4.清空上传文件列表
    uploadRef.value.clearFiles()
    return res
  }

  if (currentServiceType.value == 'ai') {
    // 2.检查翻译设置是否完整
    if (form.value.server === '') {
      ElMessage({
        message: 'Please select a translation service provider',
        type: 'error'
      })
      return
    }

    if (form.value.type === '') {
      ElMessage({
        message: 'Please select translation type',
        type: 'error'
      })
      return
    }

    if (form.value.model === '') {
      ElMessage({
        message: 'Please select translation model',
        type: 'error'
      })
      return
    }

    if (form.value.langs.length < 1) {
      ElMessage({
        message: 'Please select target language',
        type: 'error'
      })
      return
    }

    if (form.value.prompt === '') {
      ElMessage({
        message: 'Please enter translation prompt',
        type: 'error'
      })
      return
    }
    // 翻译服务 检查api密钥是否为空 会员不需要提供key
    if (form.value.api_key === '' && !userStore.isVip) {
      ElMessage({
        message: 'Please enter API key',
        type: 'error'
      })
      return
    }
  } else if (currentServiceType.value == 'baidu') {
    if (form.value.app_key === '' || form.value.app_id === '' || form.value.to_lang === '') {
      ElMessage({
        message: 'Please fill in Baidu Translate information!',
        type: 'error'
      })
      return
    }
  }

  // 3.提交翻译任务
  // 如果是会员，不需要提供api和key
  form.value.api_key = userStore.isVip ? '' : form.value.api_key
  form.value.api_url = userStore.isVip ? '' : form.value.api_url

  console.log('Translation form:', form.value)
  const res = await transalteFile(form.value)
  if (res.code == 200) {
    ElMessage({
      message: 'Translation task submitted successfully!',
      type: 'success'
    })

    // 添加到轮询任务集合
    pollingTasks.value.add(form.value.uuid)

    // 刷新翻译列表
    getTranslatesData(1)
    // 启动任务查询
    process(form.value.uuid)
  } else {
    ElMessage({
      message: 'Failed to submit translation task',
      type: 'error'
    })
  }

  // 4.清空上传文件列表
  uploadRef.value.clearFiles()
}

// 重启翻译任务
async function retryTranslate(item) {
  form.value.uuid = item.uuid
  form.value.file_name = item.origin_filename

  // 先判断是不是doc2x失败
  if (item.server == 'doc2x') {
    // 1.启动doc2x翻译
    const res = await doc2xStartService(form.value)
    if (res.code == 200) {
      ElMessage({
        message: 'doc2x translation task submitted successfully!',
        type: 'success'
      })
      // 刷新翻译列表
      getTranslatesData(1)
      // 启动任务查询
      doc2xStatusQuery({ translate_id: item.id })
    } else {
      ElMessage({
        message: 'Failed to submit doc2x task',
        type: 'error'
      })
    }
    return
  }

  // 3.重启翻译任务
  const res = await transalteFile(form.value)
  if (res.code == 200) {
    ElMessage({
      message: 'Translation task started successfully!',
      type: 'success'
    })

    // 添加到轮询任务集合
    pollingTasks.value.add(item.uuid)

    // 刷新翻译列表
    getTranslatesData(1)
    // 启动任务查询
    process(form.value.uuid)
  } else {
    ElMessage({
      message: 'Failed to start translation task',
      type: 'error'
    })
  }
}

// 上传之前
function beforeUpload(file) {
  if (!userStore.token) {
    return false
  }
  let ext = file.name.split('.').pop()
  if (!accepts.split(',').includes('.' + ext)) {
    ElMessage({
      message: 'This file format is not supported',
      type: 'error',
      duration: 5000
    })
    return false
  }
  upload_load.value = true
}

// 上传成功
function uploadSuccess(res, file) {
  if (res.code == 200) {
    const uploadedFile = {
      file_path: res.data.filepath,
      file_name: res.data.filename,
      uuid: res.data.uuid
    }
    form.value.file_name = res.data.filename
    form.value.files.push(uploadedFile)
    // 更新文件大小
    form.value.size = file.size
    // 获取到uuid和translate_id
    form.value.uuid = res.data.uuid
    form.value.translate_id = res.data.translate_id
    // 更新存储空间
    getStorageInfo()
  } else {
    ElMessage({
      message: res.message,
      type: 'error'
    })
  }
  setTimeout(() => {
    upload_load.value = false
  }, 1000)
}

function uploadError(data) {
  ElMessage({
    message: `上传失败，${JSON.parse(data.message).message}`,
    type: 'error'
  })
}

function delUploadFile(file, files) {
  let filepath = ''
  let uuid = '' // 初始化 uuid 变量
  form.value.files.forEach((item, index) => {
    if (item.file_name === file.name) {
      filepath = item.file_path
      uuid = item.uuid // 获取要删除文件的 uuid
      form.value.files.splice(index, 1)
    }
  })

  // 停止对该任务的轮询
  pollingTasks.value.delete(uuid)

  // 删除文件
  delFile({ filepath, uuid })
    .then((response) => {
      if (response.code === 200) {
        ElMessage({
          message: 'File deleted successfully',
          type: 'success'
        })
        // 更新存储空间
        getStorageInfo()
      } else {
        ElMessage({
          message: 'File deletion failed, please try again later',
          type: 'error'
        })
      }
    })
    .catch((error) => {
      ElMessage({
        message: 'File deletion failed, please try again later',
        type: 'error'
      })
    })

  // 更新 fileListShow 状态
  if (files.length <= 1) {
    fileListShow.value = false
  }
}

//获取翻译列表数据
async function getTranslatesData(page, uuid) {
  isLoadingData.value = true

  await translates({ page, limit: translatesLimit.value }).then((data) => {
    if (data.code == 200) {
      data.data.data.forEach((item) => {
        let fileArr = item.origin_filename.split('.')
        let fileType = fileArr[fileArr.length - 1]
        let fileType_f = ''
        if (item.file_type) {
          fileType_f = item.file_type
        } else if (fileType == 'docx' || fileType == 'doc') {
          fileType_f = 'Word'
        } else if (fileType == 'xlsx' || fileType == 'xls') {
          fileType_f = 'Excel'
        } else if (fileType == 'pptx') {
          fileType_f = 'PPT'
        } else if (fileType == 'pdf') {
          fileType_f = 'PDF'
        } else if (fileType == 'html' || fileType == 'htm') {
          fileType_f = 'HTML'
        } else if (fileType == 'txt' || fileType == 'md') {
          fileType_f = 'Text'
        } else {
          fileType_f = 'Other'
        }
        item.file_type = fileType_f
      })
      translatesData.value = data.data.data
      translatesTotal.value = data.data.total
      if (translatesData.value.length > 0) {
        no_data.value = false
      } else {
        no_data.value = true
      }
      // 切换状态
      isLoadingData.value = false
    }
  })
  // 切换状态
  isLoadingData.value = false
  getStorageInfo()
  getCount()
}

//获取存储空间等信息的方法
function getStorageInfo() {
  storage().then((res) => {
    if (res.code == 200) {
      const storage = res.data.used_storage
      const total_storage = res.data.total_storage
      // 更新存储空间
      userStore.updateStorage({ storage, total_storage })
      storageTotal.value = (res.data.total_storage / (1024 * 1024)).toFixed(2)
      storageUsed.value = res.data.used_storage
      storagePercentage.value = res.data.percentage
    }
  })
}

async function delTransFile(id, index) {
  try {
    await ElMessageBox.confirm('Are you sure you want to delete?', 'Notice', {
      confirmButtonText: 'Confirm',
      cancelButtonText: 'Cancel',
      type: 'warning'
    })
    isLoadingData.value = true

    // 获取要删除任务的uuid
    const taskToDelete = translatesData.value[index]
    if (taskToDelete) {
      pollingTasks.value.delete(taskToDelete.uuid)
    }

    translatesData.value.splice(index, 1)
    if (translatesData.value.length < 1) {
      no_data.value = true
    }

    const res = await delTranslate(id)
    if (res.code == 200) {
      translatesData.value = translatesData.value.filter((item) => item.id != id)
      if (translatesData.value.length < 1) {
        no_data.value = true
      }
      isLoadingData.value = false
      ElMessage.success('Deleted successfully')
      getStorageInfo()
    }
  } catch (error) {
    // 用户点击Cancel或请求失败
    console.log('删除操作已Cancel或失败:', error)
    isLoadingData.value = false
  }
}

//全部删除的方法
function delAllTransFile() {
  ElMessageBox.confirm('是否Confirm要删除全部？', 'Notice', {
    confirmButtonText: 'Confirm',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    // 清空所有轮询任务
    pollingTasks.value.clear()

    translatesData.value = []
    no_data.value = true

    delAllTranslate().then((data) => {
      if (data.code == 200) {
        translatesData.value = []
        no_data.value = true
        getStorageInfo()
      }
    })
  })
}

//下载全部文件
async function downAllTransFile() {
  try {
    const response = await fetch(API_URL + '/api/translate/download/all', {
      headers: {
        token: `${userStore.token}`
      }
    })

    if (!response.ok) {
      throw new Error('文件Download failed')
    }

    // 获取 ZIP 文件内容
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)

    // 创建 `<a>` 标签并触发下载
    const a = document.createElement('a')
    a.href = url
    a.download = `translations_${new Date().toISOString().slice(0, 10)}.zip` // 设置下载文件名
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url) // 释放 URL 对象
  } catch (error) {
    console.error('Download failed:', error)
    ElMessage.error('文件Download failed，请稍后重试')
  }
}

// 组件挂载时
onMounted(() => {
  if (userStore.token) {
    getTranslatesData(1)
    form.value = { ...form.value, ...translateStore.getCurrentServiceForm }
  }
})

// 组件卸载时清理所有定时器
onUnmounted(() => {
  // 清空所有轮询任务
  pollingTasks.value.clear()
})
</script>

<style scoped lang="scss">
.page-center {
  flex: 1;
  overflow-y: auto;
  padding-bottom: 90px;
}
// 滚动条样式
.page-center::-webkit-scrollbar {
  width: 0px;
}
.page-center::-webkit-scrollbar-thumb {
  border-radius: 10px;
  -webkit-box-shadow: inset 0 0 5px rgba(0, 0, 0, 0.2);
  opacity: 0.2;
  background: fade(#d8d8d8, 60%);
}
.page-center::-webkit-scrollbar-track {
  -webkit-box-shadow: inset 0 0 5px rgba(0, 0, 0, 0.2);
  border-radius: 0;
  background: fade(#d8d8d8, 30%);
}
.container {
  max-width: 1240px;
  margin: 0 auto;
  padding: 0 20px;
}
.upload-container {
  background: #ffffff;
  box-shadow: 0px 12px 20px 0px rgba(228, 238, 253, 0.5);
  border-radius: 12px;
  width: 100%;
  padding: 28px 28px;
  box-sizing: border-box;
  margin-top: 20px;
}
::v-deep {
  .dropzone {
    position: relative;
    .el-upload-dragger {
      border: 2px dashed #ccdaff;
      border-radius: 12px;
      padding-left: 0;
      padding-right: 0;
      &:hover {
        border-color: #3f66ff;
        background: #f8f9fe;
      }
    }
    .el-upload-list {
      position: absolute;
      width: 50%;
      left: 0;
      top: 50%;
      transform: translate(0, -50%);
      box-sizing: border-box;
      padding-left: 36px;
      padding-right: 36px;
      .el-upload-list__item:hover {
        background: #fff;
        .el-upload-list__item-file-name {
          color: var(--el-color-primary);
        }
      }
      .el-upload-list__item {
        display: inline-flex;
        align-items: center;
        margin-bottom: 20px;
        outline: none;
      }
      .el-upload-list__item-info {
        max-width: 90%;
        width: auto;
        .el-icon {
          display: none;
        }
      }
      .el-upload-list__item-status-label {
        position: relative;
        right: 0;
      }
      .el-icon--close {
        position: relative;
        top: 0;
        right: 0;
        transform: none;
      }
    }
    .left_box {
      width: 50%;
      float: left;
      height: 224px;
      border-right: 2px dashed #bcd4ff;
      box-sizing: border-box;
      display: flex;
      align-items: center;
      justify-content: center;
      img {
        margin: 0 15px;
      }
    }
    .right_box {
      width: 50%;
      float: right;
      height: 224px;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      box-sizing: border-box;
      padding: 0 20px;
      .title {
        font-family: PingFang SC;
        font-weight: bold;
        font-size: 18px;
        color: #111111;
        line-height: 24px;
      }
      .tips {
        font-family: PingFang SC;
        font-weight: 400;
        font-size: 14px;
        color: #666666;
        line-height: 18px;
      }
      .upload_btn {
        margin-top: 24px;
        margin-bottom: 18px;
        width: 180px;
        height: 40px;
        background: #f7faff;
        border-radius: 4px;
        border: 1px dashed #055cf9;
        display: flex;
        align-items: center;
        justify-content: center;
        outline: none;
        cursor: pointer;
        img {
          height: 18px;
        }
        span {
          font-family: PingFang SC;
          font-weight: bold;
          font-size: 16px;
          color: #045cf9;
          margin-left: 12px;
        }
      }
    }
  }

  .fixed_bottom {
    position: fixed;
    bottom: 0;
    width: 100%;
    background: #fff;
    height: 68px;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 99;
  }

  .list_box {
    width: 100%;
    margin-top: 20px;
    background: #fff;
    box-shadow: 0px 12px 20px 0px rgba(228, 238, 253, 0.5);
    border-radius: 12px;
    padding: 0 28px;
    box-sizing: border-box;
    padding-bottom: 30px;
    .title_box {
      display: flex;
      align-items: center;
      justify-content: space-between;
      height: 40px;
      padding-top: 14px;
      .t {
        font-weight: bold;
        font-size: 16px;
        color: #000000;
        .t_left {
          display: flex;
          align-items: center;
          .tips {
            margin-left: 30px;
            font-size: 14px;
            color: #666666;
            font-weight: 400;
            display: flex;
            align-items: center;
            span,
            i {
              color: #045cf9;
            }
          }
        }
      }
      .t_right {
        display: flex;
        align-items: center;
        flex: 1;
        justify-content: flex-end;
        .storage {
          font-size: 14px;
          color: #333333;
          margin-right: 9px;
        }
        .all_down {
          border-color: #055cf9;
          span {
            color: #055cf9;
          }
        }
      }
    }
    /*任务列表*/
    .table_box {
      width: 100;
      .table_row {
        display: flex;
        min-height: 40px;
        border-bottom: 1px solid #e5e5e5;
        align-items: center;
        font-size: 14px;
        color: #333;
        padding: 5px 0;
        .table_li {
          box-sizing: border-box;
          padding: 0 6px;
          display: flex;
          align-items: center;
          img {
            margin-right: 12px;
          }
          .file_name {
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            text-overflow: ellipsis;
          }
          .p_show {
            display: none;
          }
        }
        .table_li:first-child {
          width: 420px;
        }
        .table_li:nth-child(2) {
          width: 370px;
        }
        .table_li:nth-child(3) {
          width: 90px;
          white-space: nowrap;
        }
        .table_li:nth-child(4) {
          width: 180px;
        }
        .table_li:nth-child(5) {
          width: 50px;
        }
      }
      .table_top {
        color: #999999;
      }
      .status {
        img {
          margin-left: 5px;
          margin-right: 7px;
        }
        span {
          white-space: nowrap;
          width: 68px;
        }
        .failed {
          color: #ff4940;
        }
        .done {
          color: #20b759;
        }
        .process {
          color: #ff9c00;
        }
      }
      .icon_down::after {
        content: none;
      }
    }
  }
  .translate-btn {
    line-height: 36px;
    width: 180px;
    color: white;
    border: none;
    background: #055cf9;
    border-radius: 4px;
    cursor: pointer;
    &:hover {
      opacity: 0.7;
    }
  }
}
</style>
<style type="text/css" lang="scss">
.translated-process {
  max-width: 270px;
  width: 80%;
}
/*手机端处理*/
@media screen and (max-width: 767px) {
  .upload-container {
    padding: 20px !important;
  }
  .list_box {
    padding: 0 20px !important;
    .title_box {
      flex-direction: column !important;
      height: auto !important;
      align-items: flex-start !important;
      .t {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        width: 100%;
      }
      .t_right {
        width: 100%;
        .storage {
          white-space: nowrap;
        }
      }
    }
    .table_box {
      padding-top: 10px;
      .table_row:last-child {
        border: none;
      }
    }
    .phone_row {
      display: inline-block !important;
      width: 100%;
      overflow: hidden;
      padding-top: 10px !important;
      .table_li {
        margin-bottom: 10px;
        .p_show {
          display: block;
        }
      }
      .table_li:first-child {
        width: 100% !important;
      }
      .status {
        width: 100% !important;
      }
      .table_li:nth-child(3) {
        display: inline-block !important;
        width: auto !important;
        font-size: 12px !important;
        color: #969fa9;
        &.pc_show {
          display: none !important;
        }
      }
      .table_li:nth-child(4) {
        display: inline-block !important;
        width: auto !important;
        font-size: 12px !important;
        color: #969fa9;
        &.pc_show {
          display: none !important;
        }
      }
      .table_li:nth-child(5) {
        display: inline-block !important;
        width: auto !important;
        font-size: 12px !important;
        color: #969fa9;
        &.pc_show {
          display: none !important;
        }
      }
    }
  }
  .dropzone {
    .el-upload-dragger {
      padding: 0 !important;
    }
    .right_box {
      width: 100% !important;
      height: auto !important;
      .tips {
        margin-top: 10px;
        margin-bottom: 20px;
      }
    }
    .el-upload-list {
      position: relative !important;
      width: 100% !important;
      left: unset !important;
      transform: none !important;
      padding: 0 !important;
      margin: 0;
      .el-upload-list__item {
        margin-top: 18px !important;
        margin-bottom: 0 !important;
      }
    }
  }
  .t_left {
    display: inline-block !important;
    .tips {
      margin-top: 10px;
      margin-left: 0 !important;
      font-size: 12px !important;
    }
  }
  .no_data {
    padding-bottom: 20px !important;
  }

  /*调整间距、字体大小*/
  .upload_btn span {
    font-size: 14px !important;
  }
  .dropzone .right_box .title {
    font-size: 16px !important;
  }
  .translate-btn {
    width: 90% !important;
  }
}
.icon_handle {
  margin-right: 10px;
  cursor: pointer; /* 鼠标悬停时显示手型 */
}
</style>
