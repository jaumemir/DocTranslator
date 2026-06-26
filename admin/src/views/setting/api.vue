<template>
  <div class="app-container">
    <el-card shadow="never" v-loading="loading" :element-loading-text="'Loading...'">
      <span class="notice-tip">Note: Member users use the system default API</span>
      <el-form class="settingForm" ref="settingForm" :model="setting" label-position="top" :rules="rules">
        <el-form-item label="Base Url" prop="api_url" required>
          <el-input v-model="setting.api_url" placeholder="https://api.ezworkapi.top/v1" />
        </el-form-item>
        <el-form-item label="API Key" prop="api_key" required>
          <el-input v-model="setting.api_key" placeholder="sk-******" />
        </el-form-item>
        <el-form-item label="Model List" prop="models" required>
          <el-input
            type="textarea"
            resize="none"
            :rows="3"
            v-model="setting.models"
            @blur="changeModel"
            placeholder="Enter at least 1 model, separate multiple models with commas"
          />
        </el-form-item>
        <el-form-item label="Default Model">
          <el-select v-model="setting.default_model" placeholder="If no default model is selected, the first one in the list will be used" clearable>
            <el-option v-for="model in models" :key="model" :label="model" :value="model" />
          </el-select>
        </el-form-item>
        <el-form-item label="Default Backup Model">
          <el-select v-model="setting.default_backup" placeholder="If no backup model is selected, the first one in the list will be used" clearable>
            <el-option
              v-for="model in models"
              :key="model"
              :disabled="setting.default_model == model ? true : false"
              :label="model"
              :value="model"
            />
          </el-select>
        </el-form-item>
        <el-form-item class="setting-btns">
          <el-button style="width: 88px" type="primary" @click="onSubmit(settingForm)">Save</el-button>
          <el-button type="primary" plain @click="openTestDialog">Test Model</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Model Test Dialog -->
    <el-dialog
      title="Model Test"
      v-model="testDialogVisible"
      width="600px"
      :close-on-click-modal="false"
      align-center
      top="1vh"
    >
      <el-form :model="testForm" label-position="top">
        <el-form-item label="Select Model">
          <el-select v-model="testForm.selectedModel" placeholder="Please select a test model" style="width: 100%">
            <el-option v-for="model in models" :key="model" :label="model" :value="model" />
          </el-select>
        </el-form-item>
        <el-form-item label="Test Message">
          <el-input v-model="testForm.message" type="textarea" :rows="3" placeholder="Enter test message" />
        </el-form-item>
        <el-form-item>
          <template #label>
            <div class="result-label">
              <span>Test Result</span>
              <div class="metrics-container" v-if="metrics">
                <span class="metric-item">
                  <span class="metric-label">Response:</span>
                  <span class="metric-value">{{ metrics.responseTime }}ms</span>
                </span>
                <span class="metric-item">
                  <span class="metric-label">First Token:</span>
                  <span class="metric-value">{{ metrics.firstTokenTime }}ms</span>
                </span>
                <span class="metric-item">
                  <span class="metric-label">Duration:</span>
                  <span class="metric-value">{{ metrics.duration }}ms</span>
                </span>
                <span class="metric-item">
                  <span class="metric-label">Speed:</span>
                  <span class="metric-value">{{ metrics.tokensPerSecond }} tokens/s</span>
                </span>
              </div>
            </div>
          </template>
          <div class="test-result-container test-result-content1">{{ testResult }}</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="testDialogVisible = false">Close</el-button>
          <el-button type="primary" @click="testModel" :loading="testLoading">Test</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { ElMessage } from "element-plus"
import { getApiSettingData, setApiSettingData } from "@/api/setting"

defineOptions({
  name: "API Configuration"
})

const loading = ref(false)
const setting = ref({
  api_url: "",
  api_key: "",
  models: "",
  default_model: "",
  default_backup: ""
})

const models = ref([])
const settingForm = ref(null)

const rules = {
  api_url: [{ required: true, message: "Please enter the API endpoint URL", trigger: "blur" }],
  api_key: [{ required: true, message: "Please enter the API Key", trigger: "blur" }],
  models: [{ required: true, message: "Please enter the model list configuration", trigger: "blur" }]
}

