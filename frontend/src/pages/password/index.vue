<template>
  <div class="auth-page">
    <div class="auth-container">
      <div class="auth-header">
        <h1 class="auth-title">Password Management</h1>
        <p class="auth-subtitle">Select an operation</p>
      </div>

      <!-- Tab switching -->
      <div class="tab-container">
        <div class="tab-tabs">
          <div
            v-for="tab in tabs"
            :key="tab.value"
            class="tab-item"
            :class="{ active: activeTab === tab.value }"
            @click="activeTab = tab.value">
            {{ tab.label }}
          </div>
        </div>
      </div>

      <!-- Forgot password form -->
      <el-form
        v-show="activeTab === 'forget'"
        ref="forgetForm"
        :model="forgetUser"
        :show-message="false"
        :rules="forgetRules"
        @keyup.enter="doForget(forgetForm)"
        class="form-content">
        <el-form-item label="" prop="email">
          <el-input v-model="forgetUser.email" placeholder="Enter email" prefix-icon="el-icon-message" />
        </el-form-item>
        <el-form-item label="" prop="code">
          <el-input v-model="forgetUser.code" placeholder="Email verification code" prefix-icon="el-icon-key">
            <template #suffix>
              <el-button type="text" class="code-btn" @click="sendCode" :disabled="codeDisabled">
                {{ codeText }}
              </el-button>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="" prop="password">
          <el-input
            v-model="forgetUser.password"
            type="password"
            show-password
            placeholder="Set new password"
            prefix-icon="el-icon-lock" />
        </el-form-item>
        <el-form-item label="" prop="password_confirmation">
          <el-input
            v-model="forgetUser.password_confirmation"
            type="password"
            show-password
            placeholder="Confirm new password"
            prefix-icon="el-icon-lock" />
        </el-form-item>
        <el-form-item label="" class="center">
          <el-button type="primary" size="large" class="auth-btn" @click="doForget(forgetForm)">Submit Reset</el-button>
        </el-form-item>
      </el-form>

      <!-- Change password form -->
      <el-form
        v-show="activeTab === 'change'"
        ref="changeForm"
        :model="changeUser"
        :show-message="false"
        :rules="changeRules"
        @keyup.enter="doChangePassword(changeForm)"
        class="form-content">
        <el-form-item label="" prop="oldpwd">
          <el-input
            v-model="changeUser.oldpwd"
            type="password"
            show-password
            placeholder="Current password"
            prefix-icon="el-icon-lock" />
        </el-form-item>
        <el-form-item label="" prop="newpwd">
          <el-input
            v-model="changeUser.newpwd"
            type="password"
            show-password
            placeholder="Set new password"
            prefix-icon="el-icon-lock" />
        </el-form-item>
        <el-form-item label="" prop="newpwd_confirmation">
          <el-input
            v-model="changeUser.newpwd_confirmation"
            type="password"
            show-password
            placeholder="Confirm new password"
            prefix-icon="el-icon-lock" />
        </el-form-item>
        <el-form-item label="" class="center">
          <el-button type="primary" size="large" class="auth-btn" @click="doChangePassword(changeForm)">
            Confirm Change
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 返回操作区 -->
      <div class="action-links">
        <el-link type="primary" class="action-link" @click="goToLogin">
          <el-icon><ArrowLeft /></el-icon>
          返回登录
        </el-link>
        <el-link type="primary" class="action-link" @click="$router.push('/')">
          <el-icon><HomeFilled /></el-icon>
          首页
        </el-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, HomeFilled } from '@element-plus/icons-vue'
import { forgetSendEmail, forget } from '@/api/auth'
import { changePassword } from '@/api/account'

const router = useRouter()

// Tab 切换
const activeTab = ref('forget')
const tabs = [
  { label: '忘记密码', value: 'forget' },
  { label: '修改密码', value: 'change' },
]

// 忘记密码数据
const forgetUser = reactive({
  email: '',
  code: '',
  password: '',
  password_confirmation: '',
})

// 修改密码数据
const changeUser = reactive({
  oldpwd: '',
  newpwd: '',
  newpwd_confirmation: '',
})

// 忘记密码规则
const forgetRules = reactive({
  email: [{ required: true, message: '请填写邮箱地址', trigger: 'blur' }],
  code: [{ required: true, message: '请填写邮箱验证码', trigger: 'blur' }],
  password: [{ required: true, message: '请填写新密码', trigger: 'blur' }],
  password_confirmation: [{ required: true, message: '请填写确认密码', trigger: 'blur' }],
})

// 修改密码规则
const changeRules = reactive({
  oldpwd: [{ required: true, message: '请填写原密码', trigger: 'blur' }],
  newpwd: [{ required: true, message: '请填写新密码', trigger: 'blur' }],
  newpwd_confirmation: [{ required: true, message: '请填写确认密码', trigger: 'blur' }],
})

// 验证码相关
const codeText = ref('发送')
const codeDisabled = ref(false)
const forgetForm = ref()
const changeForm = ref()

