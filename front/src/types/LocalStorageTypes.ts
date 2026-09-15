import type { HeightRange } from "@/utils/vegetation"

export type UserSettings = { name: string }

export type LocalStorageValues = {
  hasVisitedBefore: boolean
  vegestrateHeightRanges: HeightRange[]
}

export type LocalStorageKeys = keyof LocalStorageValues
