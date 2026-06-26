export interface LoginRequestData {
  /** admin or editor */
  email: string,
  /** Password */
  password: string
  /** Verification code */
  // code: string
}

export type LoginCodeResponseData = ApiResponseData<string>

export type LoginResponseData = ApiResponseData<{ token: string }>

export type UserInfoResponseData = ApiResponseData<{ username: string; roles: string[] }>
