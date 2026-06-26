<template>
  <div class="security-settings">
    <!-- 卡片容器 -->
    <el-card class="settings-card">
      <!-- Title Area -->
      <div class="card-header">
        <h2 class="title">Account Security Settings</h2>
        <p class="subtitle">Please modify your account information carefully</p>
      </div>

      <!-- Form Area -->
      <el-form ref="formRef" :model="formData" :rules="rules" label-position="top" class="settings-form">
        <!-- Username Modification -->
        <el-form-item label="Username" prop="user">
          <el-input v-model="formData.user" placeholder="Please enter new username (email)" clearable :prefix-icon="User" />
        </el-form-item>

        <!-- Password Modification -->
        <el-form-item label="Current Password" prop="old_password">
          <el-input
            v-model="formData.old_password"
            type="password"
            show-password
            placeholder="Please enter current password"
            :prefix-icon="Lock"
          />
        </el-form-item>

        <el-form-item label="New Password" prop="new_password">
          <el-input
            v-model="formData.new_password"
            type="password"
            show-password
            placeholder="6-16 characters length"
            :prefix-icon="Key"
          />
        </el-form-item>

        <el-form-item label="Confirm New Password" prop="confirm_password">
          <el-input
            v-model="formData.confirm_password"
            type="password"
            show-password
            placeholder="Please enter new password again"
            :prefix-icon="Key"
          />
        </el-form-item>

        <!-- Action Buttons -->
        <el-form-item class="form-actions">
          <el-button type="primary" :loading="submitting" @click="handleSubmit"> Save Changes </el-button>
          <el-button @click="handleReset">Reset</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue"
import { useRouter } from "vue-router"
import { ElMessage } from "element-plus"
import { User, Lock, Key } from "@element-plus/icons-vue"
import { updatePasswordApi } from "@/api/login"
const formRef = ref()
const submitting = ref(false)
const router = useRouter()
// 表单数据
const formData = reactive({
  user: "",
  old_password: "",
  new_password: "",
  confirm_password: ""
})

// Username validation
// const validateUsername = (rule, value, callback) => {
//   if (!value) {
//    callback(new Error("Username cannot be empty"))
//    }
//   if (value.length < 6 || value.length > 16) {
//     callback(new Error("Username length must be between 6 and 16 characters"))
//   } else {
//     callback()
//   }
// }

// Password complexity validation
const validatePassword = (rule, value, callback) => {
  if (value.length < 6) {
    callback(new Error("Password must be at least 6 characters"))
  } else {
    callback()
  }
}

// Confirm password validation
const validateConfirm = (rule, value, callback) => {
  if (value !== formData.new_password) {
    callback(new Error("Passwords do not match"))
  } else {
    callback()
  }
}

// Form validation rules
const rules = {
  // user: [{ required: false, validator: validateUsername, trigger: "blur" }],
  old_password: [{ required: true, message: "Please enter current password", trigger: "blur" }],
  new_password: [
    { required: true, message: "Please enter new password", trigger: "blur" },
    { validator: validatePassword, trigger: "blur" }
  ],
  confirm_password: [
    { required: true, message: "Please confirm new password", trigger: "blur" },
    { validator: validateConfirm, trigger: "blur" }
  ]
}

// Submit form
const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true
    // Password change request
    const res = await updatePasswordApi(formData)
    if (res.code === 200) {
      submitting.value = false
      ElMessage.success("Update successful")
      router.push("/login")
    } else {
      submitting.value = false
      ElMessage.error("Update failed, please try again")
    }
  } catch (error) {
    ElMessage.error(error.message || "Update failed")
    submitting.value = false
  }
}

// Reset form
const handleReset = () => {
  formRef.value.resetFields()
}
</script>

<style lang="scss" scoped>
.security-settings {
  padding: 10px;
  display: flex;
  max-width: 1400px;
  justify-content: center;
  align-items: center;
  height: 100%;
  // min-height: calc(100vh - 64px);
  background-color: #f5f7fa; // 浅灰色背景
}

.settings-card {
  width: 100%;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-header {
  width: 50%;
  margin-bottom: 24px;

  .title {
    font-size: 20px;
    font-weight: 600;
    color: #303133;
    margin-bottom: 8px;
  }

  .subtitle {
    font-size: 14px;
    color: #909399;
  }
}

.settings-form {
  width: 40%;

  :deep(.el-form-item__label) {
    font-weight: 500;
    color: #606266;
    padding-bottom: 8px;
  }

  :deep(.el-input__inner) {
    border-radius: 8px;
    transition: border-color 0.3s ease;

    &:hover {
      border-color: #c0c4cc;
    }
  }

  .form-actions {
    margin-top: 32px;
    text-align: center;

    .el-button {
      width: 120px;
      font-size: 14px;
      border-radius: 8px;
    }

    .el-button--primary {
      background-color: #409eff;
      border-color: #409eff;

      &:hover {
        opacity: 0.9;
      }
    }
  }
}
</style>
