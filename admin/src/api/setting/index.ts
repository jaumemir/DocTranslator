import { request } from "@/utils/service"
import type * as Setting from "./types/setting"


/** List */
export function getApiSettingData() {
  return request<Setting.GetApiSettingResponseData>({
    url: `setting/api`,
    method: "get",
  })
}

/** Settings */
export function setApiSettingData(data:Setting.ApiSetting) {
  return request<Setting.SettingNoResponseData>({
    url: `setting/api`,
    method: "post",
    data
  })
}

/** List */
export function getOtherSettingData() {
  return request<Setting.GetOtherSettingResponseData>({
    url: `setting/other`,
    method: "get",
  })
}

/** Settings */
export function setOtherSettingData(data:Setting.OtherSetting) {
  return request<Setting.SettingNoResponseData>({
    url: `setting/other`,
    method: "post",
    data
  })
}

/** List */
export function getSiteSettingData() {
  return request<Setting.GetSiteSettingResponseData>({
    url: `setting/site`,
    method: "get",
  })
}

/** Settings */
export function setSiteSettingData(data:Setting.SiteSetting) {
  return request<Setting.SettingNoResponseData>({
    url: `setting/site`,
    method: "post",
    data
  })
}

