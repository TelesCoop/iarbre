<script lang="ts" setup>
import SidebarComponent from "@/components/sidebar/SidebarComponent.vue"

const changes = [
  {
    topic: "Taille d'un carreau",
    old: "5 x 5 m",
    new: "1 x 1 m"
  },
  {
    topic: "Calcul du score",
    old: "Pourcentage du carreau couverte par chaque facteur",
    new: "Présence du facteur (à 1m on a la plupart du temps qu'un facteur), adoucie en bordure selon la précision de la donnée"
  },
  {
    topic: "Précision des données",
    old: "Non prise en compte",
    new: "Une précision par source (ex: gaz ±1 m, végétation ±0,5 m) qui sert à faire la zone bordure"
  },
  {
    topic: "Zones bloquantes (bâtiments, ponts, voies ferrées, plans d'eau...)",
    old: "Poids de -5 pour ces facteurs",
    new: "Tout carreau touché est bloqué en entier"
  },
  {
    topic: "Contraintes et atouts",
    old: "Limite nette du tracé",
    new: "Les contraintes débordent un peu, les atouts sont rognés en bordure"
  },
  {
    topic: "Végétation",
    old: "EVA 2015 (photo-interprétation, simplifiée à 3 m)",
    new: "Végéstrate 2023 (0,2 m), complétée par EVA 2023"
  },
  {
    topic: "Petits espaces de plantation : post-processing",
    old: "Dilués sous 5 m",
    new: "Gardés si un carré de 4 x 4 m y tient, pixels isolés retirés"
  }
]

const newLimits = [
  "Pour les réseaux Enedis, l'assainissement, la fibre et le réseau de chaleur la précision n'a pas progressé : leur tracé est gardé tel quel, sans marge. La carte à 1 m paraît plus précise que ces données. C'est pourquoi on fait un post-processing pour avoir des zones élémentaires de 4x4m (fosse de pied d'arbre).",
  "La précision du réseau de gaz a progressé (comparaison aux affleurants du PCRS).",
  "Les branchements de gaz vers les bâtiments ne sont pas dans les données ouvertes. La proximité des façades couvre ces raccordements en partie.",
  "Un espace où ne tient pas un carré de 4 x 4 m reçoit un score plus faible, même s'il est plantable.",
  "Les seuils des classes sont ceux de la carte à 5 m. Ils seront recalculés sur toute la Métropole."
]

const blurRules = [
  "Contrainte (poids négatif) : la zone ne peut que grandir. Pénalité entière à l'intérieur, qui s'estompe à l'extérieur.",
  "Atout (poids positif) : la zone ne peut que rétrécir. Aucun bonus à l'extérieur, bonus réduit près du bord.",
  "Zones bloquantes : pas de flou, leur emprise est élargie de leur précision.",
  "Sources sans précision connue : pas de flou, limite nette (et toujours application d'un buffer)."
]

const blurExamples = [
  {
    title: "Réseau de gaz",
    detail: "poids -3, précision ±1 m",
    rows: [
      { place: "Dans la zone", hard: -3, blurred: -3 },
      { place: "0,5 m à l'extérieur", hard: 0, blurred: -0.9 },
      { place: "1 m à l'extérieur", hard: 0, blurred: -0.5 },
      { place: "2 m à l'extérieur", hard: 0, blurred: -0.1 }
    ]
  },
  {
    title: "Strate basse (Végéstrate)",
    detail: "poids +3, précision ±0,5 m",
    rows: [
      { place: "Bien à l'intérieur", hard: 3, blurred: 3 },
      { place: "0,25 m à l'intérieur du bord", hard: 3, blurred: 2.1 },
      { place: "À l'extérieur", hard: 0, blurred: 0 }
    ]
  }
]

const formatScore = (value: number, approx = false) =>
  (approx ? "≈ " : "") + value.toLocaleString("fr-FR", { signDisplay: "exceptZero" })

