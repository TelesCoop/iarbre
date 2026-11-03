<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { DataType, DataTypeToLabel } from "@/utils/enum"

const mapStore = useMapStore()
</script>

<template>
  <div class="flex flex-col gap-3 px-2 py-4">
    <div
      class="flex flex-col gap-1 bg-white border border-gray-200 rounded-lg p-3"
      data-cy="pet-description"
    >
      <h3 class="text-sm font-bold text-primary-900">
        {{ DataTypeToLabel[DataType.PET] }} - {{ mapStore.petYear }}
      </h3>
      <div class="flex flex-col gap-2 text-sm text-gray-700">
        <p>
          C'est une température ressentie (PET), en journée, obtenue à l'aide d'un modélisation du climat urbain pour une journée (légèrement chaude) le 14 juillet
          {{ mapStore.petYear }}. Nous répliquons, avec son aide, une
          <a
            class="text-primary-700 underline"
            href="https://www.sciencedirect.com/science/article/pii/S0360132325007188"
            rel="noopener noreferrer"
            target="_blank"
            >étude</a
          >
          menée par le chercheur Damien David du CETHIL.
        </p>
        <p>
          Le PET (Physiological Equivalent Temperature) est un indicateur reflétant le
          confort/inconfort d'une personne selon les caractéristiques d'ambiance : température de
          l'air, ombre ou soleil, circulation d'air/vent, rayonnement secondaire des bâtiments et du sol. Ici, la
          personne est simulée assise et immobile.
        </p>
        <p>Les données d'entrée sont :</p>
        <ul class="list-disc pl-5">
          <li>Les bâtiments,</li>
          <li>Le modèle de hauteur de la végétation,</li>
          <li>L'occupation des sols (béton, terre, etc.),</li>
          <li>
            Projection météo {{ mapStore.petYear }} heure par heure (température, humidité relative,
            vent).
          </li>
        </ul>
        <p>
          Les modélisations sont faites à l'aide du modèle open-source SOLWEIG. Chaque pixel
          correspond à une zone de 1mx1m.
        </p>
      </div>
    </div>
  </div>
</template>
