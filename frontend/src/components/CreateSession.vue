<script setup>
import { ref, computed, watch } from 'vue';
import { createSession } from '../api';
import { MapPin, Navigation, Utensils, ArrowRight, Loader2, AlertCircle, Footprints, Clock, Star } from 'lucide-vue-next';

const emit = defineEmits(['sessionCreated']);

const departureAddress = ref('');
const walkMinutes = ref(15);
const maxRestaurants = ref(35);
const WALKING_SPEED_M_PER_MIN = 100; // Allure dynamique ~6 km/h (100 m/min)
const radiusMeters = computed(() => Math.round(walkMinutes.value * WALKING_SPEED_M_PER_MIN));
const isLoading = ref(false);
const loadingStep = ref('');
const errorMessage = ref('');

// Si l'utilisateur choisit un très grand rayon (>=25 min), suggérer 50 restaurants automatiquement
watch(walkMinutes, (newMins) => {
  if (newMins >= 25 && maxRestaurants.value === 20) {
    maxRestaurants.value = 50;
  }
});

// Efface l'erreur dès que l'utilisateur modifie l'adresse ou la durée
watch([departureAddress, walkMinutes, maxRestaurants], () => {
  if (errorMessage.value) errorMessage.value = '';
});

const durationPresets = [
  { minutes: 5, label: '5 min', meters: '~500 m' },
  { minutes: 10, label: '10 min', meters: '~1 km' },
  { minutes: 15, label: '15 min', meters: '~1,5 km' },
  { minutes: 20, label: '20 min', meters: '~2 km' },
  { minutes: 30, label: '30 min', meters: '~3 km' },
];

async function handleCreateSession() {
  const address = departureAddress.value.trim();
  if (!address) {
    errorMessage.value = "Veuillez renseigner une adresse ou un lieu de départ.";
    return;
  }

  isLoading.value = true;
  errorMessage.value = '';
  loadingStep.value = "Recherche des restaurants les mieux notés et extraction des formules...";

  try {
    const session = await createSession(address, radiusMeters.value, maxRestaurants.value);
    emit('sessionCreated', session);
  } catch (err) {
    errorMessage.value = err.message || "Une erreur est survenue lors de la création de la session.";
  } finally {
    isLoading.value = false;
  }
}

</script>

