import { request } from "@/utils/service"
// Get system storage file list
export function getFileList() {
  return request({
    url: "system/storage",
    method: "get"
  })
}
// Delete file
export function deleteFile(data) {
  return request({
    url: "system/storage",
    method: "delete",
    data
  })
}
