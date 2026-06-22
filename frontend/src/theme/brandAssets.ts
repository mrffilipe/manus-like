/** Brand assets served from `frontend/public/brand/` (see docs/Brand guideline/). */
export const brandAssets = {
  logoLight: '/brand/kyvo-logo-light.png',
  logoDark: '/brand/kyvo-logo-dark.png',
  icon: '/brand/kyvo-icon.png',
} as const

export function brandLogoSrc(mode: 'light' | 'dark'): string {
  return mode === 'dark' ? brandAssets.logoDark : brandAssets.logoLight
}
