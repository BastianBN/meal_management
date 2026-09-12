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
  <div class="max-w-2xl mx-auto px-4 py-8 sm:py-16">
    <div class="text-center mb-10">
      <div class="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-brand-50 text-brand-600 mb-5 ring-1 ring-brand-200/50">
        <Utensils class="w-7 h-7" />
      </div>
      <h1 class="text-3xl sm:text-4xl font-extrabold tracking-tight text-slate-900 mb-3">
        Où mangeons-nous ce midi ?
      </h1>
      <p class="text-base sm:text-lg text-slate-600 max-w-lg mx-auto leading-relaxed">
        Rassemblez vos collègues, découvrez les cartes et formules du jour autour du bureau, et votez en quelques secondes.
      </p>
    </div>

    <!-- Carte formulaire -->
    <div class="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 sm:p-8">
      <form @submit.prevent="handleCreateSession" class="space-y-6">
        <!-- Champ Adresse -->
        <div>
          <label for="address-input" class="block text-sm font-semibold text-slate-900 mb-2">
            Adresse de départ
          </label>
          <div class="relative rounded-xl shadow-xs">
            <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5 text-slate-400">
              <MapPin class="h-5 w-5" />
            </div>
            <input
              id="address-input"
              v-model="departureAddress"
              type="text"
              required
              :disabled="isLoading"
              placeholder="ex : 12 rue de la Paix, Paris ou Gare Part-Dieu, Lyon"
              class="block w-full rounded-xl border border-slate-300 pl-11 pr-4 py-3 text-slate-900 placeholder:text-slate-400 focus:border-brand-600 focus:ring-2 focus:ring-brand-500/20 focus:outline-none text-base transition sm:text-sm"
            />
          </div>
          <p class="mt-1.5 text-xs text-slate-500">
            Nous localisons les établissements accessibles à pied depuis ce point.
          </p>
        </div>

        <!-- Slider Durée de marche maximale -->
        <div class="bg-slate-50/80 rounded-xl p-4 sm:p-5 border border-slate-200/80">
          <div class="flex items-center justify-between gap-2 mb-3">
            <label for="walk-slider" class="text-sm font-semibold text-slate-900 flex items-center gap-2">
              <Footprints class="w-4 h-4 text-brand-600" />
              <span>Durée de marche maximale</span>
            </label>
            <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-brand-50 border border-brand-200 text-brand-700 font-bold text-sm shadow-xs">
              <Clock class="w-4 h-4 text-brand-600" />
              <span>{{ walkMinutes }} min</span>
              <span class="text-xs font-normal text-brand-600/80">(~{{ radiusMeters >= 1000 ? (radiusMeters / 1000).toFixed(1).replace('.', ',') + ' km' : radiusMeters + ' m' }})</span>
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
                  ? 'text-brand-700 font-bold bg-brand-100/80 ring-1 ring-brand-300'
                  : 'text-slate-500 hover:text-slate-800 hover:bg-slate-200/60',
                'cursor-pointer transition px-2 py-0.5 rounded-md flex items-center gap-1'
              ]"
            >
              <span>{{ preset.label }}</span>
              <span class="text-[10px] text-slate-400 font-normal hidden sm:inline">({{ preset.meters }})</span>
            </button>
          </div>

          <p class="mt-3 text-xs text-slate-500">
            Recherche tous les restaurants situés dans un rayon d'environ <strong class="text-slate-700 font-semibold">{{ radiusMeters >= 1000 ? (radiusMeters / 1000).toFixed(1).replace('.', ',') + ' km' : radiusMeters + ' mètres' }}</strong> (allure dynamique ~6 km/h).
          </p>
        </div>

        <!-- Limite de restaurants & Filtrage par note -->
        <div class="bg-slate-50/80 rounded-xl p-4 sm:p-5 border border-slate-200/80">
          <div class="flex items-center justify-between gap-2 mb-2">
            <label class="text-sm font-semibold text-slate-900 flex items-center gap-2">
              <Star class="w-4 h-4 text-amber-500 fill-amber-500" />
              <span>Nombre de restaurants à retenir</span>
            </label>
            <span class="text-xs font-bold px-2.5 py-0.5 rounded-full bg-amber-50 border border-amber-200 text-amber-800">
              Sélection par note ⭐
            </span>
          </div>

          <div class="grid grid-cols-3 gap-2 mt-2">
            <button
              v-for="opt in [
                { count: 20, label: '20 restos', desc: 'Sélection rapide' },
                { count: 35, label: '35 restos', desc: 'Équilibré (Recommandé)' },
                { count: 50, label: '50 restos', desc: 'Grand choix étendu' },
              ]"
              :key="opt.count"
              type="button"
              :disabled="isLoading"
              @click="maxRestaurants = opt.count"
              :class="[
                maxRestaurants === opt.count
                  ? 'bg-amber-500/10 border-amber-500 text-amber-950 font-bold ring-1 ring-amber-500/40 shadow-xs'
                  : 'bg-white border-slate-200 text-slate-600 hover:border-slate-300 hover:bg-slate-100/50',
                'cursor-pointer transition p-2.5 rounded-xl border text-left flex flex-col justify-center'
              ]"
            >
              <span class="text-xs font-bold">{{ opt.label }}</span>
              <span class="text-[10px] text-slate-500 font-normal mt-0.5">{{ opt.desc }}</span>
            </button>
          </div>
          <p class="mt-2.5 text-xs text-slate-500 leading-relaxed">
            Pour les grands rayons de marche, l'algorithme sélectionne les restaurants <strong>les mieux notés</strong> en couvrant l'ensemble des distances (proches, intermédiaires et destination).
          </p>
        </div>



        <!-- Message d'erreur éventuel -->
        <div v-if="errorMessage" class="rounded-xl bg-red-50 border border-red-200 p-4 flex items-start gap-3 text-red-800 text-sm shadow-xs">
          <AlertCircle class="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
          <div class="space-y-1">
            <p class="font-medium text-red-900">{{ errorMessage }}</p>
            <p class="text-xs text-red-700">Conseil : essayez d'augmenter le temps de marche avec le curseur ci-dessus (ex. 15 ou 20 min) ou de préciser la ville.</p>
          </div>
        </div>

        <!-- Bouton d'action -->
        <button
          type="submit"
          :disabled="isLoading"
          class="w-full inline-flex items-center justify-center gap-2 rounded-xl bg-brand-600 px-6 py-3.5 text-base font-semibold text-white shadow-sm hover:bg-brand-700 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-600 disabled:opacity-75 transition btn-interaction cursor-pointer"
        >
          <template v-if="isLoading">
            <Loader2 class="w-5 h-5 animate-spin" />
            <span>{{ loadingStep }}</span>
          </template>
          <template v-else>
            <span>Créer la session de vote</span>
            <ArrowRight class="w-5 h-5" />
          </template>
        </button>
      </form>
    </div>

    <!-- Récapitulatif du fonctionnement -->
    <div class="mt-8 grid grid-cols-1 sm:grid-cols-3 gap-4 text-center">
      <div class="p-4 rounded-xl bg-slate-100/70 border border-slate-200/60">
        <span class="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">1. Partagez</span>
        <p class="text-xs text-slate-700">Envoyez le lien unique à votre équipe ou vos amis.</p>
      </div>
      <div class="p-4 rounded-xl bg-slate-100/70 border border-slate-200/60">
        <span class="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">2. Votez</span>
        <p class="text-xs text-slate-700">Classez vos 3 restaurants préférés (3, 2 et 1 point).</p>
      </div>
      <div class="p-4 rounded-xl bg-slate-100/70 border border-slate-200/60">
        <span class="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">3. Résultats</span>
        <p class="text-xs text-slate-700">Découvrez le gagnant en direct dès que vous avez voté.</p>
      </div>
    </div>
  </div>
</template>
