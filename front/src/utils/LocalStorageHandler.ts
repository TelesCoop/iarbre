import type { LocalStorageValues, LocalStorageKeys } from "@/types/LocalStorageTypes"

export class LocalStorageHandler {
  static getItem<K extends LocalStorageKeys>(key: K): LocalStorageValues[K] | null {
    try {
      const item = localStorage.getItem(key)
      return item ? (JSON.parse(item) as LocalStorageValues[K]) : null
    } catch (error) {
      console.error(`Error retrieving item from localStorage: ${error}`)
      return null
    }
  }

  static setItem<K extends LocalStorageKeys>(key: K, value: LocalStorageValues[K]): void {
    try {
      const item = JSON.stringify(value)
      localStorage.setItem(key, item)
    } catch (error) {
      console.error(`Error setting item in localStorage: ${error}`)
    }
  }

  static removeItem(key: LocalStorageKeys): void {
    localStorage.removeItem(key)
  }

  static clear(): void {
    localStorage.clear()
  }
}
