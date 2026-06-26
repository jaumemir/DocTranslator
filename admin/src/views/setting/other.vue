<script lang="ts" setup>
import { ref, onMounted } from "vue"
import { type FormInstance, ElMessage } from "element-plus"
import { getOtherSettingData, setOtherSettingData } from "@/api/setting"

defineOptions({
  // Name the current component
  name: "Other Configuration"
})
const loading = ref(false)
const setting = ref({
  prompt: "",
  threads: "",
  email_limit: ""
})

const settingForm = ref<FormInstance | null>(null)

const rules = {
  prompt: [{ required: true, message: "Please enter the default prompt", trigger: "blur" }],
  threads: [{ required: true, message: "Please enter the default thread count", trigger: "blur" }]
}

onMounted(async () => {
  loading.value = true
  await getOtherSettingData().then((data) => {
    setting.value = data.data
  })
  loading.value = false
})

function onSubmit(settingForm: FormInstance | null) {
  console.log(setting.value)
  console.log({
    prompt: setting.value.prompt,
    threads: setting.value.threads,
    email_limit: setting.value.email_limit
  })
  settingForm?.validate((valid, messages) => {
    console.log(valid)
    console.log(messages)
    console.log(setting.value)
    if (valid) {
      setOtherSettingData({
        prompt: setting.value.prompt,
        threads: setting.value.threads,
        email_limit: setting.value.email_limit
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
</script>

<template>
  <div class="app-container">
    <el-card shadow="never" v-loading="loading" :element-loading-text="'Loading...'">
      <el-form class="settingForm" ref="settingForm" :model="setting" label-position="top" :rules="rules">
        <el-form-item label="Default Prompt" required prop="prompt">
          <el-input type="textarea" resize="none" :rows="5" v-model="setting.prompt" />
        </el-form-item>
        <el-form-item label="Default Thread Count" required prop="threads">
          <el-input v-model="setting.threads" />
        </el-form-item>
        <el-form-item label="Restrict Registration Email Suffix" prop="email_limit">
          <el-input v-model="setting.email_limit" placeholder="Separate multiple with commas, exact domain match" />
        </el-form-item>
        <el-form-item class="setting-btns">
          <el-button style="width: 88px" type="primary" @click="onSubmit(settingForm)">Save</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<style lang="scss" scoped>
.settingForm {
  :deep(.el-form-item__content) {
    max-width: 480px;
    justify-content: left;
  }
}
</style>
