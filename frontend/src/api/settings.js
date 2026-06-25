import request from '@/utils/request'
/**
 * Get environment configuration information
 */
// Version information
export function getVersionSetting() {
  return request({
    url: '/api/common/version',
    method: 'GET',
  });
}
// Get system settings
export function getSystemSetting() {
  return request({
    url: '/api/common/all_settings',
    method: 'GET',
  });
}
/**
 * Get translation settings
 */
export function getTranslateSetting() {
  return request({
    url: '/api/translate/setting',
    method: 'get',
  });
}