import { request } from "@/utils/service"
import type * as Table from "./types/table"

/** Create */
export function createTableDataApi(data: Table.CreateOrUpdateTableRequestData) {
  return request({
    url: "table",
    method: "post",
    data
  })
}

/** Delete */
export function deleteTableDataApi(id: string) {
  return request({
    url: `table/${id}`,
    method: "delete"
  })
}

/** Update */
export function updateTableDataApi(data: Table.CreateOrUpdateTableRequestData) {
  return request({
    url: "table",
    method: "put",
    data
  })
}

/** Query */
export function getTableDataApi(params: Table.GetTableRequestData) {
  return request<Table.GetTableResponseData>({
    url: "table",
    method: "get",
    params
  })
}
