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
  <div class="max-w-2xl mx-auto px-4 py-8 sm:py-14">
    <!-- En-tête brasserie & bistrot -->
    <div class="text-center mb-10">
      <div class="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-[#191C22] text-[#D97706] mb-4 border border-[#383F4C] shadow-sm">
        <Utensils class="w-5 h-5" />
      </div>
      <h1 class="font-serif text-4xl sm:text-5xl font-normal tracking-wide text-[#191C22] mb-3 leading-tight">
        Où déjeunons-nous ce midi ?
      </h1>
      <p class="text-sm sm:text-base text-[#64748B] max-w-md mx-auto leading-relaxed">
        Découvrez les cartes, formules du jour et tables recommandées autour du bureau, et votez tous ensemble.
      </p>
    </div>

    <!-- Carte formulaire bistrot épuré -->
    <div class="bg-[#FFFFFF] rounded-2xl border border-[#E2D9CF] p-6 sm:p-9 space-y-6 shadow-sm">
      <form @submit.prevent="handleCreateSession" class="space-y-6">
        <!-- Champ Adresse -->
        <div>
          <label for="address-input" class="block text-xs font-semibold uppercase tracking-wider text-[#191C22] mb-2 font-sans">
            Adresse ou quartier de départ
          </label>
          <div class="relative rounded-xl">
            <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5 text-[#94A3B8]">
              <MapPin class="h-4 w-4" />
            </div>
            <input
              id="address-input"
              v-model="departureAddress"
              type="text"
              required
              :disabled="isLoading"
              placeholder="ex : 12 rue de la Paix, Paris ou 31 allée Christine Pascal, Lyon"
              class="block w-full rounded-xl border border-[#E2D9CF] bg-[#F8F5F2] pl-10 pr-4 py-3 text-[#191C22] placeholder:text-[#94A3B8] focus:border-[#DC2626] focus:bg-[#FFFFFF] focus:ring-1 focus:ring-[#DC2626]/20 focus:outline-none text-sm transition font-normal"
            />
          </div>
          <p class="mt-1.5 text-xs text-[#64748B]">
            Tous les bistrots et restaurants accessibles à pied seront repérés autour de cette adresse.
          </p>
        </div>

        <!-- Slider Durée de marche maximale -->
        <div class="bg-[#F8F5F2] rounded-xl p-4 sm:p-5 border border-[#E2D9CF]">
          <div class="flex items-center justify-between gap-2 mb-3">
            <label for="walk-slider" class="text-xs font-semibold uppercase tracking-wider text-[#191C22] flex items-center gap-2 font-sans">
              <Footprints class="w-3.5 h-3.5 text-[#DC2626]" />
              <span>Périmètre de marche</span>
            </label>
            <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#FFFFFF] border border-[#E2D9CF] text-[#191C22] font-medium text-xs shadow-xs">
              <Clock class="w-3.5 h-3.5 text-[#D97706]" />
              <span class="font-semibold">{{ walkMinutes }} min</span>
              <span class="text-xs text-[#64748B]">(~{{ radiusMeters >= 1000 ? (radiusMeters / 1000).toFixed(1).replace('.', ',') + ' km' : radiusMeters + ' m' }})</span>
            </div>
          </div>

          <div class="py-2">
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
          <div class="flex justify-between items-center text-xs mt-1">
            <button
              v-for="preset in durationPresets"
              :key="preset.minutes"
              type="button"
              :disabled="isLoading"
              @click="walkMinutes = preset.minutes"
              :class="[
                walkMinutes === preset.minutes
                  ? 'text-[#F8FAFC] font-medium bg-[#191C22] border border-[#383F4C] shadow-xs'
                  : 'text-[#64748B] hover:text-[#191C22] hover:bg-[#FFFFFF]',
                'cursor-pointer transition px-2.5 py-1 rounded-lg flex items-center gap-1'
              ]"
            >
              <span>{{ preset.label }}</span>
              <span class="text-[10px] text-[#94A3B8] font-normal hidden sm:inline">({{ preset.meters }})</span>
            </button>
          </div>

          <p class="mt-3 text-xs text-[#64748B]">
            Rayon de marche : environ <strong class="text-[#191C22] font-medium">{{ radiusMeters >= 1000 ? (radiusMeters / 1000).toFixed(1).replace('.', ',') + ' km' : radiusMeters + ' mètres' }}</strong> (allure dynamique ~6 km/h).
          </p>
        </div>

        <!-- Limite de restaurants & Filtrage par note -->
        <div class="bg-[#F8F5F2] rounded-xl p-4 sm:p-5 border border-[#E2D9CF]">
          <div class="flex items-center justify-between gap-2 mb-2">
            <label class="text-xs font-semibold uppercase tracking-wider text-[#191C22] flex items-center gap-2 font-sans">
              <Star class="w-3.5 h-3.5 text-[#D97706] fill-[#D97706]" />
              <span>Sélection d'adresses</span>
            </label>
            <span class="text-[11px] font-medium px-2 py-0.5 rounded-full bg-[#FFFBEB] text-[#92400E] border border-[#FDE68A]">
              Triées par note ⭐
            </span>
          </div>

          <div class="grid grid-cols-3 gap-2 mt-2">
            <button
              v-for="opt in [
                { count: 20, label: '20 tables', desc: 'Sélection rapide' },
                { count: 35, label: '35 tables', desc: 'Recommandé' },
                { count: 50, label: '50 tables', desc: 'Grand choix étendu' },
              ]"
              :key="opt.count"
              type="button"
              :disabled="isLoading"
              @click="maxRestaurants = opt.count"
              :class="[
                maxRestaurants === opt.count
                  ? 'bg-[#191C22] border border-[#383F4C] text-[#F8FAFC] font-medium shadow-xs'
                  : 'bg-[#FFFFFF] border border-[#E2D9CF] text-[#475569] hover:border-[#CBD5E1] hover:bg-[#F8F5F2]',
                'cursor-pointer transition p-2.5 rounded-xl text-left flex flex-col justify-center'
              ]"
            >
              <span class="text-xs font-medium">{{ opt.label }}</span>
              <span 
                :class="[
                  maxRestaurants === opt.count ? 'text-[#94A3B8]' : 'text-[#64748B]',
                  'text-[10px] font-normal mt-0.5'
                ]"
              >
                {{ opt.desc }}
              </span>
            </button>
          </div>
          <p class="mt-2.5 text-xs text-[#64748B] leading-relaxed">
            Pour les grands trajets, les tables les <strong>mieux notées</strong> sont réparties équitablement sur tout le parcours.
          </p>
        </div>

        <!-- Message d'erreur éventuel -->
        <div v-if="errorMessage" class="rounded-xl bg-[#FEF2F2] border border-[#FECACA] p-4 flex items-start gap-3 text-[#DC2626] text-sm">
          <AlertCircle class="w-4 h-4 shrink-0 mt-0.5" />
          <div class="space-y-1">
            <p class="font-medium">{{ errorMessage }}</p>
            <p class="text-xs text-[#64748B]">Conseil : essayez d'augmenter le temps de marche avec le curseur ci-dessus ou de préciser la ville.</p>
          </div>
        </div>

        <!-- Bouton d'action principal Rouge Bistrot -->
        <button
          type="submit"
          :disabled="isLoading"
          class="w-full inline-flex items-center justify-center gap-2 rounded-xl bg-[#DC2626] hover:bg-[#B91C1C] px-6 py-3.5 text-sm sm:text-base font-medium text-white tracking-wide disabled:opacity-70 transition cursor-pointer shadow-sm"
        >
          <template v-if="isLoading">
            <Loader2 class="w-4 h-4 animate-spin" />
            <span>{{ loadingStep }}</span>
          </template>
          <template v-else>
            <span>Dresser l'ardoise de vote</span>
            <ArrowRight class="w-4 h-4" />
          </template>
        </button>
      </form>
    </div>

    <!-- Récapitulatif simple et sobre -->
    <div class="mt-12 grid grid-cols-1 sm:grid-cols-3 gap-4 text-center">
      <div class="p-4 rounded-xl bg-[#FFFFFF]/80 border border-[#E2D9CF] shadow-2xs">
        <span class="block text-[10px] font-semibold text-[#64748B] uppercase tracking-widest mb-1 font-sans">1. Invitez</span>
        <p class="text-xs text-[#475569]">Partagez l'ardoise avec vos collègues de table.</p>
      </div>
      <div class="p-4 rounded-xl bg-[#FFFFFF]/80 border border-[#E2D9CF] shadow-2xs">
        <span class="block text-[10px] font-semibold text-[#64748B] uppercase tracking-widest mb-1 font-sans">2. Choisissez</span>
        <p class="text-xs text-[#475569]">Attribuez vos 3 préférences (3, 2 et 1 point).</p>
      </div>
      <div class="p-4 rounded-xl bg-[#FFFFFF]/80 border border-[#E2D9CF] shadow-2xs">
        <span class="block text-[10px] font-semibold text-[#64748B] uppercase tracking-widest mb-1 font-sans">3. À table !</span>
        <p class="text-xs text-[#475569]">Découvrez la table gagnante en direct.</p>
      </div>
    </div>
  </div>
</template>

