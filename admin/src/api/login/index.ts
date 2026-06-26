import { request } from "@/utils/service"
import type * as Login from "./types/login"

/** Get login verification code */
export function getLoginCodeApi() {
  return request<Login.LoginCodeResponseData>({
    url: "login/code",
    method: "get"
  })
}

/** Login and return Token */
export function loginApi(data: Login.LoginRequestData) {
  return request<Login.LoginResponseData>({
    url: "/login",
    method: "post",
    data
  })
}

/** Get user details */
export function getUserInfoApi() {
  return request<Login.UserInfoResponseData>({
    url: "/auth/info",
    method: "get"
  })
}
// Change password
export function updatePasswordApi(data) {
  return request({
    url: "/changepwd",
    method: "post",
    data
  })
}
