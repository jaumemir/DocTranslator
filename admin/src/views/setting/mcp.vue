<script lang="ts" setup>
import { ref, reactive, onMounted, computed } from "vue"
import { ElMessage, ElMessageBox } from "element-plus"
import { Plus, CopyDocument, Delete, RefreshRight, Connection, Search } from "@element-plus/icons-vue"
import ResponsiveModal from "@/components/ResponsiveModal/index.vue"
import {
  getAdminMcpKeys,
  createAdminMcpKey,
  getAdminMcpKeyDetail,
  updateAdminMcpKey,
  deleteAdminMcpKey,
  regenerateAdminMcpKey,
  searchCustomers,
  getAdminPromptList
} from "@/api/mcp"

const loading = ref(false)
const keys = ref<any[]>([])
const currentAdminKeys = ref(0)
const maxKeys = ref(3)
const activeTab = ref("user")

const mcpPort = window.__MCP_PORT__ || (window.location.port === "5000" ? "5001" : window.location.port)
const mcpBaseUrl = `${window.location.protocol}//${window.location.hostname}:${mcpPort}`
const adminMcpUrl = computed(() => `${mcpBaseUrl}/mcp/admin`)
const userMcpUrl = computed(() => `${mcpBaseUrl}/mcp/user`)

const fetchKeys = () => {
  loading.value = true
  getAdminMcpKeys()
    .then(({ data }: any) => {
      keys.value = data || []
      currentAdminKeys.value = data.current_admin_keys || 0
      maxKeys.value = data.max_keys || 3
    })
    .finally(() => {
      loading.value = false
    })
}

const userKeys = computed(() => keys.value.filter((k) => k.scope === "user"))
const adminKeys = computed(() => keys.value.filter((k) => k.scope === "admin"))

const typeOptions = [
  {
    value: "trans_text",
    label: "Text Only",
    children: [
      {
        value: "trans_text_only",
        label: "Translation Only",
        children: [
          { value: "trans_text_only_new", label: "Reformat Layout" },
          { value: "trans_text_only_inherit", label: "Inherit Original Layout" }
        ]
      },
      {
        value: "trans_text_both",
        label: "Original + Translation",
        children: [
          { value: "trans_text_both_new", label: "Reformat Layout" },
          { value: "trans_text_both_inherit", label: "Inherit Original Layout" }
        ]
      }
    ]
  },
  {
    value: "trans_all",
    label: "All Content",
    children: [
      {
        value: "trans_all_only",
        label: "Translation Only",
        children: [
          { value: "trans_all_only_new", label: "Reformat Layout" },
          { value: "trans_all_only_inherit", label: "Inherit Original Layout" }
        ]
      },
      {
        value: "trans_all_both",
        label: "Original + Translation",
        children: [
          { value: "trans_all_both_new", label: "Reformat Layout" },
          { value: "trans_all_both_inherit", label: "Inherit Original Layout" }
        ]
      }
    ]
  }
]

const languageOptions = [
  { label: "Chinese", value: "中文" },
  { label: "English", value: "英语" },
  { label: "Japanese", value: "日语" },
  { label: "Korean", value: "韩语" },
  { label: "French", value: "法语" },
  { label: "German", value: "德语" },
  { label: "Spanish", value: "西班牙语" },
  { label: "Russian", value: "俄语" },
  { label: "Portuguese", value: "葡萄牙语" },
  { label: "Arabic", value: "阿拉伯语" }
]

const createVisible = ref(false)
const createLoading = ref(false)
const createForm = reactive({
  name: "",
  scope: "user" as "user" | "admin",
  customer_id: null as number | null,
  config: {
    api_url: "",
    api_key: "",
    model: "",
    type: "trans_all_only_inherit",
    prompt_id: 0,
    backup_model: "",
    threads: 5,
    lang: "Chinese",
    comparison_id: null as number | null,
    doc2x_flag: "N",
    doc2x_secret_key: ""
  }
})

const customerSearch = ref("")
const customerLoading = ref(false)
const customerList = ref<any[]>([])