// 测试相关
const testDialogVisible = ref(false)
const testLoading = ref(false)
const testResult = ref("")
const testForm = ref({
  selectedModel: "",
  message: "Hello, 你好"
})
const metrics = ref(null)

onMounted(async () => {
  loading.value = true
  await getApiSettingData().then((data) => {
    if (data.data) {
      setting.value = data.data
      const arr = data.data.models.split(",")
      models.value = arr.filter((item) => item != "")
    }
  })
  loading.value = false
})

function changeModel() {
  if (!setting.value.models) return
  const arr = setting.value.models.split(",")
  models.value = arr.filter((item) => item != "")
  if (arr.indexOf(setting.value.default_model) == -1) {
    setting.value.default_model = ""
  }
  if (arr.indexOf(setting.value.default_backup) == -1) {
    setting.value.default_backup = ""
  }
}

function onSubmit(form) {
  console.log(setting.value)

  form.validate((valid, messages) => {
    console.log(valid)
    console.log(messages)
    if (valid) {
      setApiSettingData({
        api_url: setting.value.api_url,
        api_key: setting.value.api_key,
        models: setting.value.models,
        default_model: setting.value.default_model,
        default_backup: setting.value.default_backup
      })
        .then((data) => {
          if (data.code == 200) {
            ElMessage.success("Saved successfully")
          } else {
            ElMessage.error(data.message)
          }
        })
        .catch((e) => {
          ElMessage.error(e)
        })
    } else {
      for (const field in messages) {
        messages[field].forEach((message) => {
          ElMessage({
            message: message["message"],
            type: "error"
          })
        })
        break
      }
    }
  })
}

function openTestDialog() {
  testDialogVisible.value = true
  testResult.value = ""
  metrics.value = null
  // Select first model by default
  if (models.value.length > 0 && !testForm.value.selectedModel) {
    testForm.value.selectedModel = models.value[0]
  }
}

