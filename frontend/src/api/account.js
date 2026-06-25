import request from '@/utils/request'

// Change password
export function changePassword(data) {
    return request({
        url: '/api/change',
        method: 'POST',
        data
    });
}

/**
 * Get storage space
 */
export function storage() {
    return request({
        url: '/api/storage',
        method: 'GET',
    });
}

/**
 * Get logged-in user basic information
 */
export function authInfo() {
    return request({
        url: '/api/user-info',
        method: 'GET',
    });
}