const promptList = ref<any[]>([])
const promptLoading = ref(false)
  const default_prompt = ref(`You are a document translation assistant. Please translate the following content directly into {target_lang} without returning the original text. If the text contains {target_lang} text, special terms (such as email addresses, brand names, unit names like mm, px, ℃, etc.), or untranslatable content, return the original term directly without explanation. For untranslatable text, return the original content. Preserve extra spaces.`)

const fetchPromptList = () => {
  promptLoading.value = true
  getAdminPromptList()
    .then(({ data }: any) => {
      promptList.value = [{ id: 0, title: 'Default System Prompt', content: default_prompt.value }, ...(data.data || [])]
    })
    .finally(() => {
      promptLoading.value = false
    })
}

const getSelectedPromptContent = (promptId: number) => {
  const p = promptList.value.find(item => item.id === promptId)
  return p ? p.content : ''
}

const searchCustomerList = (keyword: string) => {
  if (!keyword) { customerList.value = []; return }
  customerLoading.value = true
  searchCustomers(keyword)
    .then(({ data }: any) => {
      customerList.value = (data.data?.list || data.data || []).slice(0, 10)
    })
    .finally(() => {
      customerLoading.value = false
    })
}

const resetCreateForm = () => {
  createForm.name = ""
  createForm.scope = "user"
  createForm.customer_id = null
  createForm.config = {
    api_url: "", api_key: "", model: "",
    type: "trans_all_only_inherit", prompt_id: 0, backup_model: "",
    threads: 5, lang: "中文", comparison_id: null,
    doc2x_flag: "N", doc2x_secret_key: ""
  }
  customerSearch.value = ""
  customerList.value = []
}

const openCreateDialog = (scope: "user" | "admin") => {
  resetCreateForm()
  createForm.scope = scope
  createVisible.value = true
}

const handleCreate = () => {
  if (!createForm.name) { ElMessage.warning("Please enter key name"); return }
  if (createForm.scope === "user" && !createForm.customer_id) {
    ElMessage.warning("Please select a user"); return
  }
  if (createForm.scope === "admin") {
    if (!createForm.config.api_url || !createForm.config.api_key || !createForm.config.model) {
      ElMessage.warning("Admin keys must include API URL, API key and model"); return
    }
  }
  createLoading.value = true
  createAdminMcpKey({
    name: createForm.name,
    scope: createForm.scope,
    customer_id: createForm.scope === "user" ? createForm.customer_id : undefined,
    config: { ...createForm.config }
  })
    .then((res: any) => {
      if (res.code === 200) {
        createVisible.value = false
        showNewKeyDialog(res.data.key)
        fetchKeys()
      } else {
        ElMessage.error(res.message || "Creation failed")
      }
    })
    .finally(() => {
      createLoading.value = false
    })
}

const newKeyVisible = ref(false)
const newKeyValue = ref("")

const showNewKeyDialog = (key: string) => {
  newKeyValue.value = key
  newKeyVisible.value = true
}

const copyText = (text: string) => {
  navigator.clipboard.writeText(text).then(() => ElMessage.success("Copied"))
}

const editVisible = ref(false)
const editLoading = ref(false)
const editKeyPrefix = ref("")
const editForm = reactive({
  name: "",
  scope: "user" as "user" | "admin",
  customer_email: "",
  config: {
    api_url: "", api_key: "", model: "",
    type: "trans_all_only_inherit", prompt_id: 0, backup_model: "",
    threads: 5, lang: "中文", comparison_id: null as number | null,
    doc2x_flag: "N", doc2x_secret_key: ""
  }
})

const openEditDialog = (row: any) => {
  editKeyPrefix.value = row.key_prefix
  getAdminMcpKeyDetail(row.key_prefix).then(({ data }: any) => {
    const d = data
    editForm.name = d.name || ""
    editForm.scope = d.scope || "user"
    editForm.customer_email = d.customer_email || ""
    if (d.config) Object.assign(editForm.config, d.config)
    editVisible.value = true
  })
}

