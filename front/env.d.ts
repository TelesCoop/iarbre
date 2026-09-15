/// <reference types="vite/client" />

interface TarteaucitronService {
  key: string
  type: string
  name: string
  needConsent?: boolean
  cookies?: string[]
  js: () => void
  fallback?: () => void
}

interface Tarteaucitron {
  init: (params: Record<string, unknown>) => void
  services: Record<string, TarteaucitronService>
  job: string[]
  userInterface: {
    openPanel: () => void
  }
}

interface Window {
  tarteaucitron: Tarteaucitron
}
