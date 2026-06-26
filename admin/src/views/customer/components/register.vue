<template>
  <el-form :model="user" ref="userform" label-width="auto" :rules="rules">
    <el-form-item prop="email" label="Email">
      <el-input v-model="user.email" placeholder="Please enter email" autocomplete="new-password" />
    </el-form-item>
    <el-form-item prop="level" label="User Level">
      <el-select v-model="user.level" placeholder="">
        <el-option label="VIP User" value="vip" />
        <el-option label="Regular User" value="common" />
      </el-select>
    </el-form-item>
    <el-form-item prop="password" label="Password">
      <el-input type="password" v-model="user.password" placeholder="Please enter" autocomplete="new-password" />
    </el-form-item>
    <el-form-item label="" class="center">
      <el-button type="primary" size="large" color="#055CF9" @click="doRegister()" style="width: 100%">Submit</el-button>
    </el-form-item>
  </el-form>
</template>
<script setup lang="ts">
import { ref, reactive } from "vue"
import { registerCustomer } from "@/api/customer/index"
import { FormInstance, ElMessage } from "element-plus"
import { CreateOrUpdateCustomerRequestData } from "@/api/customer/types/customer"
import { cloneDeep } from "lodash-es"

const emit = defineEmits(["success"])

const DEFAULT_FORM_DATA: CreateOrUpdateCustomerRequestData = {
  email: "",
  password: "",
  level: "common"
}

const user = ref<CreateOrUpdateCustomerRequestData>(cloneDeep(DEFAULT_FORM_DATA))

const userform = ref<FormInstance | null>(null)
const rules = reactive({
  email: [{ required: true, message: "Please enter email address", trigger: "blur" }],
  level: [{ required: true, message: "Please select user level" }],
  password: [{ required: true, message: "Please enter password", trigger: "blur" }]
})
const doRegister = () => {
  userform.value?.validate((valid: boolean, fields: any) => {
    if (!valid) return console.error("Form validation failed", fields)
    registerCustomer(user.value)
      .then(() => {
        ElMessage.success("Operation successful")
        emit("success")
        user.value = cloneDeep(DEFAULT_FORM_DATA)
      })
      .finally(() => {})
  })
}
</script>
<style scoped lang="scss">
:v-deep {
  .right .el-form-item__content {
    justify-content: end;
  }
  .center .el-form-item__content {
    justify-content: center;
  }
}
</style>
