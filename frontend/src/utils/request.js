import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import router from '@/router'
import { useUserStore } from '@/store/user'
import Qs from 'qs'
// import router from '@/router'
// import i18n from '@/lang/index' // i18n 国际化

// Create an axios instance
const service = axios.create({
  baseURL: '/api', //  import.meta.env.VITE_API_URL   url = base url + request url
  withCredentials: true, // Send cookies when cross-domain requests
  crossDomain: true,
  timeout: 30000, // Request timeout
  transformRequest: [function(data) {
    if (data instanceof FormData) {
      return data
    } else {
      data = Qs.stringify(data, { arrayFormat: 'indices' })
      return data
    }
  }],
  paramsSerializer: (params) => {
    for (const param in params) {
      if (params[param] === '' || params[param] == null) {
        delete params[param]
      }
    }
    return Qs.stringify(params)
  }
})

// request interceptor
service.interceptors.request.use(
  config => {
    const userStore = useUserStore()
    config.headers['token'] = userStore.token;
    config.headers['credentials']='include'
    config.headers['withCredentials']=true  // Carry credentials (like Cookies)
      // config.headers['language'] = localStorage.getItem('language')||'zh';
      return config
  },
  error => {
    // do something with request error
    console.log(error) // for debug
    return Promise.reject(error)
  }
)

// response interceptor
service.interceptors.response.use(
  response => {
    const res = response.data
    // if (res?.code === 401) {
    //   router.push('/login')
    //   return Promise.reject(new Error('Unauthorized'))
    // }
    return res
  },
  error => {
    const { response } = error
    if (response) {
      switch (response.status) {
        case 401:
          ElMessage.error('Session expired, please login again')
          router.push('/login')
          break
        case 422:
          ElMessage.error('Session expired, please login again')
          router.push('/login')
          break
        case 403:
          ElMessage.error('User status abnormal or insufficient permissions!')
          break
        default:
          ElMessage.error('Request failed')
      }
    } else {
      ElMessage.error('Network connection error')
    }
    return Promise.reject(error)
  }
)
// service.interceptors.response.use(
//   response => {

//     const res = response.data
  
//       return res
//   },
//   error => {
//     const { response } = error
//      if (response.code == 401) {
//       console.log(401);
//       router.push('/login')
// }
//     console.log('err' + error)
//     ElMessageBox({
//       message: error.message,
//       type: 'error',
//       duration: 5 * 1000
//     })
//     return Promise.reject(error)
//   }
// )

export default service

