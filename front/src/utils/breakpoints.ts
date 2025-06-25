/**
 * Breakpoints are defined in rem units.
 * By default, 1rem = 16px.
 * But it can be changed in the CSS.
 */
export enum Breakpoint {
  SM = 48,
  MD = 64,
  LG = 80,
  XL = 96,
  XXL = 120
}

export const convertRemToPx = (rem: number) => {
  const rootFontSize = parseFloat(getComputedStyle(document.documentElement).fontSize)
  return rem * rootFontSize
}
