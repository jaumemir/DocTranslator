<script lang="ts" setup>
import { reactive, ref } from "vue"
import { useRouter } from "vue-router"
import { useUserStore } from "@/store/modules/user"
import { type FormInstance, type FormRules } from "element-plus"
//import { getLoginCodeApi } from "@/api/login"
import { type LoginRequestData } from "@/api/login/types/login"

const router = useRouter()
/** Login form element reference */
const loginFormRef = ref<FormInstance | null>(null)

/** Login button loading state */
const loading = ref(false)
/** Verification code image URL */
//const codeUrl = ref("")
/** Login form data */
const loginFormData: LoginRequestData = reactive({
  email: "",
  password: ""
  // code: ""
})
/** Login form validation rules */
const loginFormRules: FormRules = {
  email: [{ required: true, message: "Please enter your login email", trigger: "blur" }],
  password: [
    { required: true, message: "Please enter your password", trigger: "blur" },
    { min: 6, max: 16, message: "Length must be between 6 and 16 characters", trigger: "blur" }
  ]
  // code: [{ required: true, message: "Please enter verification code", trigger: "blur" }]
}
/** Login logic */
const handleLogin = () => {
  loginFormRef.value?.validate((valid: boolean, fields) => {
    if (valid) {
      loading.value = true
      useUserStore()
        .login(loginFormData)
        .then(() => {
          router.push({ path: "/" })
        })
        .catch(() => {
          loginFormData.password = ""
        })
        .finally(() => {
          loading.value = false
        })
    } else {
      console.error("Form validation failed", fields)
    }
  })
}
/** Create verification code */
/*const createCode = () => {
  // Clear verification code input first
  // loginFormData.code = ""
  // Get verification code
  codeUrl.value = ""
  getLoginCodeApi().then((res) => {
    codeUrl.value = res.data
  })
}*/

/** Initialize verification code */
// createCode()
</script>

<template>
  <div class="login-container">
    <img class="login_bg" src="@/assets/login/login_bg.png" alt="" />

    <div class="login-card">
      <div class="title">
        <img src="@/assets/login/login_title.png" />
      </div>
      <div class="content">
        <el-form
          ref="loginFormRef"
          label-position="top"
          :hide-required-asterisk="true"
          :model="loginFormData"
          :rules="loginFormRules"
          @keyup.enter="handleLogin"
        >
          <el-form-item label="Username" prop="email">
            <el-input
              v-model.trim="loginFormData.email"
              placeholder="Please enter your login email"
              type="text"
              tabindex="1"
              size="large"
            />
          </el-form-item>
          <el-form-item label="Password" prop="password">
            <el-input
              v-model.trim="loginFormData.password"
              placeholder="Password"
              type="password"
              tabindex="2"
              size="large"
              show-password
            />
          </el-form-item>
          <!-- <el-form-item prop="code">
            <el-input
              v-model.trim="loginFormData.code"
              placeholder="Verification code"
              type="text"
              tabindex="3"
              :prefix-icon="Key"
              maxlength="7"
              size="large"
            >
              <template #append>
                <el-image :src="codeUrl" @click="createCode" draggable="false">
                  <template #placeholder>
                    <el-icon>
                      <Picture />
                    </el-icon>
                  </template>
                  <template #error>
                    <el-icon>
                      <Loading />
                    </el-icon>
                  </template>
                </el-image>
              </template>
            </el-input>
          </el-form-item> -->
          <el-button :loading="loading" type="primary" size="large" @click.prevent="handleLogin">Login</el-button>
        </el-form>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.login-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  width: 100%;
  min-height: 100%;
  .login_bg {
    position: absolute;
    width: 100%;
    height: 100%;
  }
  .login-card {
    position: relative;
    z-index: 99;
    width: 432px;
    max-width: 85%;
    background: #ffffff;
    box-shadow: 0px 2px 15px 0px rgba(0, 0, 0, 0.15);
    border-radius: 16px;
    overflow: hidden;
    padding: 36px;
    .title {
      display: flex;
      justify-content: left;
      align-items: center;
      height: 48px;
      margin-top: 12px;
      img {
        height: 100%;
      }
    }
    .content {
      padding: 0;
      .el-button {
        width: 100%;
        margin-top: 30px;
        background: #045cf9;
        margin-bottom: 30px;
        font-size: 18px;
      }
      .el-form-item {
        margin-top: 25px;
        :deep(.el-form-item__label) {
          font-weight: bold;
          font-size: 16px;
          color: #00334d;
        }
      }
    }
  }
}
</style>
