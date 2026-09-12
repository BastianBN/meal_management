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
    <div class="bg-white/90 backdrop-blur-sm rounded-2xl border border-[#E7E2D9] p-5 sm:p-6 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <div class="flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-[#C2410C] mb-1">
          <MapPin class="w-3.5 h-3.5 text-[#C2410C] shrink-0" />
          <span>Point de départ</span>
        </div>
        <h2 class="font-serif text-xl sm:text-2xl font-bold text-[#1C1917] tracking-tight leading-snug">
          {{ session.departure_address }}
        </h2>
        <p class="text-xs text-[#78716C] mt-1.5 flex items-center gap-2 flex-wrap">
          <span class="inline-flex items-center gap-1.5 font-semibold text-[#1C1917] bg-[#F3EFEA] px-2.5 py-0.5 rounded-md border border-[#E7E2D9]">
            <Footprints class="w-3.5 h-3.5 text-emerald-700" />
            Rayon : {{ session.radius_meters >= 1000 ? (session.radius_meters / 1000).toFixed(1).replace('.', ',') + ' km' : session.radius_meters + ' m' }} (~{{ Math.round(session.radius_meters / 100) }} min à pied)
          </span>
          <span class="text-[#D5CEC2]">•</span>
          <span class="font-semibold text-[#44403C]">{{ restaurants.length }} restaurants sélectionnés</span>
        </p>
      </div>

      <!-- Boutons Partager & Bascule Carte -->
      <div class="flex items-center gap-2 shrink-0">
        <button
          type="button"
          @click="showMap = !showMap"
          class="inline-flex items-center gap-1.5 px-3.5 py-2.5 rounded-xl border border-[#D5CEC2] hover:border-[#1C1917] bg-[#FAF7F2] hover:bg-white text-[#44403C] hover:text-[#1C1917] text-xs font-bold transition cursor-pointer"
        >
          <MapIcon v-if="!showMap" class="w-4 h-4 text-[#78716C]" />
          <List v-else class="w-4 h-4 text-[#78716C]" />
          <span>{{ showMap ? 'Masquer la carte' : 'Afficher la carte' }}</span>
        </button>

        <button
          type="button"
          @click="copyShareLink"
          class="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl border border-[#EA580C]/30 hover:border-[#EA580C] bg-[#FFF7ED] hover:bg-[#FFEDD5] text-[#9A3412] text-xs font-bold transition shadow-2xs cursor-pointer"
        >
          <CheckCircle2 v-if="copySuccess" class="w-4 h-4 text-emerald-700" />
          <Share2 v-else class="w-4 h-4 text-[#C2410C]" />
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
    <div class="bg-[#FAF7F2]/95 backdrop-blur-md rounded-2xl border border-[#D5CEC2] p-4 sm:p-5 shadow-md sticky top-4 z-20">
      <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <!-- Champ nom du votant -->
        <div class="w-full lg:w-72 shrink-0">
          <label for="voter-name" class="block text-xs font-bold text-[#1C1917] mb-1">
            Votre prénom ou nom <span class="text-[#C2410C]">*</span>
          </label>
          <div class="relative rounded-xl shadow-2xs">
            <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-[#78716C]">
              <User class="h-4 w-4" />
            </div>
            <input
              id="voter-name"
              v-model="voterName"
              type="text"
              required
              placeholder="ex : Marc, Camille..."
              class="block w-full rounded-xl border border-[#D5CEC2] bg-white pl-9 pr-3 py-2 text-sm font-semibold text-[#1C1917] placeholder:text-[#A8A29E] placeholder:font-normal focus:border-[#C2410C] focus:ring-2 focus:ring-[#C2410C]/20 focus:outline-none transition"
            />
          </div>
        </div>

        <!-- Récapitulatif visuel des 3 choix -->
        <div class="flex-1 flex flex-wrap items-center gap-2 text-xs">
          <!-- Choix 1 -->
          <div 
            :class="[
              firstChoiceId ? 'bg-[#FEF3C7] border-[#F59E0B] text-[#78350F] font-bold shadow-2xs' : 'bg-white/70 border-dashed border-[#D5CEC2] text-[#A8A29E]',
              'px-3 py-2 rounded-xl border flex items-center gap-2 transition'
            ]"
          >
            <span class="w-5 h-5 rounded-full bg-[#D97706] text-white flex items-center justify-center font-bold text-[10px] shadow-2xs">1</span>
            <span class="truncate max-w-[130px] sm:max-w-[170px]">{{ firstChoiceName || '1er choix (+3 pts)' }}</span>
          </div>

          <!-- Choix 2 -->
          <div 
            :class="[
              secondChoiceId ? 'bg-[#F3EFEA] border-[#78716C] text-[#1C1917] font-bold shadow-2xs' : 'bg-white/70 border-dashed border-[#D5CEC2] text-[#A8A29E]',
              'px-3 py-2 rounded-xl border flex items-center gap-2 transition'
            ]"
          >
            <span class="w-5 h-5 rounded-full bg-[#44403C] text-white flex items-center justify-center font-bold text-[10px] shadow-2xs">2</span>
            <span class="truncate max-w-[130px] sm:max-w-[170px]">{{ secondChoiceName || '2e choix (+2 pts)' }}</span>
          </div>

          <!-- Choix 3 -->
          <div 
            :class="[
              thirdChoiceId ? 'bg-[#FFEDD5] border-[#FB923C] text-[#7C2D12] font-bold shadow-2xs' : 'bg-white/70 border-dashed border-[#D5CEC2] text-[#A8A29E]',
              'px-3 py-2 rounded-xl border flex items-center gap-2 transition'
            ]"
          >
            <span class="w-5 h-5 rounded-full bg-[#C2410C] text-white flex items-center justify-center font-bold text-[10px] shadow-2xs">3</span>
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
                ? 'bg-[#C2410C] hover:bg-[#9A3412] active:bg-[#7C2D12] text-white shadow-sm ring-2 ring-[#C2410C]/30'
                : 'bg-[#E7E2D9] text-[#A8A29E] cursor-not-allowed border border-[#D5CEC2]',
              'px-6 py-3 rounded-xl font-bold text-sm transition flex items-center justify-center gap-2 cursor-pointer'
            ]"
          >
            <Lock class="w-4 h-4 shrink-0" />
            <span>{{ isSubmitting ? 'Enregistrement...' : submitButtonLabel }}</span>
          </button>
          <span class="text-[11px] text-[#78716C] mt-1 text-center lg:text-right font-medium">
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
    <div class="bg-white/90 backdrop-blur-sm rounded-2xl border border-[#E7E2D9] p-4 sm:p-5 shadow-xs space-y-3">
      <div class="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        <!-- Recherche textuelle -->
        <div class="relative flex-1">
          <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5 text-[#78716C]">
            <Search class="w-4 h-4" />
          </div>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Rechercher par nom, cuisine ou adresse..."
            class="block w-full rounded-xl border border-[#E7E2D9] bg-[#FAF7F2] pl-10 pr-3 py-2 text-sm font-medium text-[#1C1917] placeholder:text-[#A8A29E] focus:bg-white focus:border-[#C2410C] focus:ring-2 focus:ring-[#C2410C]/20 focus:outline-none transition"
          />
        </div>

        <!-- Bascule de Tri : Note vs Distance -->
        <div class="flex items-center gap-1.5 shrink-0 bg-[#F3EFEA] p-1 rounded-xl border border-[#E7E2D9]">
          <button
            type="button"
            @click="sortBy = 'rating'"
            :class="[
              sortBy === 'rating' ? 'bg-white text-[#1C1917] font-bold shadow-2xs border border-[#E7E2D9]' : 'text-[#78716C] hover:text-[#1C1917]',
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
              sortBy === 'distance' ? 'bg-white text-[#1C1917] font-bold shadow-2xs border border-[#E7E2D9]' : 'text-[#78716C] hover:text-[#1C1917]',
              'px-3 py-1.5 rounded-lg text-xs transition flex items-center gap-1.5 cursor-pointer'
            ]"
          >
            <Footprints class="w-3.5 h-3.5 text-emerald-700" />
            <span>Plus proches</span>
          </button>
        </div>
      </div>

      <!-- Filtres secondaires : Cuisines, Formules, Compteur -->
      <div class="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-[#E7E2D9] text-xs">
        <div class="flex flex-wrap items-center gap-2">
          <!-- Filtre Cuisine -->
          <div class="flex items-center gap-1.5 text-[#44403C] font-medium">
            <Filter class="w-3.5 h-3.5 text-[#78716C]" />
            <span>Cuisine :</span>
            <select
              v-model="selectedCuisine"
              class="rounded-lg border border-[#D5CEC2] bg-[#FAF7F2] px-2.5 py-1 text-xs font-semibold text-[#1C1917] focus:border-[#C2410C] focus:outline-none cursor-pointer"
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
                ? 'bg-emerald-50 text-emerald-900 border-emerald-400 font-bold ring-1 ring-emerald-400/30' 
                : 'bg-[#FAF7F2] text-[#44403C] border-[#D5CEC2] hover:bg-white',
              'px-3 py-1 rounded-lg border text-xs transition cursor-pointer flex items-center gap-1.5'
            ]"
          >
            <span>Avec carte / menu en ligne</span>
          </button>
        </div>

        <span class="text-[#78716C] font-medium text-xs">
          <strong class="text-[#1C1917]">{{ filteredRestaurants.length }}</strong> sur {{ restaurants.length }} restaurants affichés
        </span>
      </div>
    </div>

    <!-- Grille des cartes de restaurants -->
    <div>
      <div class="flex items-center justify-between mb-4">
        <div>
          <h3 class="font-serif text-2xl font-bold text-[#1C1917] tracking-tight">
            Établissements accessibles à pied
          </h3>
          <p class="text-xs text-[#78716C] mt-0.5">
            Attribuez vos 3 préférences avec les boutons 1er (+3 pts), 2e (+2 pts) ou 3e (+1 pt)
          </p>
        </div>
      </div>

      <!-- État vide si filtre trop restrictif -->
      <div v-if="filteredRestaurants.length === 0" class="rounded-2xl border border-[#E7E2D9] bg-white/70 p-8 text-center text-[#44403C] space-y-2">
        <p class="font-serif text-base font-bold text-[#1C1917]">Aucun restaurant ne correspond à votre filtre.</p>
        <p class="text-xs text-[#78716C]">Essayez de réinitialiser la recherche ou de sélectionner "Toutes les cuisines".</p>
        <button
          type="button"
          @click="searchQuery = ''; selectedCuisine = 'ALL'; onlyWithMenu = false;"
          class="mt-2 inline-flex items-center px-3 py-1.5 rounded-lg bg-white border border-[#D5CEC2] text-xs font-bold text-[#1C1917] hover:bg-[#FAF7F2] cursor-pointer"
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