const handleEdit = () => {
  if (!editForm.name) { ElMessage.warning("Please enter key name"); return }
  editLoading.value = true
  updateAdminMcpKey(editKeyPrefix.value, {
    name: editForm.name,
    config: { ...editForm.config }
  })
    .then((res: any) => {
      if (res.code === 200) {
        editVisible.value = false
        ElMessage.success("Updated successfully")
        fetchKeys()
      } else {
        ElMessage.error(res.message || "Update failed")
      }
    })
    .finally(() => {
      editLoading.value = false
    })
}

const handleDelete = (row: any) => {
  ElMessageBox.confirm(
    `Confirm delete key「${row.name || row.key_prefix}」? This cannot be undone.`,
    "Delete Confirmation",
    { confirmButtonText: "Confirm Delete", cancelButtonText: "Cancel", type: "warning" }
  ).then(() => {
    deleteAdminMcpKey(row.key_prefix).then(() => {
      ElMessage.success("Deleted")
      fetchKeys()
    })
  })
}

const handleRegenerate = (row: any) => {
  ElMessageBox.confirm(
    `Regenerate key「${row.name || row.key_prefix}」? The old key will be immediately invalidated.`,
    "Regenerate Confirmation",
    { confirmButtonText: "Confirm Regenerate", cancelButtonText: "Cancel", type: "warning" }
  ).then(() => {
    regenerateAdminMcpKey(row.key_prefix).then((res: any) => {
      if (res.data?.key) showNewKeyDialog(res.data.key)
      fetchKeys()
    })
  })
}

const getTypeLabel = (val: string) => {
  const find = (opts: any[]): string => {
    for (const t of opts) {
      if (t.value === val) return t.label
      if (t.children) {
        const child = find(t.children)
        if (child) return t.label + ' / ' + child
      }
    }
    return ''
  }
  return find(typeOptions) || val
}

onMounted(() => {
  fetchKeys()
  fetchPromptList()
})
</script>

