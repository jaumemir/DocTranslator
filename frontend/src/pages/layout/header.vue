<template>
  <div class="page-header">
    <div class="head-box">
      <div class="logo">
        <img src="@/assets/logo.png" class="logo_img" alt="DocTranslator" />
        <span>{{ settingsStore.siteTitle }}</span>
        <a class="btn_return" href="https://www.ehemart.com/" v-if="false"><<返回官网</a>
        <img
          class="icon_vip phone_show"
          style="height: 16px; margin-left: 10px"
          v-if="false"
          src="@/assets/vip.png"
          alt=""
        />
      </div>
      <!-- Navigation menu -->
      <div class="btn-box">
        <template v-if="userStore.token">
          <div class="flex-center">
            <div class="btn_set" @click="funOpenHome">
              <div class="icon_svg"><svg-icon icon-class="home" /></div>
              <span class="pc_show">首页</span>
            </div>
            <div class="btn_set" @click="funOpenCorpus">
              <div class="icon_svg"><svg-icon icon-class="corpus" /></div>
              <span class="pc_show">语料库</span>
            </div>
            <div class="btn_set" @click="funOpenSet">
              <div class="icon_svg"><svg-icon icon-class="setting" /></div>
              <span class="pc_show">翻译设置</span>
            </div>
            <div
              class="btn_set"
              @click="windowOpen('https://github.com/mingchen666/DocTranslator')"
            >
              <div class="icon_svg"><svg-icon icon-class="github" /></div>
              <span class="pc_show">Github</span>
            </div>
            <div class="btn_set" @click="$router.push('/profile')">
              <!-- <div class="icon_svg"><svg-icon icon-class="user" /></div> -->
              <el-icon class="icon_svg"><UserFilled /></el-icon>
              <span class="pc_show">个人中心</span>
            </div>
            <!-- <img
              class="icon_vip pc_show"
              v-if="userStore.userInfo.level == 'vip'"
              src="@/assets/vip.png"
              alt=""
            /> -->
            <el-dropdown placement="bottom-end" @command="user_action">
              <template #default>
                <div>
                  <el-button class="pc_show">
                    <div class="username">{{ userStore.userInfo.email }}</div>
                    <el-icon class="el-icon--right"><arrow-down /></el-icon>
                  </el-button>
                  <div class="phone_show icon_more">
                    <el-icon><MoreFilled /></el-icon>
                  </div>
                </div>
              </template>

              <template #dropdown>
                <el-dropdown-menu>
                  <!-- <el-dropdown-item command="profile">个人中心</el-dropdown-item> -->
                  <el-dropdown-item command="pwd">修改密码</el-dropdown-item>
                  <el-dropdown-item command="exit">退出</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </template>
        <template v-else>
          <el-button class="pc_show" @click="$router.push('/login')">登录/注册</el-button>
          <el-icon class="phone_show icon_user" @click="$router.push('/login')"><User /></el-icon>
        </template>
      </div>
    </div>

    <!-- Logout dialog -->
    <el-dialog
      v-model="logoutVisible"
      modal-class="custom_dialog"
      center
      :show-close="false"
      width="90%"
      heigt="240px"
      style="border-radius: 20px"
    >
      <div class="dialog-container">
        <div class="dialog-title">退出登录</div>
        <div class="dialog-content">您确定要退出登录吗？</div>
        <div class="dialog-btns">
          <el-button class="dialog-btn cancel" @click="logoutVisible = false">取消</el-button>
          <el-button
            class="dialog-btn confirm"
            type="primary"
            color="#055CF9"
            @click="confirmLogout"
            >确认</el-button
          >
        </div>
      </div>
    </el-dialog>

    <!-- Translation settings component -->
    <translation-settings ref="translationSettings" />
  </div>
