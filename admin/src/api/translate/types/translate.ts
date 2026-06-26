export interface GetTranslateRequestData {
  /** Current page number */
  page: number
  /** Query limit */
  limit: number
  /** Keyword */
  keyword?: string
}

export interface GetTranslateData {
  id: number
  translate_no: string
  created_at: string
  origin_filename: string
  origin_filepath: string
  target_filepath: string
  start_at: string
  end_at: string
  status: boolean
}

export type GetTranslateResponseData = ApiResponseData<{
  data: GetTranslateData[]
  total: number
}>

export type TranslateNoResponseData=ApiResponseData<[]>