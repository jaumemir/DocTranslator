/** Mock API response data */
const SUCCESS_RESPONSE_DATA = {
  code: 0,
  data: {
    list: [] as number[]
  },
  message: "Retrieved successfully"
}

/** Mock successful API request */
export function getSuccessApi(list: number[]) {
  return new Promise<typeof SUCCESS_RESPONSE_DATA>((resolve) => {
    setTimeout(() => {
      resolve({ ...SUCCESS_RESPONSE_DATA, data: { list } })
    }, 1000)
  })
}

/** Mock failed API request */
export function getErrorApi() {
  return new Promise((_resolve, reject) => {
    setTimeout(() => {
      reject(new Error("Error occurred"))
    }, 1000)
  })
}