</template>
<script setup>
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { useSettingsStore } from '@/store/settings'
import { useTranslateStore } from '@/store/translate'
import { authInfo } from '@/api/account'
import { ref, onMounted } from 'vue'
import SvgIcon from '@/components/SvgIcon/index.vue'
import { UserFilled } from '@element-plus/icons-vue'
import TranslationSettings from '@/components/TranslationSettings.vue'
import { getSystemSetting, getTranslateSetting } from '@/api/settings'
const userStore = useUserStore()
const translationSettings = ref(null)
const settingsStore = useSettingsStore()
const translateStore = useTranslateStore()
const router = useRouter()

const logoutVisible = ref(false)
const langMultipleLimit = ref(5)

// Get user info
const getUserInfo = async () => {
  try {
    const res = await authInfo()
    if (res.code === 200) {
      userStore.updateUserInfo(res.data)
    }
  } catch (error) {
    console.error('Failed to get user info:', error)
  }
}

// User actions
function user_action(command) {
  if (command == 'pwd') {
    router.push('/password')
  }
  if (command == 'exit') {
    logoutVisible.value = !logoutVisible.value
    router.push('/login')
  }
  if (command == 'profile') {
    router.push('/profile')
  }
}

// Open translation settings dialog
function funOpenSet() {
  translationSettings.value.open()
  // formSetShow.value = true
}

// Open corpus
function funOpenCorpus() {
  router.push('/corpus')
}

// Go to home
function funOpenHome() {
  router.push('/')
}

// Demo entry point
function windowOpen(url) {
  window.open(url)
}

// Confirm logout
function confirmLogout() {
  userStore.logout()
  logoutVisible.value = false
}

