import axios, { type AxiosInstance, type AxiosRequestConfig } from "axios"
import { useUserStoreHook } from "@/store/modules/user"
import { ElMessage } from "element-plus"
import { get, merge } from "lodash-es"
import { getToken } from "./cache/cookies"

/** Logout and force refresh page (will redirect to login page) */
function logout() {
  useUserStoreHook().logout()
  location.reload()
}

/** Create request instance */
function createService() {
  // Create an axios instance named service
  const service = axios.create({
    timeout: 10000,
    baseURL: "/api"
  })
  // Request interceptor
  service.interceptors.request.use(
    (config) => config,
    // Send failure
    (error) => Promise.reject(error)
  )
  // Response interceptor (can be adjusted according to specific business needs)
  service.interceptors.response.use(
    (response) => {
      // apiData is the data returned by the API
      const apiData = response.data
      // Binary data is returned directly
      const responseType = response.request?.responseType
      if (responseType === "blob" || responseType === "arraybuffer") return apiData
      // This code is the business code agreed with the backend
      const code = apiData.code
      // If there is no code, it means this is not an API developed by the project backend
      if (code === undefined) {
        ElMessage.error("Not a system API")
        return Promise.reject(new Error("Not a system API"))
      }
      switch (code) {
        case 200:
          // This system uses code === 0 to indicate no business error
          return apiData
        case 401:
          // When token expires
          return logout()
        default:
          // return apiData
          // Not a valid code
          ElMessage.error(apiData.message || "Error")
          return Promise.reject(new Error("Error"))
      }
    },
    (error) => {
      // status is HTTP status code
      const status = get(error, "response.status")
      switch (status) {
        case 400:
          error.message = "Bad Request"
          break
        case 401:
          // When token expires
          logout()
          break
        case 403:
          error.message = "Access Denied"
          break
        case 404:
          error.message = "Request URL Error"
          break
        case 408:
          error.message = "Request Timeout"
          break
        case 500:
          error.message = "Internal Server Error"
          break
        case 501:
          error.message = "Service Not Implemented"
          break
        case 502:
          error.message = "Gateway Error"
          break
        case 503:
          error.message = "Service Unavailable"
          break
        case 504:
          error.message = "Gateway Timeout"
          break
        case 505:
          error.message = "HTTP Version Not Supported"
          break
        default:
          break
      }
      ElMessage.error(error.message)
      return Promise.reject(error)
    }
  )
  return service
}
const globalApi = window.ipConfig
console.log(globalApi)
/** Create request method */
function createRequest(service: AxiosInstance) {
  return function <T>(config: AxiosRequestConfig): Promise<T> {
    const token = getToken()
    const defaultConfig = {
      headers: {
        // Carry Token
        // Authorization: token ? `Bearer ${token}` : undefined,
        Token: token ? token : undefined,
        "Content-Type": "application/json"
      },
      timeout: 10000,
      // Local development environment, API configuration modifies .env.development, production environment reads dynamic variables
      // baseURL: "/api",
      baseURL: (import.meta.env.MODE != "production" ? import.meta.env.VITE_BASE_API : globalApi) + "/api/admin",
      data: {}
    }
    // Merge default config defaultConfig and passed custom config into mergeConfig
    const mergeConfig = merge(defaultConfig, config)
    return service(mergeConfig)
  }
}

/** Instance for network requests */
const service = createService()
/** Method for network requests */
export const request = createRequest(service)
