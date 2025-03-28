export const copyToClipboard = (value: string) => {
  if (navigator.clipboard) navigator.clipboard.writeText(value)
}
