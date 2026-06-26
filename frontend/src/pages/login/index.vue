<template>
  <div class="auth-page">
    <!-- Decorative background shapes (very subtle, adds depth) -->
    <div class="bg-shape shape-1"></div>
    <div class="bg-shape shape-2"></div>

    <div class="auth-box">
      <!-- Left side: Brand and open source info -->
      <div class="auth-sidebar">
        <div class="sidebar-top">
          <!-- Logo and name in one line -->
          <div class="brand-header">
            <img src="@/assets/logo.png" alt="Logo" class="brand-logo" />
            <span class="brand-name">DocTranslator</span>
          </div>

          <div class="brand-slogan">
            <p class="main-slogan">Open Source AI Document Translation Platform</p>
            <p class="sub-slogan">All-in-One Document Translation Solution</p>
          </div>

          <div class="feature-list">
            <div class="feature-item">
              <el-icon><Connection /></el-icon>
              <span>Open Source, Community Supported</span>
            </div>
            <div class="feature-item">
              <el-icon><Lock /></el-icon>
              <span>Local/Cloud Deployment Support</span>
            </div>
            <div class="feature-item">
              <el-icon><Document /></el-icon>
              <span>Customizable Feature Development</span>
            </div>
          </div>
        </div>

        <div class="sidebar-footer">
          <div class="copyright-info">
            <a href="https://www.doctranslator.cn" target="_blank" class="github-link">
              <p class="copyright">© 2025 DocTranslator 1.5.0 All Rights Reserved</p>
              <!-- Do not remove without permission. -->
            </a>
          </div>
        </div>
      </div>

      <!-- Right side: Login/Register form -->
      <div class="auth-form-container">
        <!-- Mobile-specific header -->
        <div class="mobile-header">
          <div class="mobile-brand">
            <img src="@/assets/logo.png" alt="Logo" class="mobile-logo" />
            <div class="mobile-text">
              <h1 class="mobile-title">DocTranslator Pro</h1>
              <p class="mobile-subtitle">AI Document Translation Platform</p>
            </div>
          </div>
        </div>

        <div class="form-wrapper">
          <div class="auth-header">
            <h2 class="auth-title">{{ activeTab === 'login' ? 'Welcome Back' : 'Create Account' }}</h2>
            <p class="auth-subtitle">
              {{ activeTab === 'login' ? 'Sign in to your account' : 'Register a new account to get started' }}
            </p>
          </div>

          <el-tabs v-model="activeTab" stretch class="custom-tabs">
            <!-- Login Tab -->
            <el-tab-pane label="Login" name="login">
              <el-form
                ref="loginFormRef"
                :model="loginForm"
                :rules="loginRules"
                size="large"
                class="auth-form"
                @keyup.enter="doLogin"
              >
                <!-- prop="email" -->
                <el-form-item>
                  <el-input
                    v-model="loginForm.email"
                    placeholder="Enter email address"
                    prefix-icon="Message"
                  />
                </el-form-item>
                <!-- prop="password" -->
                <el-form-item>
                  <el-input
                    v-model="loginForm.password"
                    type="password"
                    show-password
                    placeholder="Enter password"
                    prefix-icon="Lock"
                  />
                </el-form-item>

                <div class="form-actions">
                  <el-link :underline="false" class="forget-link" @click="goToForgot"
                    >Forgot password?</el-link
                  >
                </div>

                <el-button
                  type="primary"
                  class="submit-btn"
                  :loading="loginLoading"
                  @click="doLogin"
                  >Login</el-button
                >
              </el-form>
            </el-tab-pane>

            <!-- Register Tab -->
            <el-tab-pane label="Register" name="register">
              <el-form
                ref="registerFormRef"
                :model="registerForm"
                :rules="registerRules"
                size="large"
                class="auth-form"
                @keyup.enter="doRegister"
              >
                <el-form-item prop="name">
                  <el-input
                    v-model="registerForm.name"
                    placeholder="Enter nickname"
                    prefix-icon="User"
                  />
                </el-form-item>
                <el-form-item prop="email">
                  <el-input
                    v-model="registerForm.email"
                    placeholder="Enter email address"
                    prefix-icon="Message"
                  />
                </el-form-item>
                <el-form-item prop="code">
                  <el-input
                    v-model="registerForm.code"
                    placeholder="Enter verification code"
                    prefix-icon="Key"
                  >
                    <template #suffix>
                      <el-button
                        type="primary"
                        link
                        class="code-btn"
                        :disabled="codeDisabled"
                        :loading="codeSending"
                        @click="sendCode"
                      >
                        {{ codeText }}
                      </el-button>
                    </template>
                  </el-input>
                </el-form-item>
                <el-form-item prop="password">
                  <el-input
                    v-model="registerForm.password"
                    type="password"
                    show-password
                    placeholder="Set password"
                    prefix-icon="Lock"
                  />
                </el-form-item>
                <el-form-item prop="password2">
                  <el-input
                    v-model="registerForm.password2"
                    type="password"
                    show-password
                    placeholder="Confirm password"
                    prefix-icon="Lock"
                  />
                </el-form-item>

                <el-button
                  type="primary"
                  class="submit-btn"
                  :loading="registerLoading"
                  @click="doRegister"
                >
                  Register
                </el-button>
              </el-form>
            </el-tab-pane>
          </el-tabs>

          <!-- Footer notes -->
          <div class="form-footer">
            <p class="footer-text">
              By continuing, you agree to our
              <el-link type="primary" class="footer-link">Terms of Service</el-link>
              and
              <el-link type="primary" class="footer-link">Privacy Policy</el-link>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Lock, Connection, Document } from '@element-plus/icons-vue'