<template>
  <div class="max-w-5xl mx-auto px-4 py-6 sm:py-10">
    <!-- En-tête Brasserie & Fronton d'Honneur -->
    <div class="text-center mb-8 sm:mb-12">
      <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-[var(--border-ornament)] bg-[var(--bg-surface)] text-[var(--accent-brass)] text-xs uppercase tracking-widest font-serif font-bold shadow-xs mb-3.5">
        <span>⚜</span>
        <span class="tracking-widest">Grand Registre des Déjeuners</span>
        <span>⚜</span>
      </div>
      <h1 class="font-display sm:font-serif text-4xl sm:text-5xl lg:text-6xl font-normal tracking-wide text-[var(--text-main)] mb-3 leading-tight">
        Où déjeunons-nous ce midi ?
      </h1>
      <div class="flex items-center justify-center gap-3 text-[var(--accent-brass)] text-sm mb-2">
        <span>❧</span>
        <span class="font-serif italic text-base sm:text-lg">Service de Table & Consultation des Cartes du Quartier</span>
        <span>☙</span>
      </div>
      <p class="text-sm sm:text-base text-[var(--text-muted)] max-w-xl mx-auto leading-relaxed">
        Indiquez votre adresse de ralliement pour recenser les meilleures tables accessibles à pied, consulter leurs formules du midi et voter à l'unanimité.
      </p>
    </div>

    <!-- Le Grand Registre / Livre d'Accueil Déployé (Cadre Brasserie Grand Format) -->
    <div class="bistro-grand-frame rounded-3xl p-6 sm:p-10 relative">
      <!-- 4 Coins en Laiton Vénérable -->
      <div class="brass-corner-bracket brass-corner-tl"></div>
      <div class="brass-corner-bracket brass-corner-tr"></div>
      <div class="brass-corner-bracket brass-corner-bl"></div>
      <div class="brass-corner-bracket brass-corner-br"></div>

      <form @submit.prevent="handleCreateSession" class="relative z-10">
        <!-- Grille en 2 volets ouverts (Façon Livre d'Or de Brasserie) -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-10">
          
          <!-- Volet Gauche : Adresse & Périmètre d'arpentage -->
          <div class="lg:col-span-7 space-y-6">
            <div class="flex items-center gap-2 border-b border-[var(--border-subtle)] pb-2 mb-1">
              <span class="font-serif text-xs font-bold text-[var(--accent-brass)] uppercase tracking-wider">Volet I</span>
              <span class="text-[var(--text-faint)]">•</span>
              <h2 class="font-serif text-xl sm:text-2xl font-normal text-[var(--text-main)]">
                Le Point de Ralliement
              </h2>
            </div>

            <!-- Champ Adresse de départ -->
            <div>
              <label for="address-input" class="block font-serif text-sm font-semibold text-[var(--text-main)] mb-2 tracking-wide">
                📍 Adresse de départ ou station
              </label>
              <div class="relative rounded-2xl">
                <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-4 text-[var(--text-faint)]">
                  <MapPin class="h-4 w-4 text-[var(--accent-red)]" />
                </div>
                <input
                  id="address-input"
                  v-model="departureAddress"
                  type="text"
                  required
                  :disabled="isLoading"
                  placeholder="ex : 12 rue de la Paix, Paris ou 31 allée Christine Pascal, Lyon"
                  class="block w-full rounded-2xl border border-[var(--border-main)] bg-[var(--bg-surface-inset)] pl-11 pr-4 py-3.5 text-[var(--text-main)] placeholder:text-[var(--text-faint)] focus:border-[var(--accent-brass)] focus:bg-[var(--bg-surface)] focus:ring-2 focus:ring-[var(--accent-brass)]/20 focus:outline-none text-sm sm:text-base transition font-normal"
                />
              </div>
              <p class="mt-2 text-xs text-[var(--text-muted)] font-serif italic">
                Toutes les adresses seront repérées à partir de cet ancrage géographique.
              </p>
            </div>

            <!-- Réglette Périmètre de marche -->
            <div class="bg-[var(--bg-surface-subtle)] rounded-2xl p-5 sm:p-6 border border-[var(--border-subtle)] space-y-4">
              <div class="flex items-center justify-between gap-2">
                <label for="walk-slider" class="font-serif text-base font-normal text-[var(--text-main)] flex items-center gap-2">
                  <Footprints class="w-4 h-4 text-[var(--accent-red)]" />
                  <span>Périmètre de marche maximale</span>
                </label>
                <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[var(--bg-surface)] border border-[var(--border-main)] text-[var(--text-main)] font-medium text-xs shadow-xs">
                  <Clock class="w-3.5 h-3.5 text-[var(--accent-brass)]" />
                  <span class="font-serif font-bold text-sm text-[var(--accent-brass)]">{{ walkMinutes }} min</span>
                  <span class="text-xs text-[var(--text-muted)]">(~{{ radiusMeters >= 1000 ? (radiusMeters / 1000).toFixed(1).replace('.', ',') + ' km' : radiusMeters + ' m' }})</span>
                </div>
              </div>

              <div class="py-1">
                <input
                  id="walk-slider"
                  v-model.number="walkMinutes"
                  type="range"
                  min="3"
                  max="35"
                  step="1"
                  :disabled="isLoading"
                  class="slider-custom"
                />
              </div>

              <!-- Raccourcis cliquables sous le slider -->
              <div class="flex justify-between items-center text-xs gap-1">
                <button
                  v-for="preset in durationPresets"
                  :key="preset.minutes"
                  type="button"
                  :disabled="isLoading"
                  @click="walkMinutes = preset.minutes"
                  :class="[
                    walkMinutes === preset.minutes
                      ? 'text-white font-medium bg-[var(--accent-brass)] border border-[var(--accent-brass)] shadow-xs'
                      : 'text-[var(--text-muted)] hover:text-[var(--text-main)] hover:bg-[var(--bg-surface)]',
                    'cursor-pointer transition px-2.5 sm:px-3 py-1.5 rounded-xl flex items-center gap-1'
                  ]"
                >
                  <span class="font-serif font-bold">{{ preset.label }}</span>
                  <span class="text-[10px] opacity-80 hidden sm:inline">({{ preset.meters }})</span>
                </button>
              </div>

              <p class="text-xs text-[var(--text-muted)] pt-1">
                Allure dynamique calculée à 6 km/h (100 mètres par minute).
              </p>
            </div>
          </div>

          <!-- Volet Droit : Format de table, Protocole & Grand Sceau -->
          <div class="lg:col-span-5 flex flex-col justify-between space-y-6 lg:border-l lg:border-[var(--border-subtle)] lg:pl-10">
            <div class="space-y-5">
              <div class="flex items-center gap-2 border-b border-[var(--border-subtle)] pb-2 mb-1">
                <span class="font-serif text-xs font-bold text-[var(--accent-brass)] uppercase tracking-wider">Volet II</span>
                <span class="text-[var(--text-faint)]">•</span>
                <h2 class="font-serif text-xl sm:text-2xl font-normal text-[var(--text-main)]">
                  La Tablée & Le Protocole
                </h2>
              </div>

              <!-- Format de table -->
              <div class="space-y-2.5">
                <label class="block font-serif text-sm font-semibold text-[var(--text-main)]">
                  Nombre de tables à recenser
                </label>
                <div class="grid grid-cols-3 gap-2">
                  <button
                    v-for="opt in [
                      { count: 20, label: '20 tables', desc: 'Sélection' },
                      { count: 35, label: '35 tables', desc: 'Idéal' },
                      { count: 50, label: '50 tables', desc: 'Grand rayon' },
                    ]"
                    :key="opt.count"
                    type="button"
                    :disabled="isLoading"
                    @click="maxRestaurants = opt.count"
                    :class="[
                      maxRestaurants === opt.count
                        ? 'bg-[var(--accent-red)] border border-[var(--accent-red)] text-white font-medium shadow-md'
                        : 'bg-[var(--bg-surface)] border border-[var(--border-main)] text-[var(--text-muted)] hover:border-[var(--accent-brass)] hover:text-[var(--text-main)]',
                      'cursor-pointer transition p-2.5 rounded-2xl text-center flex flex-col items-center justify-center'
                    ]"
                  >
                    <span class="font-serif text-sm sm:text-base font-bold">{{ opt.label }}</span>
                    <span 
                      :class="[
                        maxRestaurants === opt.count ? 'text-white/85' : 'text-[var(--text-faint)]',
                        'text-[10px] font-sans mt-0.5'
                      ]"
                    >
                      {{ opt.desc }}
                    </span>
                  </button>
                </div>
              </div>

              <!-- Note de protocole du suffrage -->
              <div class="p-4 rounded-2xl bg-[var(--bg-surface-inset)] border border-[var(--border-subtle)] text-xs text-[var(--text-muted)] space-y-2">
                <div class="flex items-center gap-2 text-[var(--accent-brass)] font-serif font-bold text-xs uppercase tracking-wider">
                  <span>❧</span>
                  <span>Règlement du vote</span>
                  <span>☙</span>
                </div>
                <p class="leading-relaxed font-serif">
                  Chaque convive disposera de <strong>3 choix pondérés</strong> (3 points pour le 1er, 2 pour le second, 1 pour le troisième). L'ardoise compilera les suffrages en temps réel dès la soumission.
                </p>
              </div>

              <!-- Message d'erreur éventuel -->
              <div v-if="errorMessage" class="rounded-2xl bg-[var(--accent-red-soft)] border border-[var(--accent-red-border)] p-4 flex items-start gap-3 text-[var(--accent-red)] text-sm">
                <AlertCircle class="w-5 h-5 shrink-0 mt-0.5" />
                <div class="space-y-1">
                  <p class="font-medium">{{ errorMessage }}</p>
                  <p class="text-xs opacity-90">Conseil : essayez d'augmenter le temps de marche avec le curseur ou de préciser la ville.</p>
                </div>
              </div>
            </div>

            <!-- Grand Sceau de Cire / Bouton de Soumission -->
            <div class="pt-2">
              <button
                type="submit"
                :disabled="isLoading"
                class="wax-seal-btn w-full rounded-2xl px-6 py-4 text-base sm:text-lg font-serif font-semibold tracking-wide disabled:opacity-70 cursor-pointer flex items-center justify-center gap-3 shadow-xl"
              >
                <template v-if="isLoading">
                  <Loader2 class="w-5 h-5 animate-spin" />
                  <span class="font-sans text-sm sm:text-base">{{ loadingStep }}</span>
                </template>
                <template v-else>
                  <span>Apposer le sceau & ouvrir la table</span>
                  <ArrowRight class="w-5 h-5" />
                </template>
              </button>
            </div>
          </div>
        </div>
      </form>
    </div>

    <!-- Les 3 temps de la brasserie sous forme de cartouches d'honneur -->
    <div class="mt-12 grid grid-cols-1 sm:grid-cols-3 gap-5 text-center">
      <div class="bistro-card-frame p-5 rounded-2xl shadow-xs">
        <span class="block font-serif text-sm font-bold text-[var(--accent-brass)] uppercase tracking-wider mb-1">⚜ I. Conviez la Tablée</span>
        <p class="text-xs text-[var(--text-muted)] font-serif">Partagez l'adresse de votre ardoise avec vos collègues en un clic.</p>
      </div>
      <div class="bistro-card-frame p-5 rounded-2xl shadow-xs">
        <span class="block font-serif text-sm font-bold text-[var(--accent-brass)] uppercase tracking-wider mb-1">⚜ II. Explorez les Cartes</span>
        <p class="text-xs text-[var(--text-muted)] font-serif">Consultez les formules du midi et attribuez vos jetons (3, 2 et 1 pt).</p>
      </div>
      <div class="bistro-card-frame p-5 rounded-2xl shadow-xs">
        <span class="block font-serif text-sm font-bold text-[var(--accent-brass)] uppercase tracking-wider mb-1">⚜ III. À Table !</span>
        <p class="text-xs text-[var(--text-muted)] font-serif">L'adresse plébiscitée triomphe en tête d'ardoise en temps réel.</p>
      </div>
    </div>
  </div>
</template>

