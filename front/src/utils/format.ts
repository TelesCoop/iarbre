export const capitalize = (str: string) => str.charAt(0).toUpperCase() + str.slice(1)

export const formatNumber = (value: number, digits = 1) =>
  value.toLocaleString("fr-FR", { minimumFractionDigits: digits, maximumFractionDigits: digits })

export const formatSurface = (m2: number) =>
  m2 >= 1_000_000
    ? `${(m2 / 1_000_000).toLocaleString("fr-FR", { maximumFractionDigits: 2 })} km²`
    : `${Math.round(m2).toLocaleString("fr-FR")} m²`