// Get default translation settings
const getTranslateSettingInfo = async () => {
  const res = await getTranslateSetting()
  if (res.code === 200) {
    // Update system settings store
    settingsStore.updateSystemSettings(res.data)
  }
}
onMounted(() => {
  getUserInfo()
  getTranslateSettingInfo()
})
</script>
<style scoped lang="scss">
.page-header {
  width: 100%;
  height: 60px;
  background: #ffffff;
  box-shadow: 0px 0px 12px 0px rgba(0, 22, 52, 0.05);
}
.head-box {
  max-width: 1240px;
  padding: 0 20px;
  margin: 0 auto;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.logo {
  display: flex;
  align-items: center;
  img {
    height: 44px;
  }
  span {
    font-size: 20px;
    font-weight: bold;
    margin-left: 20px;
  }
  .btn_return {
    color: #045cf9;
    margin-left: 10px;
    font-size: 14px;
    text-decoration: none;
    cursor: pointer;
  }
}
::v-deep {
  .btn_set {
    display: flex;
    align-items: center;
    margin-right: 20px;
    font-size: 14px;
    color: #000000;
    cursor: pointer;
    img {
      margin-right: 8px;
    }
    .icon_svg {
      margin-right: 8px;
      font-size: 16px;
      color: #666;
    }
    &:hover {
      color: #045cf9;
      .icon_svg {
        color: #045cf9;
      }
    }
  }
  .icon_vip {
    margin-right: 12px;
  }
  .username {
    max-width: 150px;
    overflow: hidden;
    text-overflow: ellipsis;
    line-height: 30px;
  }
  .el-dropdown {
    .el-tooltip__trigger {
      outline: none;
    }
    .el-button {
      outline: none;
    }
  }

  .custom_dialog {
    .el-dialog__header {
      padding-bottom: 0;
      font-size: 16px;
      color: #111;
    }
    .el-dialog {
      max-width: 410px;
      padding: 20px;
    }
  }
  .custom_2_dialog {
    .el-dialog {
      max-width: 410px;
    }
  }
  .change_dialog {
    .el-dialog {
      padding: 20px 40px;
    }
    .el-dialog__header {
      margin-top: 10px;
      margin-bottom: 20px;
    }
  }

  .dialog-container {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
  }
  .dialog-title {
    font-weight: bold;
    font-size: 20px;
    color: #111111;
    line-height: 24px;
    margin-top: 30px;
    margin-bottom: 20px;
  }
  .dialog-content {
    font-family: 'PingFang SC';
    font-weight: 400;
    font-size: 16px;
    color: #999999;
    line-height: 24px;
    margin-bottom: 40px;
  }
  .dialog-btns {
    margin-bottom: 30px;
  }
  .dialog-btn {
    width: 120px;
  }
  .dialog-btn.cancel {
    margin-right: 4px;
  }
  .dialog-btn.send-confirm {
    width: 327px;
  }
  .login_dialog1 {
    .el-dialog {
      padding: 20px 40px;
    }
    .el-menu {
      border: none;
      height: 65px;
    }
    .el-menu-item {
      padding: 0;
      height: 40px;
      font-size: 20px;
      font-family: PingFang SC;
      margin: 0 15px;
      background: #fff !important;
    }
  }
  .forget-title {
    display: flex;
    justify-content: space-between;
    margin-top: 10px;
    margin-bottom: 30px;
    .el-text {
      font-size: 22px;
      color: #111111;
    }
    .el-icon {
      font-size: 24px;
    }
  }

  .setting_dialog {
    .el-dialog {
      max-width: 800px;
      padding: 30px 70px;
    }
    .el-dialog__title {
      color: #111111;
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
      padding: 0 30px 0 30px;
    }
    .el-form-item {
      .el-form-item__label {
        justify-content: flex-start;
        color: #111111;
      }
    }
    .btn_box {
      position: relative;
      text-align: center;
      .btn_check {
        position: absolute;
        left: 0;
        .el-tag {
          height: 28px;
          margin-left: 10px;
        }
      }
      .custom_btn {
        background: #fff;
        color: #055cf9;
        height: 28px;
        padding: 0 10px;
        &:hover {
          color: #055cf9;
          background: var(--el-color-primary-light-9);
        }
      }
    }
  }
  .no_label {
    label {
      opacity: 0;
    }
    .flex_box {
      width: 100%;
      .el-input {
        flex: 1;
        margin-right: 10px;
      }
    }
  }
}
</style>
<style type="text/css" lang="scss">
.flex_box {
  display: flex;
  align-items: center;
}
.flex-between {
  justify-content: space-between;
}
.flex-center {
  display: flex;
  align-items: center;
  justify-content: space-around;
}
.menu-center {
  justify-content: center;
}
.menu-title {
  font-family: 'PingFang SC';
  font-weight: bold;
  font-size: 22px;
  color: #8f8f91;
  line-height: 24px;
}
.menu-title.active {
  color: #111111;
}
.phone_show {
  display: none !important;
}

.language-selection {
  display: flex;
  align-items: center;
  gap: 10px; /* Adjust gap between elements */
  width: 100%;
}
.lang-select {
  width: 100%; /* Default width is 100% */
  transition: width 0.3s ease; /* Add transition effect */
}
.language-selection:has(.conversion-symbol) .lang-select {
  width: 100%; /* Set width to 45% when conversion symbol is present */
}
.conversion-symbol {
  font-size: 20px;
  color: #409eff; /* Use Element Plus primary color, adjust as needed */
  flex-shrink: 0; /* Prevent symbol from being compressed */
}
@media screen and (max-width: 767px) {
  .pc_show {
    display: none !important;
  }
  .phone_show {
    display: inline-block !important;
  }
  .icon_user {
    font-size: 30px !important;
  }
  .logo span {
    font-size: 14px !important;
    margin-left: 10px !important;
  }
  .icon_more {
    font-size: 20px;
  }
  .btn_set {
    margin-right: 6px !important;
  }
  .logo_img {
    height: 30px !important;
  }

  .setting_dialog {
    .el-dialog {
      padding: 20px !important;
    }
    .el-dialog__body {
      padding: 0 !important;
      max-height: 300px;
      overflow-y: auto;
      .el-form-item {
        display: block !important;
        margin-bottom: 10px;
      }
    }
    .btn_box {
      text-align: right !important;
    }
  }

  .no_label {
    label {
      display: none;
    }
  }
}
</style>
