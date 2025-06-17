import sharedConfig from "@/../../shared/config.json"

interface SharedConfig {
  metaFactorsMapping: Record<string, string[]>
  localClimateZones: Record<string, string>
}

export const SHARED_CONFIG = sharedConfig as SharedConfig

export const META_FACTORS_MAPPING = SHARED_CONFIG.metaFactorsMapping
export const LOCAL_CLIMATE_ZONES = SHARED_CONFIG.localClimateZones