const postProcessingSteps = [
  {
    title: "Pixels isolés",
    text: "Un pixel seul dans sa classe, entouré de pixels d'autres classes, prend le score moyen de ses voisins de la classe qui l'entoure."
  },
  {
    title: "Espaces de 4 x 4 m",
    text: "Un pixel garde son score seulement s'il fait partie d'un carré de 4 x 4 m dont tous les pixels ont au moins ce score. Sinon il prend le meilleur score possible pour un tel carré. Une bande plantable plus étroite que 4 m descend donc au score de ce qui l'entoure."
  }
]

const oldLimits = [
  "Prudence parfois trompeuse : la moyenne sur 5 m n'absorbe pas toujours les erreurs de position. Un réseau sur le bord d'un carreau et en réalité décalé de 3 m tombe dans un carreau voisin, non pénalisé.",
  "Un carreau à cheval entre partie en herbe et chaussée reçoit un score moyen qui ne correspond à aucun des deux.",
  "La végétation EVA ignore les surfaces de moins de 100 m² ou de moins de 3 m de large et est peu précise sur les bordures de zone. 7 % des zones arborées EVA n'ont pas de végétation dans Végéstrate, surtout en bordure.",
  "Carte 2025 publiée : décalage de 2 m vers le nord-ouest, entrées de parkings publiques absentes. Corrigé dans les deux cartes 2026."
]
</script>