<template>
  <div class="app-container">
    <div class="mcp-page" v-loading="loading">
      <div class="mcp-header">
        <div class="mcp-header-left">
          <el-icon :size="22" color="#3b82f6"><Connection /></el-icon>
          <h3 class="mcp-title">MCP Key Management</h3>
        </div>
        <div class="mcp-header-right">
          <el-button type="primary" :icon="Plus" @click="openCreateDialog('user')">Create Key for User</el-button>
          <el-button type="primary" plain :icon="Plus" @click="openCreateDialog('admin')" :disabled="currentAdminKeys >= maxKeys">
            Create Admin Key ({{ currentAdminKeys }}/{{ maxKeys }})
          </el-button>
        </div>
      </div>

      <el-tabs v-model="activeTab" class="mcp-tabs">
        <el-tab-pane label="User Keys" name="user">
          <div v-if="false" class="tab-info">
            <span>User connection URL: </span>
            <el-link type="primary" @click="copyText(userMcpUrl)">{{ userMcpUrl }}</el-link>
            <el-icon style="margin-left:2px;cursor:pointer;" @click="copyText(userMcpUrl)"><CopyDocument /></el-icon>
            <span style="margin-left:16px;">Total {{ userKeys.length }} keys</span>
          </div>
          <div class="key-cards" v-if="userKeys.length">
            <div class="mcp-key-card" v-for="key in userKeys" :key="key.key_prefix">
              <div class="key-meta">
                <div class="key-name">{{ key.name || 'Unnamed' }}</div>
                <div class="key-info">
                  <span class="key-prefix"><code>{{ key.key_prefix }}••••</code></span>
                  <el-tag :type="key.status === 'active' ? 'success' : 'danger'" effect="plain" size="small">
                    {{ key.status === 'active' ? 'Enabled' : 'Disabled' }}
                  </el-tag>
                  <span class="key-detail">User: {{ key.customer_email }}</span>
                  <span class="key-detail" v-if="key.config">Model: {{ key.config.model || '-' }}</span>
                  <span class="key-detail" v-if="key.config">Language: {{ key.config.lang || '-' }}</span>
                  <span class="key-detail" v-if="key.config">Type: {{ getTypeLabel(key.config.type) }}</span>
                </div>
                <div class="key-time">Created: {{ key.created_at }} · Last used: {{ key.last_used_at || 'Never' }}</div>
              </div>
              <div class="key-actions">
                <el-button type="primary" text size="small" @click="openEditDialog(key)">Edit</el-button>
                <el-button type="warning" text size="small" @click="handleRegenerate(key)">Regenerate</el-button>
                <el-button type="danger" text size="small" @click="handleDelete(key)">Delete</el-button>
              </div>
            </div>
          </div>
          <div class="no-keys" v-else>
            <div class="empty-visual">🔑</div>
            <p class="empty-title">No user keys yet</p>
            <p class="empty-desc">Click "Create Key for User" above to assign MCP access to users</p>
          </div>
        </el-tab-pane>

        <el-tab-pane label="Admin Keys" name="admin">
          <div v-if="false" class="tab-info">
            <span>Admin connection URL: </span>
            <el-link type="primary" @click="copyText(adminMcpUrl)">{{ adminMcpUrl }}</el-link>
            <el-icon style="margin-left:2px;cursor:pointer;" @click="copyText(adminMcpUrl)"><CopyDocument /></el-icon>
            <span style="margin-left:16px;">Created {{ currentAdminKeys }} / {{ maxKeys }}</span>
          </div>
          <div class="key-cards" v-if="adminKeys.length">
            <div class="mcp-key-card" v-for="key in adminKeys" :key="key.key_prefix">
              <div class="key-meta">
                <div class="key-name">{{ key.name || 'Unnamed' }}</div>
                <div class="key-info">
                  <span class="key-prefix"><code>{{ key.key_prefix }}••••</code></span>
                  <el-tag :type="key.status === 'active' ? 'success' : 'danger'" effect="plain" size="small">
                    {{ key.status === 'active' ? 'Enabled' : 'Disabled' }}
                  </el-tag>
                  <span class="key-detail" v-if="key.config">模型：{{ key.config.model || '-' }}</span>
                  <span class="key-detail" v-if="key.config">语言：{{ key.config.lang || '-' }}</span>
                  <span class="key-detail" v-if="key.config">类型：{{ getTypeLabel(key.config.type) }}</span>
                </div>
                <div class="key-time">Created: {{ key.created_at }} · Last used: {{ key.last_used_at || 'Never' }}</div>
              </div>
              <div class="key-actions">
                <el-button type="primary" text size="small" @click="openEditDialog(key)">Edit</el-button>
                <el-button type="warning" text size="small" @click="handleRegenerate(key)">Regenerate</el-button>
                <el-button type="danger" text size="small" @click="handleDelete(key)">Delete</el-button>
              </div>
            </div>
          </div>
          <div class="no-keys" v-else>
            <div class="empty-visual">🔐</div>
            <p class="empty-title">No Admin Keys</p>
            <p class="empty-desc">Admin Keys can access system management tools (statistics, customer management, translation monitoring, etc.)</p>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- Create Key dialog -->
    <ResponsiveModal v-model="createVisible" :title="createForm.scope === 'admin' ? 'Create Admin Key' : 'Create Key for User'" width="560px" :close-on-click-overlay="false">
      <el-form :model="createForm" label-position="top" class="mcp-form">
        <el-form-item label="Key Name">
          <el-input v-model="createForm.name" placeholder="e.g., Production Environment Key" />
        </el-form-item>

        <el-form-item v-if="createForm.scope === 'user'" label="Select User" required>
          <el-select
            v-model="createForm.customer_id"
            placeholder="Search user email or name"
            filterable
            remote
            :remote-method="searchCustomerList"
            :loading="customerLoading"
            style="width: 100%"
          >
            <el-option
              v-for="c in customerList"
              :key="c.id"
              :value="c.id"
              :label="`${c.email} (${c.name || c.id})`"
            />
          </el-select>
        </el-form-item>

        <div class="form-section-title">
          <span class="section-label required-label">Translation Configuration</span>
        </div>

        <el-form-item label="API URL" :required="createForm.scope === 'admin'">
          <el-input v-model="createForm.config.api_url" placeholder="https://api.openai.com/v1" />
        </el-form-item>
        <el-form-item label="API Key" :required="createForm.scope === 'admin'">
          <el-input v-model="createForm.config.api_key" placeholder="sk-xxxx" show-password />
        </el-form-item>
        <el-form-item label="Model Name" :required="createForm.scope === 'admin'">
          <el-input v-model="createForm.config.model" placeholder="gpt-4o" />
        </el-form-item>
        <el-form-item label="Translation Format">
          <el-cascader v-model="createForm.config.type" :options="typeOptions" :props="{ expandTrigger: 'hover', emitPath: false }" placeholder="Select translation format" style="width: 100%" clearable />
        </el-form-item>
        <el-form-item label="Target Language">
          <el-select v-model="createForm.config.lang" placeholder="Please select target language" style="width: 100%">
            <el-option v-for="lang in languageOptions" :key="lang.value" :label="lang.label" :value="lang.value" />
          </el-select>
        </el-form-item>

        <div class="form-section-title">
          <span class="section-label optional-label">Optional Configuration</span>
        </div>

        <el-form-item label="Backup Model">
          <el-input v-model="createForm.config.backup_model" placeholder="Backup model automatically switches when primary model is unavailable" />
        </el-form-item>
        <el-form-item label="Concurrent Thread Count">
          <el-input-number v-model="createForm.config.threads" :min="1" :max="20" />
        </el-form-item>
        <el-form-item label="Glossary ID">
          <el-input-number v-model="createForm.config.comparison_id" :min="0" />
        </el-form-item>
        <el-form-item label="Prompt Template">
          <el-select
            v-model="createForm.config.prompt_id"
            placeholder="Please select prompt template"
            :loading="promptLoading"
            style="width: 100%"
          >
            <el-option
              v-for="p in promptList"
              :key="p.id"
              :label="`${p.title}${p.content ? ' - ' + (p.content.length > 30 ? p.content.substring(0, 30) + '...' : p.content) : ''}`"
              :value="p.id"
            />
          </el-select>
          <div v-if="createForm.config.prompt_id !== 0 && getSelectedPromptContent(createForm.config.prompt_id)" class="prompt-preview">
            <div class="prompt-preview-label">Prompt Content:</div>
            <div class="prompt-preview-content">{{ getSelectedPromptContent(createForm.config.prompt_id) }}</div>
          </div>
          <!-- <div v-else-if="createForm.config.prompt_id === 0" class="prompt-preview">
            <div class="prompt-preview-label">Prompt Content:</div>
            <div class="prompt-preview-content" style="color: #94a3b8;">Use system built-in default prompt</div>
          </div> -->
        </el-form-item>
        <el-form-item label="Doc2X">
          <el-radio-group v-model="createForm.config.doc2x_flag">
            <el-radio-button value="N">Disable</el-radio-button>
            <el-radio-button value="Y">Enable</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="createForm.config.doc2x_flag === 'Y'" label="Doc2X Key">
          <el-input v-model="createForm.config.doc2x_secret_key" placeholder="Enter Doc2X API Key" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible = false">Cancel</el-button>
        <el-button type="primary" @click="handleCreate" :loading="createLoading">Create Key</el-button>
      </template>
    </ResponsiveModal>

    <!-- Edit key dialog -->
    <ResponsiveModal v-model="editVisible" title="Edit Key" width="560px" :close-on-click-overlay="false">
      <el-form :model="editForm" label-position="top" class="mcp-form">
        <el-form-item label="Key Name">
          <el-input v-model="editForm.name" placeholder="Key Name" />
        </el-form-item>
        <el-form-item v-if="editForm.customer_email && editForm.scope === 'user'" label="Belongs to User">
          <el-input :model-value="editForm.customer_email" disabled />
        </el-form-item>

        <div class="form-section-title">
          <span class="section-label required-label">Translation Configuration</span>
        </div>

        <el-form-item label="API 地址">
          <el-input v-model="editForm.config.api_url" placeholder="https://api.ezworkapi.top/v1" />
        </el-form-item>
        <el-form-item label="API Key">
          <el-input v-model="editForm.config.api_key" placeholder="sk-xxxx" show-password />
        </el-form-item>
        <el-form-item label="模型名称">
          <el-input v-model="editForm.config.model" placeholder="gpt-4o" />
        </el-form-item>
        <el-form-item label="译文形式">
          <el-cascader v-model="editForm.config.type" :options="typeOptions" :props="{ expandTrigger: 'hover', emitPath: false }" placeholder="选择译文形式" style="width: 100%" clearable />
        </el-form-item>
        <el-form-item label="目标语言">
          <el-select v-model="editForm.config.lang" placeholder="请选择目标语言" style="width: 100%">
            <el-option v-for="lang in languageOptions" :key="lang.value" :label="lang.label" :value="lang.value" />
          </el-select>
        </el-form-item>

        <div class="form-section-title">
          <span class="section-label optional-label">Optional Configuration</span>
        </div>

        <el-form-item label="Backup Model">
          <el-input v-model="editForm.config.backup_model" placeholder="Backup Model" />
        </el-form-item>
        <el-form-item label="并发Thread Count">
          <el-input-number v-model="editForm.config.threads" :min="1" :max="20" />
        </el-form-item>
        <el-form-item label="术语库 ID">
          <el-input-number v-model="editForm.config.comparison_id" :min="0" />
        </el-form-item>
        <el-form-item label="提示词模板">
          <el-select
            v-model="editForm.config.prompt_id"
            placeholder="请Select Prompt模板"
            :loading="promptLoading"
            style="width: 100%"
          >
            <el-option
              v-for="p in promptList"
              :key="p.id"
              :label="`${p.title}${p.content ? ' - ' + (p.content.length > 30 ? p.content.substring(0, 30) + '...' : p.content) : ''}`"
              :value="p.id"
            />
          </el-select>
          <div v-if="editForm.config.prompt_id>=0 && getSelectedPromptContent(editForm.config.prompt_id)" class="prompt-preview">
            <div class="prompt-preview-label">Prompt Content:</div>
            <div class="prompt-preview-content">{{ getSelectedPromptContent(editForm.config.prompt_id) }}</div>
          </div>
          <div v-else class="prompt-preview">
            <div class="prompt-preview-label">Prompt Content:</div>
            <div class="prompt-preview-content" style="color: #94a3b8;">Use system built-in default prompt</div>
          </div>
        </el-form-item>
        <el-form-item label="Doc2X">
          <el-radio-group v-model="editForm.config.doc2x_flag">
            <el-radio-button value="N">禁用</el-radio-button>
            <el-radio-button value="Y">启用</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="editForm.config.doc2x_flag === 'Y'" label="Doc2X Key">
          <el-input v-model="editForm.config.doc2x_secret_key" placeholder="输入 Doc2X API Key" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">Cancel</el-button>
        <el-button type="primary" @click="handleEdit" :loading="editLoading">Save</el-button>
      </template>
    </ResponsiveModal>

    <!-- New key display dialog -->
    <ResponsiveModal v-model="newKeyVisible" title="Key Created" width="460px" :close-on-click-overlay="false" :show-close="false">
      <div class="new-key-display">
        <div class="new-key-icon">🎉</div>
        <p class="new-key-title">Key created successfully</p>
        <div class="new-key-warning">⚠️ This key will only be displayed once and cannot be viewed again after closing</div>
        <div class="key-display-box">
          <span class="key-value">{{ newKeyValue }}</span>
          <el-button type="primary" text :icon="CopyDocument" @click="copyText(newKeyValue)" class="copy-key-btn">Copy</el-button>
        </div>
      </div>
      <template #footer>
        <el-button type="primary" @click="newKeyVisible = false" class="confirm-saved-btn">I have securely saved it</el-button>
      </template>
    </ResponsiveModal>
  </div>