// 发送验证码
const sendCode = async () => {
  if (codeDisabled.value) return
  if (!forgetUser.email.trim()) {
    ElMessage.error('请填写邮箱地址')
    return
  }

  try {
    await forgetSendEmail(forgetUser.email)
    ElMessage.success('验证码已发送')
    codeDisabled.value = true
    let count = 60
    codeText.value = `${count}s`
    const timer = setInterval(() => {
      if (count <= 0) {
        clearInterval(timer)
        codeDisabled.value = false
        codeText.value = '发送'
        return
      }
      count--
      codeText.value = `${count}s`
    }, 1000)
  } catch (error) {
    ElMessage.error(error.message)
  }
}

// 忘记密码提交
const doForget = async (form) => {
  form.validate((valid, fields) => {
    if (valid) {
      if (forgetUser.password !== forgetUser.password_confirmation) {
        ElMessage.error('两次密码输入不一致')
        return
      }
      forget(forgetUser)
        .then((data) => {
          if (data.code === 200) {
            ElMessage.success('密码重置成功')
            router.push({ name: 'login' })
          } else {
            ElMessage.error(data.message)
          }
        })
        .catch((error) => {
          ElMessage.error(error.message)
        })
    } else {
      ElMessage.error(fields[Object.keys(fields)[0]][0].message)
    }
  })
}

// 修改密码提交
const doChangePassword = async (form) => {
  form.validate((valid, fields) => {
    if (valid) {
      if (changeUser.newpwd !== changeUser.newpwd_confirmation) {
        ElMessage.error('两次密码输入不一致')
        return
      }
      changePassword(changeUser)
        .then((data) => {
          if (data.code === 200) {
            ElMessage.success('密码修改成功')
            router.push({ name: 'login' })
          } else {
            ElMessage.error(data.message)
          }
        })
        .catch((error) => {
          ElMessage.error(error.message)
        })
    } else {
      ElMessage.error(fields[Object.keys(fields)[0]][0].message)
    }
  })
}

// 返回登录
const goToLogin = () => {
  router.push({ name: 'login' })
}
</script>

<style scoped lang="scss">
.auth-page {
  display: flex;
  justify-content: center;
  align-items: center;
  // background: #f0f7ff;
}

.auth-container {
  width: 100%;
  max-width: 420px;
  border-radius: 8px;
  padding: 20px;
}

.auth-header {
  text-align: center;
  margin-bottom: 20px;
}

.auth-title {
  font-size: 22px;
  font-weight: 600;
  color: #1976d2;
  margin-bottom: 6px;
}

.auth-subtitle {
  font-size: 13px;
  color: #6c757d;
}

// Tab 容器
.tab-container {
  margin-bottom: 20px;
}

.tab-tabs {
  display: flex;
  background: #f5f5f5;
  border-radius: 6px;
  padding: 3px;
}

.tab-item {
  flex: 1;
  text-align: center;
  padding: 10px 0;
  font-size: 14px;
  color: #6c757d;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s ease;
  font-weight: 500;

  &:hover {
    background: #e9ecef;
    color: #495057;
  }

  &.active {
    background: #2196f3;
    color: white;
  }
}

// 表单内容
.form-content {
  margin-bottom: 10px;
}

// 按钮样式
.auth-btn {
  width: 100%;
  background: #2196f3;
  border: none;
  font-weight: 500;
  transition: background-color 0.2s ease;

  &:hover {
    background: #1976d2;
  }
}

// 验证码按钮
.code-btn {
  font-size: 13px;
  font-weight: 600;
  color: #2196f3;
  padding: 0 8px;

  &:disabled {
    color: #909399;
  }
}

// 操作链接
.action-links {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.action-link {
  font-size: 13px;
  font-weight: 500;
  color: #6c757d;

  &:hover {
    color: #2196f3;
  }

  .el-icon {
    margin-right: 4px;
    font-size: 14px;
  }
}

// 移动端适配
@media (max-width: 768px) {
  .auth-page {
    padding: 10px;
  }

  .auth-container {
    max-width: 100%;
    padding: 20px;
    margin: 0;
    border-radius: 6px;
  }

  .auth-title {
    font-size: 20px;
  }

  .auth-subtitle {
    font-size: 12px;
  }

  .tab-tabs {
    padding: 2px;
  }

  .tab-item {
    padding: 8px 0;
    font-size: 13px;
  }

  .form-content {
    margin-bottom: 16px;
  }

  .action-links {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .action-link {
      width: 100%;
      justify-content: center;
    }
  }
}

// 输入框样式优化
:deep(.el-input__wrapper) {
  background-color: #fafafa;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  transition: all 0.2s ease;

  &:hover {
    border-color: #90caf9;
    background-color: #ffffff;
  }

  &.is-focus {
    border-color: #2196f3;
    background-color: #ffffff;
  }
}

:deep(.el-input__inner) {
  color: #495057;
  font-weight: 500;
}

:deep(.el-input__prefix) {
  color: #6c757d;
}
</style>
