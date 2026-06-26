export interface CreateOrUpdateCustomerRequestData {
  id?: number
  email: string
  password?: string
  level: string
  add_storage: number
  storage: number
  // status: boolean
}

export interface GetCustomerRequestData {
  /** Current page number */
  page: number
  /** Query limit */
  limit: number
  /** Keyword */
  keyword?: string
}

export interface GetCustomerData {
  id: number
  created_at: string
  email: string
  level: string
  status: boolean
}

export type GetCustomerResponseData = ApiResponseData<{
  data: GetCustomerData[]
  total: number
}>

export interface RegisterData {
  email: string
  password?: string
  level: string
}