<template>
  <div class="flex h-screen lg:ml-18">
    <SidebarComponent />
    <main class="flex-1 overflow-y-auto bg-gray-50 px-4 pt-6 pb-24 md:px-8 lg:px-12 lg:py-12">
      <article class="mx-auto flex max-w-4xl flex-col gap-10 text-brown">
        <header class="flex max-w-2xl flex-col gap-3">
          <h1 class="font-accent text-3xl font-bold">Plantabilité 2026 : ce qui change</h1>
          <p class="text-base leading-relaxed">
            Perimètre de Villeurbanne uniquement. Les deux cartes utilisent les données 2026. A 5x5m
            c'est la méthode de calcul originel et à 1x1m une mise à jour de la méthode (zone de
            flou et postprocessing). Les poids des facteurs restent les mêmes.
          </p>
        </header>

        <section class="flex flex-col gap-4" aria-labelledby="changes-title">
          <h2 id="changes-title" class="text-xl font-semibold">Ancienne et nouvelle méthode</h2>
          <div class="overflow-x-auto rounded-lg border border-gray-200 bg-white">
            <table class="w-full min-w-xl border-collapse text-sm" data-cy="methodology-changes">
              <thead>
                <tr class="border-b border-gray-200 text-left">
                  <th class="w-1/4 px-4 py-3 font-medium text-gray-500" scope="col">
                    <span class="sr-only">Sujet</span>
                  </th>
                  <th class="w-3/8 px-4 py-3 font-semibold text-gray-700" scope="col">
                    Méthode actuelle (5 m)
                  </th>
                  <th
                    class="w-3/8 bg-primary-50 px-4 py-3 font-semibold text-primary-700"
                    scope="col"
                  >
                    Nouvelle méthode (1 m)
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="change in changes"
                  :key="change.topic"
                  class="border-b border-gray-100 align-top last:border-b-0"
                >
                  <th class="px-4 py-3 text-left font-medium" scope="row">{{ change.topic }}</th>
                  <td class="px-4 py-3 text-gray-600">{{ change.old }}</td>
                  <td class="bg-primary-50 px-4 py-3">{{ change.new }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section class="flex flex-col gap-4" aria-labelledby="blur-title">
          <h2 id="blur-title" class="text-xl font-semibold">Zone de flou en bordure</h2>
          <div class="flex max-w-2xl flex-col gap-3 text-base leading-relaxed">
            <p>
              À 5 m, un facteur compte selon la part du carreau qu'il couvre : un carreau couvert à
              40&nbsp;% par la zone du réseau de gaz reçoit 0,4&nbsp;x&nbsp;-3&nbsp;=&nbsp;-1,2. À 1
              m, un pixel est dedans ou dehors, et le score n'est plus qu'une somme de poids
              entiers. Cette limite nette supposerait une précision plus grandes que celles des
              données en réalité, d'où l'utilisation de flou sur la bordure, en plus du buffer.
            </p>
            <p>
              Nous avons donc pour chaque source une précision estimée en mètres. À 1 m, la zone est
              floutée sur cette distance avec une décroissance (non-linéaire, gaussienne), ce qui
              donne la probabilité que l'objet couvre vraiment le pixel. Le flou reste prudent :
            </p>
            <ul class="flex list-disc flex-col gap-1.5 pl-5 text-sm">
              <li v-for="rule in blurRules" :key="rule">{{ rule }}</li>
            </ul>
          </div>

          <div class="grid gap-4 md:grid-cols-2">
            <figure
              v-for="example in blurExamples"
              :key="example.title"
              class="flex flex-col gap-2 rounded-lg border border-gray-200 bg-white p-4"
            >
              <figcaption>
                <span class="font-semibold">{{ example.title }}</span>
                <span class="text-sm text-gray-500"> ({{ example.detail }})</span>
              </figcaption>
              <table class="w-full border-collapse text-sm">
                <thead>
                  <tr class="text-left text-gray-500">
                    <th class="py-1.5 pr-2 font-medium" scope="col">Pixel</th>
                    <th class="py-1.5 pr-2 whitespace-nowrap text-right font-medium" scope="col">
                      Ancienne méthode (net)
                    </th>
                    <th class="w-2/5 py-1.5 pl-2 font-medium" scope="col">
                      Nouvelle méthode (flou)
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="row in example.rows" :key="row.place" class="border-t border-gray-100">
                    <th class="py-1.5 pr-2 text-left font-normal" scope="row">{{ row.place }}</th>
                    <td class="py-1.5 pr-2 text-right tabular-nums text-gray-500">
                      {{ formatScore(row.hard) }}
                    </td>
                    <td class="py-1.5 pl-2">
                      <div class="flex items-center gap-2">
                        <span class="w-12 shrink-0 tabular-nums">
                          {{ formatScore(row.blurred, row.blurred !== row.hard) }}
                        </span>
                        <span class="h-2 flex-1 rounded-full bg-gray-100" aria-hidden="true">
                          <span
                            :class="[
                              'block h-full rounded-full',
                              row.blurred < 0 ? 'bg-orange-400' : 'bg-primary-500'
                            ]"
                            :style="{ width: `${(Math.abs(row.blurred) / 3) * 100}%` }"
                          />
                        </span>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </figure>
          </div>
        </section>

        <section class="flex flex-col gap-4" aria-labelledby="post-title">
          <h2 id="post-title" class="text-xl font-semibold">Post-traitement</h2>
          <p class="max-w-2xl text-base leading-relaxed">
            Après la somme pondérée des facteurs, deux étapes nettoient la carte à 1 m. Les pixels
            bloqués ne changent jamais.
          </p>
          <ol class="grid gap-4 md:grid-cols-2">
            <li
              v-for="(step, index) in postProcessingSteps"
              :key="step.title"
              class="flex gap-3 rounded-lg border border-gray-200 bg-white p-4"
            >
              <span
                class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-primary-100 text-sm font-semibold text-primary-700"
                aria-hidden="true"
              >
                {{ index + 1 }}
              </span>
              <div class="flex flex-col gap-1">
                <h3 class="font-semibold">{{ step.title }}</h3>
                <p class="text-sm leading-relaxed">{{ step.text }}</p>
              </div>
            </li>
          </ol>
        </section>

        <div class="grid gap-8 md:grid-cols-2">
          <section class="flex flex-col gap-3" aria-labelledby="new-limits-title">
            <h2 id="new-limits-title" class="text-xl font-semibold">
              Limites de la nouvelle méthode
            </h2>
            <ul class="flex list-disc flex-col gap-3 pl-5 text-sm leading-relaxed">
              <li v-for="limit in newLimits" :key="limit">{{ limit }}</li>
            </ul>
          </section>
          <section class="flex flex-col gap-3" aria-labelledby="old-limits-title">
            <h2 id="old-limits-title" class="text-xl font-semibold">
              Limites et biais de l'ancienne méthode
            </h2>
            <ul class="flex list-disc flex-col gap-3 pl-5 text-sm leading-relaxed">
              <li v-for="limit in oldLimits" :key="limit">{{ limit }}</li>
            </ul>
          </section>
        </div>
      </article>
    </main>
  </div>
</template>