</template>

<style scoped>
.mcp-page {
  /* max-width: 960px; */
  margin: 0 auto;
}

.mcp-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;

  .mcp-header-left {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .mcp-title {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
    color: #1e293b;
  }

  .mcp-header-right {
    display: flex;
    gap: 8px;
  }
}

.mcp-tabs {
  :deep(.el-tabs__header) {
    margin-bottom: 16px;
  }
}

.tab-info {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: 16px;
  padding: 10px 14px;
  background: #f8fafc;
  border-radius: 8px;
  font-size: 13px;
  color: #64748b;
}

.key-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mcp-key-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  transition: box-shadow 0.2s;

  &:hover {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  }

  .key-meta {
    display: flex;
    flex-direction: column;
    gap: 6px;
    flex: 1;
    min-width: 0;
  }

  .key-name {
    font-size: 15px;
    font-weight: 600;
    color: #1e293b;
  }

  .key-info {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;

    .key-prefix code {
      font-family: 'SF Mono', 'Fira Code', monospace;
      font-size: 12px;
      color: #475569;
      background: #f1f5f9;
      padding: 2px 8px;
      border-radius: 4px;
    }

    .key-detail {
      font-size: 12px;
      color: #64748b;
    }
  }

  .key-time {
    font-size: 12px;
    color: #94a3b8;
  }

  .key-actions {
    display: flex;
    gap: 4px;
    flex-shrink: 0;
  }
}

