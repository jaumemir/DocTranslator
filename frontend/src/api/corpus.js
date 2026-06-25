import request from '@/utils/request'

// Terminology - Add comparison data
export function comparison(params) {
  return request({
      url: `/api/comparison`,
      method: 'POST',
      data: params
  });
}

// Edit comparison data
export function comparison_edit(id,params){
  return request({
      url: `/api/comparison/${id}`,
      method: 'POST',
      data:params
  });
}

// Delete comparison data
export function comparison_del(id){
  return request({
      url: `/api/comparison/${id}`,
      method: 'delete'
  });
}


/**
 * Get terminology list
 */
export function comparison_my(){
  return request({
      url: '/api/comparison/my',
      method: 'get',
  });
}


// Update share status
export function comparison_share(id,params){
  return request({
      url: `/api/comparison/share/${id}`,
      method: 'POST',
      data:params
  });
}

/**
 * Get prompts
 */
export function prompt_my(){
  return request({
      url: '/api/prompt/my',
      method: 'get',
  });
}

// Add prompt
export function prompt_add(params) {
  return request({
      url: `/api/prompt`,
      method: 'POST',
      data: params
  });
}

// Edit prompt
export function prompt_edit(id,params){
  return request({
      url: `/api/prompt/${id}`,
      method: 'POST',
      data:params
  });
}

// Update prompt share status
export function prompt_share(id,params){
  return request({
      url: `/api/prompt/share/${id}`,
      method: 'POST',
      data:params
  });
}


// Delete prompt
export function prompt_del(id){
  return request({
      url: `/api/prompt/${id}`,
      method: 'delete'
  });
}