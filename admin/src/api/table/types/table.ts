export interface CreateOrUpdateTableRequestData {
  id?: string
  username: string
  password?: string
}

export interface GetTableRequestData {
  /** Current page number */
  currentPage: number
  /** Query limit */
  size: number
  /** Query parameter: username */
  username?: string
  /** Query parameter: phone number */
  phone?: string
}

export interface GetTableData {
  createTime: string
  email: string
  id: string
  phone: string
  roles: string
  status: boolean
  username: string
}

export type GetTableResponseData = ApiResponseData<{
  list: GetTableData[]
  total: number
}>
