export const PET_YEARS = [2020, 2090] as const

export type PetYear = (typeof PET_YEARS)[number]

export const DEFAULT_PET_YEAR: PetYear = 2090

export const PET_HOURS = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21] as const

export type PetHour = (typeof PET_HOURS)[number]

export const DEFAULT_PET_HOUR: PetHour = 16

export const buildPetTileUrl = (baseApiUrl: string, year: PetYear, hour: PetHour): string =>
  `${baseApiUrl}/tiles/pet/{z}/{x}/{y}.png?year=${year}&hour=${hour}`