.no-keys {
  text-align: center;
  padding: 48px 20px;
  background: #f8fafc;
  border-radius: 12px;
  border: 2px dashed #e2e8f0;

  .empty-visual {
    font-size: 40px;
    margin-bottom: 16px;
  }

  .empty-title {
    font-size: 16px;
    font-weight: 500;
    color: #475569;
    margin: 0 0 6px;
  }

  .empty-desc {
    font-size: 13px;
    color: #94a3b8;
    margin: 0;
  }
}

.form-section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #334155;
  margin: 16px 0 10px;
  padding-bottom: 6px;
  border-bottom: 1px solid #f1f5f9;

  .section-label {
    display: flex;
    align-items: center;
    gap: 6px;

    &::before {
      content: '';
      width: 8px;
      height: 8px;
      border-radius: 50%;
    }

    &.required-label::before {
      background: #3b82f6;
    }

    &.optional-label::before {
      background: #94a3b8;
    }
  }
}

.mcp-form {
  .el-form-item {
    margin-bottom: 14px;
  }
}

.prompt-preview {
  margin-top: 8px;
  padding: 10px 14px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  max-height: 120px;
  overflow-y: auto;

  .prompt-preview-label {
    font-size: 12px;
    color: #94a3b8;
    margin-bottom: 6px;
  }

  .prompt-preview-content {
    font-size: 13px;
    color: #475569;
    line-height: 1.6;
    white-space: pre-wrap;
    word-break: break-all;
  }
}

