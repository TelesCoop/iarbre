import { initMatomo } from "@certible/use-matomo"

const PROD_HOSTNAME = "carte.iarbre.fr"

function isAnalyticsEnabled() {
  if (window.location.hostname === PROD_HOSTNAME) {
    return true
  }
  return new URLSearchParams(window.location.search).has("debug-analytics")
}

export function setupAnalytics() {
  if (!isAnalyticsEnabled()) {
    return
  }

  const script = document.createElement("script")
  script.src = "/tarteaucitron/tarteaucitron.min.js"
  script.onload = () => {
    const matomo = initMatomo({
      host: "https://analytics.tlscp.fr",
      siteId: 4,
      trackRouter: true,
      requireConsent: true
    })

    window.tarteaucitron.services.matomoCustom = {
      key: "matomoCustom",
      type: "analytic",
      name: "Matomo",
      needConsent: true,
      cookies: [],
      js: () => matomo.ready.then(() => matomo.push(["setConsentGiven"])),
      fallback: () => matomo.ready.then(() => matomo.push(["forgetConsentGiven"]))
    }
    window.tarteaucitron.job = ["matomoCustom"]

    window.tarteaucitron.init({
      privacyUrl: "/mentions-legales",
      bodyPosition: "bottom",
      orientation: "middle",
      groupServices: false,
      mandatory: false,
      iconPosition: "BottomLeft"
    })
  }
  document.head.appendChild(script)
}
