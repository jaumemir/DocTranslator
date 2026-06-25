import request from '@/utils/request'

// Terminology - Square list
export function comparison_share(params) {
  return request({
      url: `/api/comparison/share`,
      method: 'get',
      params: params
  });
}

// Prompt - Square list
export function prompt_share(params) {
  return request({
      url: `/api/prompt/share`,
      method: 'get',
      params: params
  });
}

// Add to my terminology
export function comparison_copy(id){
  return request({
      url: `/api/comparison/copy/${id}`,
      method: 'POST'
  });
}

// Add to my prompts
export function prompt_copy(id){
  return request({
      url: `/api/prompt/copy/${id}`,
      method: 'POST'
  });
}

// Favorite terminology
export function comparison_fav(id){
  return request({
      url: `/api/comparison/fav/${id}`,
      method: 'POST'
  });
}

// Favorite prompt
export function prompt_fav(id){
  return request({
      url: `/api/prompt/fav/${id}`,
      method: 'POST'
  });
}