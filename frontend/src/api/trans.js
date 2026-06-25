import request from '@/utils/request'

// Check if available
export function checkOpenAI(params) {
    return request({
        url: `/api/check/openai`,
        method: 'POST',
        data: params
    });
}

// Check if available
export function checkDocx(params) {
    return request({
        url: `/api/check/doc2x`,
        method: 'POST',
        data: params
    });
}

// Check if PDF is scanned
export function checkPdf(file_path) {
    return request({
        url: `/api/check/pdf`,
        method: 'POST',
        data: { file_path }
    });
}

export function delFile(data) {
    return request({
        url: `/api/delFile`,
        method: 'POST',
        data: data
    });
}


export function transalteFile(params) {
    return request({
        url: `/api/translate`,
        method: 'POST',
        data: params
    });
}
// Query progress
export function transalteProcess(params) {
    return request({
        url: `/api/process`,
        method: 'POST',
        data: params
    });
}

/**
 * Translation
 */
export function translates(params) {
    return request({
        url: `/api/translates`,
        method: 'get',
        params
    });
}



export function delTranslate(id) {
    return request({
        url: `/api/translate/${id}`,
        method: 'delete'
    });
}

/**
 * Delete all translation file records
 */
export function delAllTranslate() {
    return request({
        url: '/api/translate/all',
        method: 'delete'
    });
}

/**
 * Download all translation file records
 */
export function downAllTranslate() {
    return request({
        url: '/api/translate/download/all',
        method: 'get'
    });
}


/**
 * Get file statistics
 */
export function getFinishCount() {
    return request({
        url: '/api/translate/finish/count',
        method: 'get'
    });
}

// doc2x start PDF translation
export function doc2xStartService(data) {
    return request({
        url: '/api/doc2x/start',
        method: 'post',
        data
    });
}

// doc2x query task status
export function doc2xQueryStatusService(data) {
    return request({
        url: '/api/doc2x/status',
        method: 'post',
        data: data
    });
}