import { login, register, registerSendEmail } from '@/api/auth'
import { useUserStore } from '@/store/user'
const userStore = useUserStore()
const router = useRouter()
const activeTab = ref('login')
const loginFormRef = ref(null)
const registerFormRef = ref(null)
const loginLoading = ref(false)
const registerLoading = ref(false)
const codeSending = ref(false)

// 登录数据
const loginForm = reactive({
  email: '',
  password: ''
})
const loginRules = reactive({
  email: [
    { required: true, message: 'Please enter email address', trigger: 'blur' },
    { type: 'email', message: 'Please enter a valid email format', trigger: 'blur' }
  ],
  password: [
    { required: true, message: 'Please enter password', trigger: 'blur' },
    { min: 6, message: 'Password must be at least 6 characters', trigger: 'blur' }
  ]
})

// 注册数据
const registerForm = reactive({
  email: '',
  code: '',
  password: '',
  password2: '',
  name: ''
})
const registerRules = reactive({
  email: [
    { required: true, message: 'Please enter email address', trigger: 'blur' },
    { type: 'email', message: 'Please enter a valid email format', trigger: 'blur' }
  ],
  code: [{ required: true, message: 'Please enter verification code', trigger: 'blur' }],
  password: [
    { required: true, message: 'Please set a password', trigger: 'blur' },
    { min: 6, message: 'Password must be at least 6 characters', trigger: 'blur' }
  ],
  password2: [
    { required: true, message: 'Please confirm password', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== registerForm.password) callback(new Error('Passwords do not match'))
        else callback()
      },
      trigger: 'blur'
    }
  ]
})

// Verification code logic
const codeText = ref('Get Code')
const codeDisabled = ref(false)

const sendCode = async () => {
  if (codeDisabled.value || codeSending.value) return
  if (!registerForm.email) {
    ElMessage.warning('Please enter email address first')
    return
  }
  try {
    codeSending.value = true
    await registerSendEmail(registerForm.email)
    ElMessage.success('Verification code has been sent to your email')
    codeDisabled.value = true

    let count = 60
    codeText.value = `Resend in ${count}s`
    const timer = setInterval(() => {
      count--
      if (count <= 0) {
        clearInterval(timer)
        codeDisabled.value = false
        codeText.value = 'Get Code'
      } else {
        codeText.value = `Resend in ${count}s`
      }
    }, 1000)
  } catch (error) {
    ElMessage.error(error.message || 'Failed to send, please try again later')
  } finally {
    codeSending.value = false
  }
}

// Login submission
const doLogin = () => {
  if (!loginFormRef.value) return
  loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loginLoading.value = true
      try {
        const res = await login(loginForm)
        if (res.code === 200) {
          userStore.updateToken(res.data.token)
          ElMessage.success('Login successful')
          router.push({ name: 'home' })
        } else {
          ElMessage.error(res.message || 'Login failed')
        }
      } catch (err) {
        ElMessage.error(err.response.data.message || 'Login failed, please try again later')
      } finally {
        loginLoading.value = false
      }
    } else {
      ElMessage.error('Please fill in the form correctly')
    }
  })
}

