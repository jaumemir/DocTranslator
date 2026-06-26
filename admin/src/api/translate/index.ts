import { request } from "@/utils/service"
import type * as Translate from "./types/translate"

/** List */
export function getTranslateDataApi(params: Translate.GetTranslateRequestData) {
  return request<Translate.GetTranslateResponseData>({
    url: `translates`,
    method: "get",
    params
  })
}

export function deleteTranslateDataApi(id: number) {
  return request<Translate.TranslateNoResponseData>({
    url: `/translate/${id}`,
    method: "delete"
  })
}

export function deleteMoreTranslateDataApi(data: object) {
  return request<Translate.TranslateNoResponseData>({
    url: `/translates/delete/batch`,
    method: "post",
    data
  })
}
// Batch download
export function downloadMoreTranslateDataApi(data: object) {
  return request<Translate.TranslateNoResponseData>({
    url: `/translates/download/batch`,
    method: "post",
    data
  })
}