.new-key-display {
  text-align: center;
  padding: 4px 0;

  .new-key-icon {
    font-size: 48px;
    margin-bottom: 12px;
  }

  .new-key-title {
    font-size: 20px;
    font-weight: 700;
    color: #1e293b;
    margin: 0 0 16px;
  }

  .new-key-warning {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #fdf6ec;
    border: 1px solid #faecd8;
    color: #e6a23c;
    padding: 8px 16px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 500;
    margin-bottom: 20px;
  }

  .key-display-box {
    display: flex;
    align-items: center;
    gap: 10px;
    background: #f1f5f9;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 12px 16px;

    .key-value {
      flex: 1;
      font-family: 'SF Mono', 'Fira Code', monospace;
      font-size: 13px;
      color: #334155;
      word-break: break-all;
      text-align: left;
      line-height: 1.5;
    }

    .copy-key-btn {
      flex-shrink: 0;
    }
  }
}

.confirm-saved-btn {
  width: 100%;
  height: 40px;
  border-radius: 8px;
  font-weight: 500;
}

@media screen and (max-width: 768px) {
  .mcp-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;

    .mcp-header-right {
      width: 100%;
      flex-direction: column;
    }
  }

  .mcp-key-card {
    flex-direction: column;
    gap: 12px;
    padding: 14px;

    .key-info {
      flex-direction: column;
      align-items: flex-start;
      gap: 6px;
    }

    .key-actions {
      width: 100%;
      justify-content: flex-end;
    }
  }
}
</style>
