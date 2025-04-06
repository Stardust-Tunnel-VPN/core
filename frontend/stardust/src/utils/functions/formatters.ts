// src/utils/formatters.ts

/**
 * Formats speed from bits/sec to Mb/sec with two decimal places.
 * If the result is not valid, returns an empty string.
 * @param speed - speed value (number or string)
 * @returns formatted speed with units or empty string
 */
export function formatSpeed(speed: string | number): string {
  if (speed === undefined || speed === null) return ''
  const speedNum = Number(speed)
  if (isNaN(speedNum)) return ''
  const mbSec = (speedNum / 1e6).toFixed(2)
  return `${mbSec} Mb/sec`
}

/**
 * Formats ping value by adding "ms".
 * If the result is not valid, returns an empty string.
 * @param ping - ping value (number or string)
 * @returns formatted ping value with units or empty string
 */
export function formatPing(ping: string | number): string {
  if (ping === undefined || ping === null) return ''
  const pingNum = Number(ping)
  if (isNaN(pingNum)) return ''
  return `${pingNum} ms`
}

/**
 * Formats uptime value by converting seconds into days, hours, and minutes.
 * If the result is not valid, returns an empty string.
 * @param uptime - uptime value (number or string)
 * @returns formatted uptime value or empty string
 */
export function formatUptime(uptime: string | number): string {
  if (uptime === undefined || uptime === null) return ''
  const uptimeNum = Number(uptime)
  if (isNaN(uptimeNum)) return ''
  const days = Math.floor(uptimeNum / 86400)
  const hours = Math.floor((uptimeNum % 86400) / 3600)
  const minutes = Math.floor((uptimeNum % 3600) / 60)
  return `${days}d ${hours}h ${minutes}m`
}
