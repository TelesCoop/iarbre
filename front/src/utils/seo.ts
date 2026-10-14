import type { RouteLocationNormalized } from "vue-router"
import { DataType, DataTypeToLabel } from "@/utils/enum"

const SITE_URL = "https://carte.iarbre.fr"
const SITE_NAME = "IA·rbre"
const DEFAULT_TITLE = "Carte IA·rbre : où planter des arbres et îlots de chaleur à Lyon"
const DEFAULT_DESCRIPTION =
  "Carte interactive de la Métropole de Lyon : score de plantabilité des arbres, vulnérabilité à la chaleur, zones climatiques locales, strates végétales et biodiversité. Données ouvertes."

const DataTypeToDescription: Record<DataType, string> = {
  [DataType.PLANTABILITY]:
    "Score de plantabilité des arbres de 0 à 10 sur des tuiles de 5 x 5 m dans la Métropole de Lyon : réseaux souterrains, voirie et bâti pris en compte.",
  [DataType.VULNERABILITY]:
    "Carte de vulnérabilité à la chaleur de la Métropole de Lyon : zones les plus exposées aux vagues de chaleur et aux îlots de chaleur urbains.",
  [DataType.PLANTABILITY_VULNERABILITY]:
    "Croisement du score de plantabilité et de la vulnérabilité à la chaleur pour cibler où planter des arbres en priorité dans la Métropole de Lyon.",
  [DataType.CLIMATE_ZONE]:
    "Zones climatiques locales (ZCL / LCZ) de la Métropole de Lyon pour comprendre les îlots de chaleur urbains.",
  [DataType.VEGESTRATE]:
    "Strates végétales herbacée, arbustive et arborée de la Métropole de Lyon détectées par intelligence artificielle.",
  [DataType.BIOSPHERE_FUNCTIONAL_INTEGRITY]:
    "Intégrité fonctionnelle de la biosphère dans la Métropole de Lyon : un indicateur de biodiversité en ville."
}

interface PageMeta {
  title: string
  description: string
  canonicalPath: string
  noindex: boolean
}

function getPageMeta(route: RouteLocationNormalized): PageMeta {
  const dataType = route.params.dataType as DataType | undefined
  if (dataType && dataType in DataTypeToDescription) {
    return {
      title: `${DataTypeToLabel[dataType]} à Lyon | Carte ${SITE_NAME}`,
      description: DataTypeToDescription[dataType],
      canonicalPath: "/",
      noindex: false
    }
  }
  if (route.meta.title) {
    return {
      title: `${route.meta.title} | Carte ${SITE_NAME}`,
      description: (route.meta.description as string | undefined) ?? DEFAULT_DESCRIPTION,
      canonicalPath: route.path,
      noindex: Boolean(route.meta.noindex)
    }
  }
  return {
    title: DEFAULT_TITLE,
    description: DEFAULT_DESCRIPTION,
    canonicalPath: "/",
    noindex: Boolean(route.meta.noindex)
  }
}

function setMeta(attribute: "name" | "property", key: string, content: string) {
  let element = document.head.querySelector<HTMLMetaElement>(`meta[${attribute}="${key}"]`)
  if (!element) {
    element = document.createElement("meta")
    element.setAttribute(attribute, key)
    document.head.appendChild(element)
  }
  element.content = content
}

function setCanonical(href: string) {
  let element = document.head.querySelector<HTMLLinkElement>('link[rel="canonical"]')
  if (!element) {
    element = document.createElement("link")
    element.rel = "canonical"
    document.head.appendChild(element)
  }
  element.href = href
}

export function updatePageMeta(route: RouteLocationNormalized) {
  const { title, description, canonicalPath, noindex } = getPageMeta(route)
  const url = `${SITE_URL}${canonicalPath}`
  document.title = title
  setMeta("name", "description", description)
  setMeta("property", "og:title", title)
  setMeta("property", "og:description", description)
  setMeta("property", "og:url", url)
  setMeta("name", "robots", noindex ? "noindex" : "index, follow")
  setCanonical(url)
}
