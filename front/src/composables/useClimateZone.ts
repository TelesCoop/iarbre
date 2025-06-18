import { ClimateCategory, ClimateDataDetailsKey } from "@/types/climate"

export const useClimateZone = () => {
  const climateZoneDetailsByCategory = {
    [ClimateCategory.BUILDING]: [
      {
        key: ClimateDataDetailsKey.HRE,
        label: "Hauteur moyenne du bâti",
        unit: "m",
        description: "Hauteur moyenne des bâtiments dans la zone"
      },
      {
        key: ClimateDataDetailsKey.ARE,
        label: "Superficie moyenne du bâti",
        unit: "m²",
        description: "Superficie moyenne des bâtiments"
      },
      {
        key: ClimateDataDetailsKey.BUR,
        label: "Taux de surface bâtie",
        unit: "%",
        description: "Pourcentage de la surface occupée par des bâtiments"
      }
    ],
    [ClimateCategory.SURFACES]: [
      {
        key: ClimateDataDetailsKey.ROR,
        label: "Surface minérale imperméable",
        unit: "%",
        description: "Pourcentage de surface imperméable (routes, trottoirs, etc.)"
      },
      {
        key: ClimateDataDetailsKey.BSR,
        label: "Sol nu perméable",
        unit: "%",
        description: "Pourcentage de sol nu mais perméable"
      }
    ],
    [ClimateCategory.VEGETATION]: [
      {
        key: ClimateDataDetailsKey.WAR,
        label: "Surface en eau",
        unit: "%",
        description: "Pourcentage de surface occupée par l'eau"
      },
      {
        key: ClimateDataDetailsKey.VER,
        label: "Végétation totale",
        unit: "%",
        description: "Pourcentage de surface couverte par la végétation"
      },
      {
        key: ClimateDataDetailsKey.VHR,
        label: "Végétation arborée",
        unit: "%",
        description: "Part de végétation arborée sur la végétation totale"
      }
    ]
  }

  const climateCategoryToIcon: Record<ClimateCategory, string> = {
    [ClimateCategory.BUILDING]: "🏢",
    [ClimateCategory.SURFACES]: "🛣️",
    [ClimateCategory.VEGETATION]: "🌿"
  }

  const climateCategoryToDescription: Record<ClimateCategory, string> = {
    [ClimateCategory.BUILDING]: "Indicateurs liés aux bâtiments et à l'urbanisation",
    [ClimateCategory.SURFACES]: "Répartition des différents types de surfaces au sol",
    [ClimateCategory.VEGETATION]: "Présence de végétation et d'eau dans la zone"
  }

  const climateCategoryKey: Record<ClimateCategory, string> = {
    [ClimateCategory.BUILDING]: "building",
    [ClimateCategory.SURFACES]: "surfaces",
    [ClimateCategory.VEGETATION]: "vegetation"
  }

  const climateCategoryOrder = [
    ClimateCategory.BUILDING,
    ClimateCategory.SURFACES,
    ClimateCategory.VEGETATION
  ]

  return {
    climateZoneDetailsByCategory,
    climateCategoryToIcon,
    climateCategoryToDescription,
    climateCategoryOrder,
    climateCategoryKey
  }
}