// Register submission
const doRegister = () => {
  if (!registerFormRef.value) return
  registerFormRef.value.validate(async (valid) => {
    if (valid) {
      registerLoading.value = true
      try {
        const res = await register(registerForm)
        if (res.code === 200) {
          ElMessage.success('Registration successful, please login')
          activeTab.value = 'login'
          // Fill registration email into login form
          loginForm.email = registerForm.email
          // Clear registration form
          Object.assign(registerForm, {
            email: '',
            name:'',
            code: '',
            password: '',
            password2: ''
          })
        } else {
          ElMessage.error(res.message || 'Registration failed')
        }
      } catch (err) {
        ElMessage.error(err.message || 'Registration failed, please try again later')
      } finally {
        registerLoading.value = false
      }
    } else {
      ElMessage.error('Please fill in the form correctly')
    }
  })
}

const goToForgot = () => {
  router.push({ name: 'password' })
}
</script>

<style scoped lang="scss">
/* 
  配色变量：
  主色调：#3b82f6 (品牌蓝)
  背景色：#f0f7ff (极淡蓝)
  侧边栏背景：#eff6ff (淡蓝)
  文字色：#1e293b (深灰蓝)
*/

.auth-page {
  width: 100vw;
  height: 100vh;
  overflow: hidden; /* 核心：禁止出现滚动条 */
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #f0f7ff 0%, #ffffff 100%); /* 极淡的蓝色背景 */
  position: relative;
}

/* 背景装饰，增加一点点现代感，但不抢眼 */
.bg-shape {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  z-index: 0;
  opacity: 0.6;
}
.shape-1 {
  width: 500px;
  height: 500px;
  background: #dbeafe; /* 淡蓝色 */
  top: -100px;
  left: -100px;
}
.shape-2 {
  width: 400px;
  height: 400px;
  background: #e0f2fe; /* 另一种淡蓝 */
  bottom: -100px;
  right: -100px;
}

/* 主容器 */
.auth-box {
  position: relative;
  z-index: 1;
  width: 1000px;
  height: 600px;
  border-radius: 20px;
  display: flex;
  overflow: hidden;
}

/* 左侧：品牌侧边栏 */
.auth-sidebar {
  width: 400px;
  padding: 60px 40px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  color: #334155;

  .brand-header {
    display: flex;
    align-items: center; /* 垂直居中 */
    gap: 15px; /* 图片和文字间距 */
    margin-bottom: 20px;

    .brand-logo {
      width: 48px;
      height: 48px;
      display: block;
    }

    .brand-name {
      font-size: 28px;
      font-weight: 700;
      color: #0f172a;
      letter-spacing: 0.5px;
      line-height: 1;
    }
  }

  .main-slogan {
    font-size: 24px;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 8px;
  }

  .sub-slogan {
    font-size: 14px;
    color: #64748b;
    margin-bottom: 40px;
  }

  .feature-list {
    display: flex;
    flex-direction: column;
    gap: 20px;

    .feature-item {
      display: flex;
      align-items: center;
      gap: 12px;
      font-size: 14px;
      color: #475569;

      .el-icon {
        font-size: 18px;
        color: #3b82f6; /* 图标保持品牌蓝 */
        background: #dbeafe;
        padding: 6px;
        border-radius: 6px;
        box-sizing: content-box;
      }
    }
  }

  .sidebar-footer {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;

    .copyright-info {
      display: flex;
      flex-direction: column;
      gap: 2px;
      :hover {
        color: #1b6df2 !important;
      }
      .copyright {
        font-size: 14px;
        color: #94a3b8;
        margin: 0;
      }
    }

    .github-link {
      display: flex;
      align-items: center;
      gap: 4px;
      color: #64748b;
      text-decoration: none;
      transition: color 0.2s;
      font-size: 13px;

      &:hover {
        color: #3b82f6;
      }

      .el-icon {
        font-size: 14px;
      }
    }
  }
}

/* 移动端专用头部 */
.mobile-header {
  display: none; /* PC端隐藏 */
}

