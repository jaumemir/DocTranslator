/** Mock API response data */
const SELECT_RESPONSE_DATA = {
  code: 0,
  data: [
    {
      label: "Apple",
      value: 1
    },
    {
      label: "Banana",
      value: 2
    },
    {
      label: "Orange",
      value: 3,
      disabled: true
    }
  ],
  message: "Select data retrieved successfully"
}

/** Mock API */
export function getSelectDataApi() {
  return new Promise<typeof SELECT_RESPONSE_DATA>((resolve, reject) => {
    // Mock API response time 2s
    setTimeout(() => {
      // Mock successful API call
      if (Math.random() < 0.8) {
        resolve(SELECT_RESPONSE_DATA)
      } else {
        // Mock API error
        reject(new Error("API error occurred"))
      }
    }, 2000)
  })
}
