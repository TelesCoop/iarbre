import { describe, it, expect, vi, beforeEach, afterEach } from "vitest"
import { fetchShortLink, useCopyLink } from "@/composables/useShortLink"

const useApiPostMock = vi.hoisted(() => vi.fn())

vi.mock("@/api", () => ({ useApiPost: useApiPostMock }))

describe("fetchShortLink", () => {
  beforeEach(() => {
    useApiPostMock.mockReset()
    window.history.replaceState({}, "", "/plantability/14/45.75773/4.85377?filters=8,10")
  })

  it("stores the current path and returns the short url", async () => {
    useApiPostMock.mockResolvedValue({ data: { code: "r4Vd9x" } })

    await expect(fetchShortLink()).resolves.toBe(`${window.location.origin}/s/r4Vd9x`)
    expect(useApiPostMock).toHaveBeenCalledWith("short-links/", {
      path: "/plantability/14/45.75773/4.85377?filters=8,10"
    })
  })

  it("falls back to the full url when the short link cannot be created", async () => {
    useApiPostMock.mockResolvedValue({ data: undefined, error: new Error("boom") })

    await expect(fetchShortLink()).resolves.toBe(window.location.href)
  })
})

describe("useCopyLink", () => {
  const write = vi.fn()

  beforeEach(() => {
    vi.useFakeTimers()
    write.mockReset().mockResolvedValue(undefined)
    vi.stubGlobal("navigator", { clipboard: { write } })
    vi.stubGlobal(
      "ClipboardItem",
      class {
        constructor(public items: Record<string, Promise<Blob>>) {}
      }
    )
  })

  afterEach(() => {
    vi.useRealTimers()
    vi.unstubAllGlobals()
  })

  it("writes the url to the clipboard and flags it as copied for 2 seconds", async () => {
    const { isCopied, copyLink } = useCopyLink()

    await copyLink("https://carte.iarbre.fr/s/r4Vd9x")

    const [[item]] = write.mock.calls[0]
    await expect(item.items["text/plain"].then((blob: Blob) => blob.text())).resolves.toBe(
      "https://carte.iarbre.fr/s/r4Vd9x"
    )
    expect(isCopied.value).toBe(true)
    vi.advanceTimersByTime(2000)
    expect(isCopied.value).toBe(false)
  })
})
