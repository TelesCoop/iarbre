import { beforeEach, describe, expect, test, vi } from "vitest"
import { createPinia, setActivePinia } from "pinia"

const fetchDashboard = vi.fn()
const fetchDashboardForZone = vi.fn()

vi.mock("@/services/dashboardService", () => ({
  fetchDashboard: (...args: unknown[]) => fetchDashboard(...args),
  fetchDashboardForZone: (...args: unknown[]) => fetchDashboardForZone(...args)
}))

import { useDashboardStore } from "@/stores/dashboard"
import { useZoneStore, type ZonePolygon } from "@/stores/zone"

const POLYGON: ZonePolygon = {
  type: "Polygon",
  coordinates: [
    [
      [4.86, 45.8],
      [4.87, 45.8],
      [4.87, 45.81],
      [4.86, 45.8]
    ]
  ]
}

describe("dashboard store — zone scale", () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    fetchDashboard.mockReset().mockResolvedValue({ data: { areaKm2: 1 }, error: null })
    fetchDashboardForZone.mockReset().mockResolvedValue({ data: { areaKm2: 5 }, error: null })
  })

  test("hasZone reflects the zone store", () => {
    const store = useDashboardStore()
    expect(store.hasZone).toBe(false)
    useZoneStore().setZone(POLYGON)
    expect(store.hasZone).toBe(true)
  })

  test("zone scale calls the polygon service with the geometry", async () => {
    useZoneStore().setZone(POLYGON)
    const store = useDashboardStore()
    store.setScale("zone")
    await vi.waitFor(() => expect(store.dashboardData).toEqual({ areaKm2: 5 }))
    expect(fetchDashboardForZone).toHaveBeenCalledWith(POLYGON)
    expect(fetchDashboard).not.toHaveBeenCalled()
  })

  test("zone scale without a geometry surfaces an error", async () => {
    const store = useDashboardStore()
    store.setScale("zone")
    await vi.waitFor(() => expect(store.error).not.toBeNull())
    expect(fetchDashboardForZone).not.toHaveBeenCalled()
  })
})