/* 右侧：表单区 */
.auth-form-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 40px;
}

.form-wrapper {
  width: 360px;

  .auth-header {
    margin-bottom: 30px;
    text-align: left;

    .auth-title {
      font-size: 26px;
      font-weight: 700;
      color: #0f172a;
      margin-bottom: 8px;
    }
    .auth-subtitle {
      font-size: 14px;
      color: #64748b;
    }
  }
}

/* 改造 Tabs 样式 */
.custom-tabs {
  :deep(.el-tabs__item) {
    font-size: 16px;
    color: #64748b;
    padding: 0 20px 10px 0; /* 左对齐Tab */
    height: auto;
  }

  :deep(.el-tabs__item.is-active) {
    color: #3b82f6;
    font-weight: 600;
  }

  :deep(.el-tabs__active-bar) {
    background-color: #3b82f6;
    height: 3px;
    border-radius: 2px;
  }

  :deep(.el-tabs__nav-wrap::after) {
    height: 1px;
    background-color: #f1f5f9;
  }
}

/* 输入框样式微调 */
.auth-form {
  margin-top: 20px;

  :deep(.el-input__wrapper) {
    box-shadow: none;
    background: #f8fafc; /* 极淡灰蓝背景 */
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    transition: all 0.2s;
    padding: 1px 11px;

    &:hover {
      border-color: #cbd5e1;
    }

    &.is-focus {
      background: #fff;
      border-color: #3b82f6;
      box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1); /* 柔和的蓝色光晕 */
    }
  }

  :deep(.el-input__inner) {
    height: 44px;
    color: #334155;
  }
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 24px;
  margin-top: -10px;

  .forget-link {
    color: #64748b;
    font-size: 13px;
    &:hover {
      color: #3b82f6;
    }
  }
}

.submit-btn {
  width: 100%;
  height: 46px;
  font-size: 16px;
  border-radius: 8px;
  background: #3b82f6;
  border: none;
  font-weight: 500;

  &:hover {
    background: #2563eb;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
  }
}

.code-btn {
  font-size: 14px;
  font-weight: 500;
  color: #3b82f6;
  padding: 0;
  margin-right: 8px;

  &:hover {
    color: #2563eb;
  }

  &.is-disabled {
    color: #9ca3af;
  }
}

.form-footer {
  text-align: center;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #f1f5f9;

  .footer-text {
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    color: #94a3b8;
    line-height: 1.5;
  }

  .footer-link {
    font-size: 12px;
    font-weight: 500;
    color: #3b82f6;
  }
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .auth-box {
    width: 100%;
    height: 100%;
    border-radius: 0;
    flex-direction: column;
    box-shadow: none;
  }

  .auth-sidebar {
    display: none;
  }

  .mobile-header {
    display: block; /* 移动端显示 */
    width: 100%;
    text-align: center;
    margin-bottom: 20px;
    padding-bottom: 20px;
    border-bottom: 1px solid #f1f5f9;
  }

  .mobile-brand {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;

    .mobile-logo {
      width: 40px;
      height: 40px;
    }

    .mobile-text {
      text-align: left;

      .mobile-title {
        font-size: 22px;
        font-weight: 700;
        color: #0f172a;
        margin: 0;
        line-height: 1.2;
      }

      .mobile-subtitle {
        font-size: 13px;
        color: #64748b;
        margin: 2px 0 0 0;
      }
    }
  }

  .auth-form-container {
    flex: none;
    padding: 20px 24px;
  }

  .form-wrapper {
    width: 100%;
    max-width: 400px;
  }

  .auth-header {
    text-align: center;
    margin-bottom: 24px;

    .auth-title {
      font-size: 22px;
    }

    .auth-subtitle {
      font-size: 13px;
    }
  }

  .custom-tabs {
    :deep(.el-tabs__item) {
      font-size: 15px;
      padding: 0 12px 8px;
    }
  }
}

/* 表单验证错误样式 */
:deep(.el-form-item.is-error .el-input__wrapper) {
  border-color: #ef4444;
}

:deep(.el-form-item__error) {
  font-size: 12px;
  line-height: 1.4;
  padding-top: 4px;
}

/* 加载状态样式 */
.submit-btn.is-loading {
  opacity: 0.8;
  cursor: not-allowed;
}
</style>
