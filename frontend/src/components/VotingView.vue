<script setup>
import { ref, computed } from 'vue';
import RestaurantCard from './RestaurantCard.vue';

import RestaurantsMap from './RestaurantsMap.vue';
import { submitVote } from '../api';
import { Share2, MapPin, Footprints, AlertCircle, CheckCircle2, User, Lock, Map as MapIcon, List, Star, Search, Filter } from 'lucide-vue-next';

const props = defineProps({
  session: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(['voteSubmitted']);

const voterName = ref('');
const firstChoiceId = ref(null);
const secondChoiceId = ref(null);
const thirdChoiceId = ref(null);
const isSubmitting = ref(false);
const errorMessage = ref('');
const copySuccess = ref(false);
const showMap = ref(true);

const sortBy = ref('rating'); // 'rating' or 'distance'
const selectedCuisine = ref('ALL');
const onlyWithMenu = ref(false);
const searchQuery = ref('');

const restaurants = computed(() => props.session.restaurants || []);

// Liste des cuisines disponibles
const availableCuisines = computed(() => {
  const set = new Set();
  for (const r of restaurants.value) {
    if (r.cuisine) set.add(r.cuisine);
  }
  return Array.from(set).sort();
});

// Filtrage et tri réactifs
const filteredRestaurants = computed(() => {
  let list = [...restaurants.value];

  // Recherche texte
  const q = searchQuery.value.trim().toLowerCase();
  if (q) {
    list = list.filter(r => 
      r.name.toLowerCase().includes(q) || 
      (r.address && r.address.toLowerCase().includes(q)) ||
      (r.cuisine && r.cuisine.toLowerCase().includes(q))
    );
  }

  // Filtre cuisine
  if (selectedCuisine.value !== 'ALL') {
    list = list.filter(r => r.cuisine === selectedCuisine.value);
  }

  // Filtre carte / menu
  if (onlyWithMenu.value) {
    list = list.filter(r => 
      (r.lunch_formulas && r.lunch_formulas.length > 0) || 
      r.menu_url || 
      (r.menu_summary && !r.menu_summary.includes('consultables sur place'))
    );
  }

  // Tri
  if (sortBy.value === 'rating') {
    list.sort((a, b) => {
      const rateA = Number(a.rating) || 0;
      const rateB = Number(b.rating) || 0;
      if (rateB !== rateA) return rateB - rateA;
      return a.distance_meters - b.distance_meters;
    });
  } else {
    list.sort((a, b) => a.distance_meters - b.distance_meters);
  }

  return list;
});


// Attribution d'un rang (1, 2 ou 3) à un restaurant
function handleToggleRank({ restaurantId, rank }) {
  if (rank === 1) {
    if (firstChoiceId.value === restaurantId) {
      firstChoiceId.value = null;
    } else {
      if (secondChoiceId.value === restaurantId) secondChoiceId.value = null;
      if (thirdChoiceId.value === restaurantId) thirdChoiceId.value = null;
      firstChoiceId.value = restaurantId;
    }
  } else if (rank === 2) {
    if (secondChoiceId.value === restaurantId) {
      secondChoiceId.value = null;
    } else {
      if (firstChoiceId.value === restaurantId) firstChoiceId.value = null;
      if (thirdChoiceId.value === restaurantId) thirdChoiceId.value = null;
      secondChoiceId.value = restaurantId;
    }
  } else if (rank === 3) {
    if (thirdChoiceId.value === restaurantId) {
      thirdChoiceId.value = null;
    } else {
      if (firstChoiceId.value === restaurantId) firstChoiceId.value = null;
      if (secondChoiceId.value === restaurantId) secondChoiceId.value = null;
      thirdChoiceId.value = restaurantId;
    }
  }
}

function getRestaurantRank(restaurantId) {
  if (firstChoiceId.value === restaurantId) return 1;
  if (secondChoiceId.value === restaurantId) return 2;
  if (thirdChoiceId.value === restaurantId) return 3;
  return null;
}

const firstChoiceName = computed(() => {
  return restaurants.value.find(r => r.id === firstChoiceId.value)?.name;
});

const secondChoiceName = computed(() => {
  return restaurants.value.find(r => r.id === secondChoiceId.value)?.name;
});

const thirdChoiceName = computed(() => {
  return restaurants.value.find(r => r.id === thirdChoiceId.value)?.name;
});

const canSubmit = computed(() => {
  return voterName.value.trim().length >= 2 && firstChoiceId.value !== null;
});

const submitButtonLabel = computed(() => {
  if (!voterName.value.trim()) return "Saisissez votre prénom pour voter";
  if (!firstChoiceId.value) return "Choisissez votre 1er choix (3 pts)";
  return "Valider mon vote (Définitif)";
});

async function copyShareLink() {
  const url = window.location.href;
  try {
    await navigator.clipboard.writeText(url);
    copySuccess.value = true;
    setTimeout(() => {
      copySuccess.value = false;
    }, 3000);
  } catch (err) {
    prompt("Copiez ce lien pour inviter vos collègues :", url);
  }
}

async function handleVoteSubmit() {
  const name = voterName.value.trim();
  if (!name) {
    errorMessage.value = "Veuillez renseigner votre prénom ou nom pour voter.";
    return;
  }

  if (!firstChoiceId.value) {
    errorMessage.value = "Veuillez désigner au moins votre 1er choix (3 points) parmi les restaurants.";
    return;
  }

  isSubmitting.value = true;
  errorMessage.value = '';

  try {
    const leaderboard = await submitVote(props.session.id, {
      voterName: name,
      firstChoiceId: firstChoiceId.value,
      secondChoiceId: secondChoiceId.value,
      thirdChoiceId: thirdChoiceId.value,
    });

    localStorage.setItem(`meal_voter_${props.session.id}`, name);
    localStorage.setItem(`meal_choices_${props.session.id}`, JSON.stringify({
      first: firstChoiceName.value,
      second: secondChoiceName.value,
      third: thirdChoiceName.value,
    }));
    emit('voteSubmitted', { leaderboard, voterName: name });
  } catch (err) {
    errorMessage.value = err.message || "Erreur lors de l'enregistrement de votre vote.";
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<template>
  <div class="space-y-6">
    <!-- En-tête de session : Adresse, Rayon, Partage -->
    <div class="bg-white rounded-2xl border border-slate-200 p-5 sm:p-6 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <div class="flex items-center gap-2 text-xs font-semibold text-orange-700 mb-1">
          <MapPin class="w-4 h-4 text-orange-600 shrink-0" />
          <span>Point de départ du groupe :</span>
        </div>
        <h2 class="text-lg sm:text-xl font-extrabold text-slate-900 leading-snug">
          {{ session.departure_address }}
        </h2>
        <p class="text-xs text-slate-500 mt-1 flex items-center gap-2 flex-wrap">
          <span class="inline-flex items-center gap-1 font-medium text-slate-700">
            <Footprints class="w-3.5 h-3.5 text-emerald-600" />
            Rayon : {{ session.radius_meters >= 1000 ? (session.radius_meters / 1000).toFixed(1).replace('.', ',') + ' km' : session.radius_meters + ' mètres' }} (~{{ Math.round(session.radius_meters / 100) }} min max à pied)
          </span>
          <span>•</span>
          <span class="font-medium text-slate-700">{{ restaurants.length }} restaurants découverts</span>
        </p>
      </div>

      <!-- Boutons Partager & Bascule Carte -->
      <div class="flex items-center gap-2 shrink-0">
        <button
          type="button"
          @click="showMap = !showMap"
          class="inline-flex items-center gap-1.5 px-3.5 py-2.5 rounded-xl border border-slate-300 hover:border-slate-400 bg-white hover:bg-slate-50 text-slate-700 text-xs font-bold transition btn-interaction cursor-pointer"
        >
          <MapIcon v-if="!showMap" class="w-4 h-4 text-slate-500" />
          <List v-else class="w-4 h-4 text-slate-500" />
          <span>{{ showMap ? 'Masquer la carte' : 'Afficher la carte' }}</span>
        </button>

        <button
          type="button"
          @click="copyShareLink"
          class="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl border border-orange-200 hover:border-orange-300 bg-orange-50/80 hover:bg-orange-100 text-orange-800 text-xs font-bold transition btn-interaction cursor-pointer"
        >
          <CheckCircle2 v-if="copySuccess" class="w-4 h-4 text-emerald-600" />
          <Share2 v-else class="w-4 h-4 text-orange-600" />
          <span>{{ copySuccess ? 'Lien copié !' : 'Partager le vote' }}</span>
        </button>
      </div>
    </div>

    <!-- Carte interactive Leaflet OpenStreetMap avec les épingles -->
    <div v-show="showMap" class="transition-all duration-300">
      <RestaurantsMap
        :departure="{
          address: session.departure_address,
          latitude: session.latitude,
          longitude: session.longitude,
          radius_meters: session.radius_meters
        }"
        :restaurants="filteredRestaurants"
        :selected-rankings="{
          firstChoiceId,
          secondChoiceId,
          thirdChoiceId
        }"
        @toggle-rank="handleToggleRank"
      />
    </div>


    <!-- Barre d'action fixe et bien visible pour voter -->
    <div class="bg-white rounded-2xl border-2 border-slate-200 p-5 shadow-md sticky top-4 z-20 backdrop-blur-md bg-white/95">
      <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <!-- Champ nom du votant -->
        <div class="w-full lg:w-72 shrink-0">
          <label for="voter-name" class="block text-xs font-bold text-slate-800 mb-1">
            Votre prénom ou nom <span class="text-red-500">*</span>
          </label>
          <div class="relative rounded-xl shadow-xs">
            <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">
              <User class="h-4 w-4" />
            </div>
            <input
              id="voter-name"
              v-model="voterName"
              type="text"
              required
              placeholder="ex : Marc, Camille..."
              class="block w-full rounded-xl border-2 border-slate-300 pl-9 pr-3 py-2 text-sm font-semibold text-slate-900 placeholder:text-slate-400 placeholder:font-normal focus:border-orange-600 focus:ring-2 focus:ring-orange-500/20 focus:outline-none"
            />
          </div>
        </div>

        <!-- Récapitulatif visuel des 3 choix -->
        <div class="flex-1 flex flex-wrap items-center gap-2 text-xs">
          <!-- Choix 1 -->
          <div 
            :class="[
              firstChoiceId ? 'bg-amber-100/70 border-amber-400 text-amber-950 font-bold' : 'bg-slate-50 border-slate-200 text-slate-400',
              'px-3 py-2 rounded-xl border flex items-center gap-2 transition'
            ]"
          >
            <span class="w-5 h-5 rounded-full bg-amber-500 text-white flex items-center justify-center font-extrabold text-[10px] shadow-xs">1</span>
            <span class="truncate max-w-[130px] sm:max-w-[170px]">{{ firstChoiceName || '1er choix (+3 pts)' }}</span>
          </div>

          <!-- Choix 2 -->
          <div 
            :class="[
              secondChoiceId ? 'bg-slate-200/80 border-slate-400 text-slate-900 font-bold' : 'bg-slate-50 border-slate-200 text-slate-400',
              'px-3 py-2 rounded-xl border flex items-center gap-2 transition'
            ]"
          >
            <span class="w-5 h-5 rounded-full bg-slate-700 text-white flex items-center justify-center font-extrabold text-[10px] shadow-xs">2</span>
            <span class="truncate max-w-[130px] sm:max-w-[170px]">{{ secondChoiceName || '2e choix (+2 pts)' }}</span>
          </div>

          <!-- Choix 3 -->
          <div 
            :class="[
              thirdChoiceId ? 'bg-amber-900/15 border-amber-700 text-amber-950 font-bold' : 'bg-slate-50 border-slate-200 text-slate-400',
              'px-3 py-2 rounded-xl border flex items-center gap-2 transition'
            ]"
          >
            <span class="w-5 h-5 rounded-full bg-amber-900 text-white flex items-center justify-center font-extrabold text-[10px] shadow-xs">3</span>
            <span class="truncate max-w-[130px] sm:max-w-[170px]">{{ thirdChoiceName || '3e choix (+1 pt)' }}</span>
          </div>
        </div>

        <!-- Bouton de validation bien visible -->
        <div class="shrink-0 flex flex-col items-stretch lg:items-end">
          <button
            type="button"
            :disabled="isSubmitting || !canSubmit"
            @click="handleVoteSubmit"
            :class="[
              canSubmit
                ? 'bg-orange-600 hover:bg-orange-700 active:bg-orange-800 text-white shadow-md ring-2 ring-orange-500/30'
                : 'bg-slate-200 text-slate-400 cursor-not-allowed border border-slate-300',
              'px-6 py-3 rounded-xl font-extrabold text-sm transition btn-interaction flex items-center justify-center gap-2 cursor-pointer'
            ]"
          >
            <Lock class="w-4 h-4 shrink-0" />
            <span>{{ isSubmitting ? 'Enregistrement...' : submitButtonLabel }}</span>
          </button>
          <span class="text-[11px] text-slate-500 mt-1 text-center lg:text-right font-medium">
            Vote définitif • Enregistrement irrévocable
          </span>
        </div>
      </div>

      <!-- Erreur éventuelle -->
      <div v-if="errorMessage" class="mt-3 p-3 rounded-xl bg-red-50 border border-red-200 text-red-800 text-xs flex items-center gap-2 font-medium">
        <AlertCircle class="w-4 h-4 text-red-600 shrink-0" />
        <span>{{ errorMessage }}</span>
      </div>
    </div>

    <!-- Barre de filtrage & tri -->
    <div class="bg-white rounded-2xl border border-slate-200 p-4 sm:p-5 shadow-xs space-y-3">
      <div class="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        <!-- Recherche textuelle -->
        <div class="relative flex-1">
          <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5 text-slate-400">
            <Search class="w-4 h-4" />
          </div>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Rechercher par nom, cuisine ou adresse..."
            class="block w-full rounded-xl border border-slate-200 pl-10 pr-3 py-2 text-sm font-medium text-slate-900 placeholder:text-slate-400 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 focus:outline-none transition"
          />
        </div>

        <!-- Bascule de Tri : Note vs Distance -->
        <div class="flex items-center gap-1.5 shrink-0 bg-slate-100/90 p-1 rounded-xl border border-slate-200/80">
          <button
            type="button"
            @click="sortBy = 'rating'"
            :class="[
              sortBy === 'rating' ? 'bg-white text-amber-950 font-bold shadow-xs ring-1 ring-slate-200' : 'text-slate-600 hover:text-slate-900',
              'px-3 py-1.5 rounded-lg text-xs transition flex items-center gap-1.5 cursor-pointer'
            ]"
          >
            <Star class="w-3.5 h-3.5 text-amber-500 fill-amber-400" />
            <span>Mieux notés ⭐</span>
          </button>
          <button
            type="button"
            @click="sortBy = 'distance'"
            :class="[
              sortBy === 'distance' ? 'bg-white text-slate-900 font-bold shadow-xs ring-1 ring-slate-200' : 'text-slate-600 hover:text-slate-900',
              'px-3 py-1.5 rounded-lg text-xs transition flex items-center gap-1.5 cursor-pointer'
            ]"
          >
            <Footprints class="w-3.5 h-3.5 text-emerald-600" />
            <span>Plus proches</span>
          </button>
        </div>
      </div>

      <!-- Filtres secondaires : Cuisines, Formules, Compteur -->
      <div class="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-slate-100 text-xs">
        <div class="flex flex-wrap items-center gap-2">
          <!-- Filtre Cuisine -->
          <div class="flex items-center gap-1.5 text-slate-600 font-medium">
            <Filter class="w-3.5 h-3.5 text-slate-400" />
            <span>Cuisine :</span>
            <select
              v-model="selectedCuisine"
              class="rounded-lg border border-slate-200 bg-white px-2.5 py-1 text-xs font-semibold text-slate-800 focus:border-orange-500 focus:outline-none cursor-pointer"
            >
              <option value="ALL">Toutes les cuisines ({{ restaurants.length }})</option>
              <option v-for="c in availableCuisines" :key="c" :value="c">{{ c }}</option>
            </select>
          </div>

          <!-- Toggle avec formule/menu -->
          <button
            type="button"
            @click="onlyWithMenu = !onlyWithMenu"
            :class="[
              onlyWithMenu 
                ? 'bg-emerald-50 text-emerald-800 border-emerald-300 font-bold ring-1 ring-emerald-300' 
                : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100',
              'px-3 py-1 rounded-lg border text-xs transition cursor-pointer flex items-center gap-1.5'
            ]"
          >
            <span>Avec carte / menu en ligne</span>
          </button>
        </div>

        <span class="text-slate-500 font-medium text-xs">
          <strong>{{ filteredRestaurants.length }}</strong> sur {{ restaurants.length }} restaurants affichés
        </span>
      </div>
    </div>

    <!-- Grille des cartes de restaurants -->
    <div>
      <div class="flex items-center justify-between mb-4">
        <div>
          <h3 class="text-lg font-extrabold text-slate-900">
            Établissements accessibles à pied
          </h3>
          <p class="text-xs text-slate-500">
            Attribuez vos 3 préférences avec les boutons 1er (+3 pts), 2e (+2 pts) ou 3e (+1 pt)
          </p>
        </div>
      </div>

      <!-- État vide si filtre trop restrictif -->
      <div v-if="filteredRestaurants.length === 0" class="rounded-2xl border border-slate-200 bg-slate-50/50 p-8 text-center text-slate-600 space-y-2">
        <p class="font-semibold text-slate-800">Aucun restaurant ne correspond à votre filtre.</p>
        <p class="text-xs text-slate-500">Essayez de réinitialiser la recherche ou de sélectionner "Toutes les cuisines".</p>
        <button
          type="button"
          @click="searchQuery = ''; selectedCuisine = 'ALL'; onlyWithMenu = false;"
          class="mt-2 inline-flex items-center px-3 py-1.5 rounded-lg bg-white border border-slate-300 text-xs font-bold text-slate-700 hover:bg-slate-50 cursor-pointer"
        >
          Réinitialiser les filtres
        </button>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <RestaurantCard
          v-for="r in filteredRestaurants"
          :key="r.id"
          :restaurant="r"
          :current-rank="getRestaurantRank(r.id)"
          @toggle-rank="handleToggleRank"
        />
      </div>
    </div>
  </div>
</template>