function testModel() {
  if (!testForm.value.selectedModel) {
    ElMessage.warning("Please select a test model")
    return
  }
  if (!testForm.value.message.trim()) {
    ElMessage.warning("Please enter a test message")
    return
  }

  testLoading.value = true
  testResult.value = ""
  metrics.value = null

  const model = testForm.value.selectedModel
  const message = testForm.value.message

  // Construct OpenAI format request
  const requestBody = {
    model: model,
    messages: [{ role: "user", content: message }],
    stream: true
  }

  // Record timestamps
  const timestamps = {
    start: performance.now(),
    response: null,      // API response time (HTTP headers received)
    firstToken: null,    // First token time
    end: null           // Completion time
  }

  // Token statistics
  let inputTokens = 0
  let outputTokens = 0
  let reasoningTokens = 0 // Reasoning tokens for thinking models

  // Reasoning content markers
  let hasReasoning = false
  let reasoningContent = ""
  let finalContent = ""

  const startTime = performance.now()

  fetch(setting.value.api_url + "/chat/completions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${setting.value.api_key}`
    },
    body: JSON.stringify(requestBody)
  })
    .then((response) => {
      // Record API response time (when fetch Promise resolves)
      timestamps.response = performance.now()

      if (!response.ok) {
        // If response is unsuccessful, read response body for error message
        return response.text().then((errorText) => {
          testLoading.value = false
          let errorMessage = `HTTP ${response.status}`
          try {
            // Try to parse JSON error response
            const errorJson = JSON.parse(errorText)
            if (errorJson.error && errorJson.error.message) {
              errorMessage = errorJson.error.message
            } else {
              errorMessage = errorText
            }
          } catch (e) {
            // If not JSON format, use text directly
            errorMessage = errorText
          }
          testResult.value = `Test failed: ${errorMessage}`
          ElMessage.error(`Test failed: ${errorMessage}`)
          throw new Error(errorMessage)
        })
      }

      // If response is successful, start processing stream data
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ""

      function read() {
        reader
          .read()
          .then(({ done, value }) => {
            if (done) {
              timestamps.end = performance.now()
              testLoading.value = false
              calculateMetrics()
              ElMessage.success("Test completed")
              return
            }

            buffer += decoder.decode(value, { stream: true })
            const lines = buffer.split("\n")
            buffer = lines.pop() || ""

            for (const line of lines) {
              if (line.startsWith("data: ")) {
                const data = line.slice(6)
                if (data === "[DONE]") {
                  timestamps.end = performance.now()
                  testLoading.value = false
                  calculateMetrics()
                  ElMessage.success("Test completed")
                  return
                }

                try {
                  const parsed = JSON.parse(data)

                  // Handle token statistics
                  if (parsed.usage) {
                    if (parsed.usage.prompt_tokens) inputTokens = parsed.usage.prompt_tokens
                    if (parsed.usage.completion_tokens) outputTokens = parsed.usage.completion_tokens
                    // Support reasoning tokens for thinking models
                    if (parsed.usage.reasoning_tokens) reasoningTokens = parsed.usage.reasoning_tokens
                  }

                  const delta = parsed.choices?.[0]?.delta
                  if (delta) {
                    // Record first token time (including reasoning content)
                    if (!timestamps.firstToken) {
                      timestamps.firstToken = performance.now()
                    }

                    // Handle reasoning content (reasoning_content)
                    if (delta.reasoning_content) {
                      hasReasoning = true
                      reasoningContent += delta.reasoning_content
                      // If there is reasoning content, show thinking part first
                      testResult.value = `[Reasoning Process]\n${reasoningContent}`
                    }

                    // Handle final answer content (content)
                    if (delta.content) {
                      finalContent += delta.content
                      // If there is reasoning content, display separately
                      if (hasReasoning) {
                        testResult.value = `[Reasoning Process]\n${reasoningContent}\n\n[Final Answer]\n${finalContent}`
                      } else {
                        testResult.value = finalContent
                      }
                    }
                  }
                } catch (e) {
                  console.error("Data parsing error:", e)
                }
              }
            }

            read()
          })
          .catch((error) => {
            testLoading.value = false
            // Error occurred while reading stream
            testResult.value = `Stream reading failed: ${error.message}`
            ElMessage.error(`Stream reading failed: ${error.message}`)
          })
      }

      read()
    })
    .catch((error) => {
      testLoading.value = false
      testResult.value = `Test failed: ${error.message}`
      console.error("Request error:", error)
      ElMessage.error(`Test failed: ${error.message}`)
    })

  function calculateMetrics() {
    // Response time: from request sent to HTTP response headers received
    const responseTime = timestamps.response ? Math.round(timestamps.response - timestamps.start) : 0

    // First token time: from request sent to first content token received
    const firstTokenTime = timestamps.firstToken ? Math.round(timestamps.firstToken - timestamps.start) : 0

    // Total duration: from request sent to completion
    const duration = timestamps.end ? Math.round(timestamps.end - timestamps.start) : 0

    // Total tokens (including input, output and reasoning)
    const totalTokens = inputTokens + outputTokens + reasoningTokens

    // tokens/s (output speed per second)
    const tokensPerSecond = duration > 0 ? Math.round((totalTokens / duration) * 1000) : 0

    metrics.value = {
      responseTime,
      firstTokenTime,
      duration,
      tokensPerSecond
    }
  }
}
</script>

<style lang="scss" scoped>
.settingForm {
  :deep(.el-form-item__content) {
    max-width: 480px;
    line-height: 1.2;
    justify-content: left;
  }
}
:deep(.el-form-item) {
  margin-bottom: 8px;
}

:deep(.el-form-item__content) {
  line-height: 1.2;
  justify-content: left;
}

.notice-tip {
  padding: 6px 12px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e6f3ff 100%);
  border-left: 3px solid #409eff;
  border-radius: 4px;
  font-size: 13px;
  color: #606266;
  font-weight: 500;
  margin-bottom: 8px;
  animation: fadeIn 0.3s ease-in-out;
  display: inline-block;
}

.test-result-container {
  width: 100%;
  height: 100px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 8px;
  background-color: #f5f7fa;
  overflow: auto;
  font-family: monospace;
  font-size: 13px;
  line-height: 1.3;
  // color: #606266;
}

.result-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.metrics-container {
  display: flex;
  gap: 12px;
}

.metric-item {
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.metric-label {
  color: #909399;
  font-weight: 400;
}

.metric-value {
  color: #67c23a;
  font-weight: 600;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
