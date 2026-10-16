import { ref } from "vue"
import { useApiPost } from "@/api"

export const fetchShortLink = async (): Promise<string> => {
  const { data } = await useApiPost<{ code: string }>("short-links/", {
    path: window.location.pathname + window.location.search
  })
  return data ? `${window.location.origin}/s/${data.code}` : window.location.href
}

export const useCopyLink = () => {
  const isCopied = ref(false)

  const copyLink = async (url: string | Promise<string>) => {
    await navigator.clipboard.write([
      new ClipboardItem({
        "text/plain": Promise.resolve(url).then(
          (value) => new Blob([value], { type: "text/plain" })
        )
      })
    ])
    isCopied.value = true
    setTimeout(() => {
      isCopied.value = false
    }, 2000)
  }

  return { isCopied, copyLink }
}
