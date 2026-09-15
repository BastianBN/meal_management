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
    <!-- En-tête éditorial poétique -->
    <div class="text-center mb-10">
      <div class="inline-flex items-center justify-center w-10 h-10 rounded-xl bg-[#FFFDF9] text-[#B85B43] mb-4 border border-[#E8E3DA]">
        <Utensils class="w-4 h-4" />
      </div>
      <h1 class="font-serif text-3xl sm:text-5xl font-normal tracking-wide text-[#292524] mb-3 leading-tight">
        Où déjeunons-nous ce midi ?
      </h1>
      <p class="text-sm sm:text-base text-[#78716C] max-w-md mx-auto leading-relaxed">
        Découvrez les cartes, formules du jour et avis autour du bureau, et choisissez ensemble en toute sérénité.
      </p>
    </div>

    <!-- Carte formulaire en papier washi -->
    <div class="bg-[#FFFDF9] rounded-2xl border border-[#E8E3DA] p-6 sm:p-9 space-y-6">
      <form @submit.prevent="handleCreateSession" class="space-y-6">
        <!-- Champ Adresse -->
        <div>
          <label for="address-input" class="block text-xs font-semibold uppercase tracking-wider text-[#292524] mb-2">
            Adresse de départ
          </label>
          <div class="relative rounded-xl">
            <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5 text-[#A8A29E]">
              <MapPin class="h-4 w-4" />
            </div>
            <input
              id="address-input"
              v-model="departureAddress"
              type="text"
              required
              :disabled="isLoading"
              placeholder="ex : 12 rue de la Paix, Paris ou 31 allée Christine Pascal, Lyon"
              class="block w-full rounded-xl border border-[#E8E3DA] bg-[#FAF8F5] pl-10 pr-4 py-3 text-[#292524] placeholder:text-[#A8A29E] focus:border-[#B85B43] focus:bg-[#FFFDF9] focus:ring-1 focus:ring-[#B85B43]/20 focus:outline-none text-sm transition font-normal"
            />
          </div>
          <p class="mt-1.5 text-xs text-[#78716C]">
            Tous les restaurants accessibles à pied seront repérés autour de cette adresse.
          </p>
        </div>

        <!-- Slider Durée de marche maximale -->
        <div class="bg-[#FAF8F5] rounded-xl p-4 sm:p-5 border border-[#E8E3DA]">
          <div class="flex items-center justify-between gap-2 mb-3">
            <label for="walk-slider" class="text-xs font-semibold uppercase tracking-wider text-[#292524] flex items-center gap-2">
              <Footprints class="w-3.5 h-3.5 text-[#B85B43]" />
              <span>Temps de marche maximal</span>
            </label>
            <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#FFFDF9] border border-[#E8E3DA] text-[#292524] font-medium text-xs">
              <Clock class="w-3.5 h-3.5 text-[#B85B43]" />
              <span>{{ walkMinutes }} min</span>
              <span class="text-xs text-[#78716C]">(~{{ radiusMeters >= 1000 ? (radiusMeters / 1000).toFixed(1).replace('.', ',') + ' km' : radiusMeters + ' m' }})</span>
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
                  ? 'text-[#B85B43] font-medium bg-[#FFFDF9] border border-[#B85B43]'
                  : 'text-[#78716C] hover:text-[#292524] hover:bg-[#FFFDF9]',
                'cursor-pointer transition px-2.5 py-1 rounded-lg flex items-center gap-1'
              ]"
            >
              <span>{{ preset.label }}</span>
              <span class="text-[10px] text-[#A8A29E] font-normal hidden sm:inline">({{ preset.meters }})</span>
            </button>
          </div>

          <p class="mt-3 text-xs text-[#78716C]">
            Rayon de marche : environ <strong class="text-[#292524] font-medium">{{ radiusMeters >= 1000 ? (radiusMeters / 1000).toFixed(1).replace('.', ',') + ' km' : radiusMeters + ' mètres' }}</strong> (allure dynamique ~6 km/h).
          </p>
        </div>

        <!-- Limite de restaurants & Filtrage par note -->
        <div class="bg-[#FAF8F5] rounded-xl p-4 sm:p-5 border border-[#E8E3DA]">
          <div class="flex items-center justify-between gap-2 mb-2">
            <label class="text-xs font-semibold uppercase tracking-wider text-[#292524] flex items-center gap-2">
              <Star class="w-3.5 h-3.5 text-amber-600 fill-amber-500" />
              <span>Sélection de restaurants</span>
            </label>
            <span class="text-[11px] font-medium px-2 py-0.5 rounded-full bg-[#FEF3C7] text-[#78350F] border border-[#F59E0B]/30">
              Triés par note ⭐
            </span>
          </div>

          <div class="grid grid-cols-3 gap-2 mt-2">
            <button
              v-for="opt in [
                { count: 20, label: '20 restos', desc: 'Sélection rapide' },
                { count: 35, label: '35 restos', desc: 'Recommandé' },
                { count: 50, label: '50 restos', desc: 'Grand choix étendu' },
              ]"
              :key="opt.count"
              type="button"
              :disabled="isLoading"
              @click="maxRestaurants = opt.count"
              :class="[
                maxRestaurants === opt.count
                  ? 'bg-[#FFFDF9] border border-[#B85B43] text-[#B85B43] font-medium'
                  : 'bg-[#FAF8F5] border border-[#E8E3DA] text-[#57534E] hover:border-[#DDD7CD] hover:bg-[#FFFDF9]',
                'cursor-pointer transition p-2.5 rounded-xl text-left flex flex-col justify-center'
              ]"
            >
              <span class="text-xs font-medium">{{ opt.label }}</span>
              <span class="text-[10px] text-[#78716C] font-normal mt-0.5">{{ opt.desc }}</span>
            </button>
          </div>
          <p class="mt-2.5 text-xs text-[#78716C] leading-relaxed">
            Pour les grands trajets, les restaurants les <strong>mieux notés</strong> sont répartis sur tout le parcours (proche, mi-chemin et destination).
          </p>
        </div>

        <!-- Message d'erreur éventuel -->
        <div v-if="errorMessage" class="rounded-xl bg-[#FBF4F1] border border-[#E8C7BE] p-4 flex items-start gap-3 text-[#B85B43] text-sm">
          <AlertCircle class="w-4 h-4 shrink-0 mt-0.5" />
          <div class="space-y-1">
            <p class="font-medium">{{ errorMessage }}</p>
            <p class="text-xs text-[#78716C]">Conseil : essayez d'augmenter le temps de marche avec le curseur ci-dessus ou de préciser la ville.</p>
          </div>
        </div>

        <!-- Bouton d'action principal -->
        <button
          type="submit"
          :disabled="isLoading"
          class="w-full inline-flex items-center justify-center gap-2 rounded-xl bg-[#B85B43] hover:bg-[#9E4C36] px-6 py-3.5 text-sm sm:text-base font-medium text-white tracking-wide disabled:opacity-70 transition cursor-pointer"
        >
          <template v-if="isLoading">
            <Loader2 class="w-4 h-4 animate-spin" />
            <span>{{ loadingStep }}</span>
          </template>
          <template v-else>
            <span>Créer la session de vote</span>
            <ArrowRight class="w-4 h-4" />
          </template>
        </button>
      </form>
    </div>

    <!-- Récapitulatif simple et sobre -->
    <div class="mt-12 grid grid-cols-1 sm:grid-cols-3 gap-4 text-center">
      <div class="p-4 rounded-xl bg-[#FFFDF9]/70 border border-[#E8E3DA]">
        <span class="block text-[10px] font-semibold text-[#78716C] uppercase tracking-widest mb-1">1. Invitez</span>
        <p class="text-xs text-[#57534E]">Partagez le lien avec vos collègues ou amis.</p>
      </div>
      <div class="p-4 rounded-xl bg-[#FFFDF9]/70 border border-[#E8E3DA]">
        <span class="block text-[10px] font-semibold text-[#78716C] uppercase tracking-widest mb-1">2. Votez</span>
        <p class="text-xs text-[#57534E]">Classez vos 3 préférences (3, 2 et 1 point).</p>
      </div>
      <div class="p-4 rounded-xl bg-[#FFFDF9]/70 border border-[#E8E3DA]">
        <span class="block text-[10px] font-semibold text-[#78716C] uppercase tracking-widest mb-1">3. Résultats</span>
        <p class="text-xs text-[#57534E]">Découvrez en direct le vainqueur du déjeuner.</p>
      </div>
    </div>
  </div>
</template>

