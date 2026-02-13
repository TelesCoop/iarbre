<script lang="ts" setup>
import { ref } from "vue"
import AppButton from "@/components/shared/AppButton.vue"
import IconLegal from "@/components/icons/IconLegal.vue"

type Tab = "mentions" | "privacy"

const activeTab = ref<Tab>("mentions")
</script>

<template>
  <div class="legal-page">
    <div class="legal-container">
      <header class="legal-header">
        <div class="legal-header-top">
          <router-link to="/">
            <AppButton size="sm" variant="ghost">
              <template #icon-left>
                <svg
                  fill="none"
                  height="16"
                  stroke="currentColor"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  viewBox="0 0 24 24"
                  width="16"
                >
                  <path d="m15 18-6-6 6-6" />
                </svg>
              </template>
              Retour à la carte
            </AppButton>
          </router-link>
        </div>

        <div class="legal-title-block">
          <IconLegal :size="32" class="text-primary-500" />
          <h1 class="legal-title">Informations légales</h1>
        </div>

        <nav class="legal-tabs">
          <button
            :class="['legal-tab', { active: activeTab === 'mentions' }]"
            @click="activeTab = 'mentions'"
          >
            Mentions légales
          </button>
          <button
            :class="['legal-tab', { active: activeTab === 'privacy' }]"
            @click="activeTab = 'privacy'"
          >
            Politique de confidentialité
          </button>
        </nav>
      </header>

      <main class="legal-content">
        <section v-if="activeTab === 'mentions'">
          <h2 class="section-title">Mentions légales</h2>

          <div class="section-block">
            <h3 class="block-title">Éditeur du site</h3>
            <p>Le site <strong>IA·rbre</strong> (carte.iarbre.fr) est édité par :</p>
            <ul class="legal-list">
              <li><strong>TELESCOOP</strong>, SARL SCOP</li>
              <li>SIREN : 890 488 950</li>
              <li>Siège social : Paris (75008)</li>
              <li>
                Contact :
                <a class="legal-link" href="mailto:contact@telescoop.fr">contact@telescoop.fr</a>
              </li>
            </ul>
          </div>

          <div class="section-block">
            <h3 class="block-title">Hébergeur</h3>
            <ul class="legal-list">
              <li><strong>OVH SAS</strong></li>
              <li>2 rue Kellermann, 59100 Roubaix, France</li>
              <li>RCS Lille Métropole 424 761 419 00045</li>
              <li>
                Site web :
                <a
                  class="legal-link"
                  href="https://www.ovhcloud.com"
                  rel="noopener noreferrer"
                  target="_blank"
                >
                  www.ovhcloud.com
                </a>
              </li>
            </ul>
          </div>

          <div class="section-block">
            <h3 class="block-title">Propriété intellectuelle</h3>
            <p>
              Le code source de IA·rbre est disponible en open source sur
              <a
                class="legal-link"
                href="https://github.com/TelesCoop/iarbre"
                rel="noopener noreferrer"
                target="_blank"
              >
                GitHub </a
              >.
            </p>
          </div>
        </section>

        <section v-if="activeTab === 'privacy'">
          <h2 class="section-title">Politique de confidentialité</h2>

          <div class="section-block">
            <h3 class="block-title">Responsable du traitement</h3>
            <p>Le responsable du traitement des données personnelles est :</p>
            <ul class="legal-list">
              <li><strong>TELESCOOP</strong>, SARL SCOP</li>
              <li>SIREN : 890 488 950</li>
              <li>
                Contact :
                <a class="legal-link" href="mailto:contact@telescoop.fr">contact@telescoop.fr</a>
              </li>
            </ul>
          </div>

          <div class="section-block">
            <h3 class="block-title">Données collectées</h3>

            <h4 class="sub-block-title">Formulaire de contact / feedback</h4>
            <ul class="legal-list">
              <li><strong>Données</strong> : adresse email (optionnelle), message</li>
              <li><strong>Base légale</strong> : consentement (article 6.1.a du RGPD)</li>
              <li><strong>Finalité</strong> : répondre à vos retours et améliorer le service</li>
              <li><strong>Durée de conservation</strong> : 12 mois après réception</li>
            </ul>

            <h4 class="sub-block-title">Analytics (Plausible)</h4>
            <ul class="legal-list">
              <li>
                Nous utilisons <strong>Plausible Analytics</strong>, une solution d'analyse
                respectueuse de la vie privée
              </li>
              <li>Aucun cookie n'est déposé</li>
              <li>Aucune donnée personnelle n'est collectée</li>
              <li>Les données sont agrégées et anonymes</li>
              <li>Conforme au RGPD sans nécessité de consentement (exempté par la CNIL)</li>
            </ul>

            <h4 class="sub-block-title">Cookie technique (CSRF)</h4>
            <ul class="legal-list">
              <li>
                Un cookie technique <code>csrftoken</code> est utilisé pour la protection contre les
                attaques CSRF (Cross-Site Request Forgery)
              </li>
              <li>Ce cookie est strictement nécessaire au fonctionnement du site</li>
              <li>Exempté de consentement conformément à la directive ePrivacy</li>
            </ul>

            <h4 class="sub-block-title">Stockage local (localStorage)</h4>
            <ul class="legal-list">
              <li>
                Une clé <code>hasVisitedBefore</code> est stockée localement pour adapter
                l'affichage du message de bienvenue
              </li>
              <li>Donnée purement fonctionnelle, non transmise à un serveur</li>
            </ul>
          </div>

          <div class="section-block">
            <h3 class="block-title">Vos droits</h3>
            <p>
              Conformément au RGPD, vous disposez des droits suivants sur vos données personnelles :
            </p>
            <ul class="legal-list">
              <li><strong>Droit d'accès</strong> : obtenir une copie de vos données</li>
              <li><strong>Droit de rectification</strong> : corriger vos données inexactes</li>
              <li><strong>Droit de suppression</strong> : demander l'effacement de vos données</li>
              <li>
                <strong>Droit à la portabilité</strong> : recevoir vos données dans un format
                structuré
              </li>
              <li>
                <strong>Droit d'opposition</strong> : vous opposer au traitement de vos données
              </li>
              <li>
                <strong>Droit de retrait du consentement</strong> : retirer votre consentement à
                tout moment
              </li>
            </ul>
            <p>
              Pour exercer ces droits, contactez-nous à :
              <a class="legal-link" href="mailto:contact@telescoop.fr">contact@telescoop.fr</a>
            </p>
          </div>

          <div class="section-block">
            <h3 class="block-title">Réclamation</h3>
            <p>
              Si vous estimez que le traitement de vos données ne respecte pas la réglementation,
              vous pouvez introduire une réclamation auprès de la
              <a
                class="legal-link"
                href="https://www.cnil.fr"
                rel="noopener noreferrer"
                target="_blank"
              >
                CNIL
              </a>
              (Commission Nationale de l'Informatique et des Libertés).
            </p>
          </div>

          <div class="section-block">
            <h3 class="block-title">Mise à jour</h3>
            <p>
              Cette politique de confidentialité peut être mise à jour à tout moment. La date de
              dernière mise à jour est indiquée ci-dessous.
            </p>
            <p class="text-sm text-gray-500">Dernière mise à jour : février 2026</p>
          </div>
        </section>
      </main>
    </div>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.legal-page {
  @apply min-h-screen bg-off-white;
}

.legal-container {
  @apply max-w-3xl mx-auto px-4 py-8;
}

.legal-header {
  @apply mb-8;
}

.legal-header-top {
  @apply mb-6;
}

.legal-title-block {
  @apply flex items-center gap-3 mb-6;
}

.legal-title {
  @apply text-3xl font-bold text-brown font-accent;
}

.legal-tabs {
  @apply flex gap-2 border-b border-gray-200;
}

.legal-tab {
  @apply px-4 py-2 text-sm font-medium cursor-pointer;
  @apply border-b-2 border-transparent;
  @apply text-gray-500 bg-transparent;
  @apply transition-colors duration-200;
  @apply hover:text-primary-500;
}

.legal-tab.active {
  @apply text-primary-500 border-primary-500;
}

.legal-content {
  @apply text-brown text-base leading-relaxed;
}

.section-title {
  @apply text-2xl font-semibold text-brown mb-6 font-accent;
}

.section-block {
  @apply mb-8;
}

.block-title {
  @apply text-lg font-semibold text-brown mb-3;
}

.sub-block-title {
  @apply text-base font-medium text-brown mt-4 mb-2;
}

.legal-list {
  @apply list-disc pl-6 space-y-1 my-2;
}

.legal-link {
  @apply text-primary-500 underline;
  @apply hover:text-primary-600;
  @apply transition-colors duration-200;
}

code {
  @apply bg-gray-100 px-1.5 py-0.5 rounded text-sm;
}
</style>
