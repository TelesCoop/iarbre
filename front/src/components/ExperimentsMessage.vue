<script lang="ts" setup>
import IconExperiment from "@/components/icons/IconExperiment.vue"

const visible = defineModel<boolean>({ default: false })

const experiments = [
  {
    title: "Ipave",
    description: "Faire un découpage de l'espace public (la voirie) et projetr le végétal dessus.",
    url: "https://feature-ipave-carte.iarbre.fr/"
  },
  {
    title: "Variations Vegestrate",
    description: "Les différentes pre-processing testés et les diachronies non publiées encore.",
    url: "https://feature-vegestrate-1-carte.iarbre.fr/"
  }
]
</script>

<template>
  <AppDialog
    v-model:visible="visible"
    :draggable="false"
    width="28rem"
    header="Expérimentations"
    modal
    data-cy="experiments-dialog"
    :closable="true"
  >
    <div class="flex flex-col gap-4 bg-white">
      <div class="space-y-4">
        <a
          v-for="experiment in experiments"
          :key="experiment.title"
          :href="experiment.url"
          target="_blank"
          rel="noopener noreferrer"
          class="welcome-functionnality welcome-functionnality--clickable w-full text-left"
        >
          <span
            class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-gray-100 bg-gray-50 text-primary-600"
          >
            <IconExperiment :size="20" />
          </span>
          <div>
            <h4 class="font-medium">{{ experiment.title }}</h4>
            <p class="text-sm">{{ experiment.description }}</p>
          </div>
        </a>
      </div>
    </div>

    <template #footer>
      <AppButton data-cy="experiments-close" full-width @click="visible = false">
        Fermer
      </AppButton>
    </template>
  </AppDialog>
</template>
