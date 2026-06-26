import { ref } from "vue"

export function useFocus() {
  /** Whether has focus */
  const isFocus = ref<boolean>(false)

  /** Lose focus */
  const handleBlur = () => {
    isFocus.value = false
  }
  /** Get focus */
  const handleFocus = () => {
    isFocus.value = true
  }

  return { isFocus, handleBlur, handleFocus }
}
