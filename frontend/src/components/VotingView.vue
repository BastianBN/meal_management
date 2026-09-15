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
    <!-- En-tête de Session (Adresse & Rayon) -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-[#FFFCF7] rounded-2xl border border-[#E5D6C5] p-5 sm:p-6">
      <div>
        <div class="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-[#C2542D] mb-1">
          <MapPin class="w-3.5 h-3.5 text-[#C2542D] shrink-0" />
          <span>Point de départ</span>
        </div>
        <h2 class="font-serif text-xl sm:text-2xl font-normal text-[#2C2019] tracking-wide leading-snug">
          {{ session.departure_address }}
        </h2>
        <p class="text-xs text-[#857263] mt-1.5 flex items-center gap-2 flex-wrap">
          <span class="inline-flex items-center gap-1.5 font-medium text-[#2C2019] bg-[#FAF2E8] px-2.5 py-0.5 rounded-md border border-[#E5D6C5]">
            <Footprints class="w-3.5 h-3.5 text-[#586F54]" />
            Rayon : {{ session.radius_meters >= 1000 ? (session.radius_meters / 1000).toFixed(1).replace('.', ',') + ' km' : session.radius_meters + ' m' }} (~{{ Math.round(session.radius_meters / 100) }} min à pied)
          </span>
          <span class="text-[#DAC7B2]">•</span>
          <span class="font-medium text-[#5D4B3E]">{{ restaurants.length }} restaurants repérés</span>
        </p>
      </div>

      <!-- Boutons Partager & Bascule Carte -->
      <div class="flex items-center gap-2 shrink-0">
        <button
          type="button"
          @click="showMap = !showMap"
          class="inline-flex items-center gap-1.5 px-3.5 py-2.5 rounded-xl border border-[#E5D6C5] hover:border-[#2C2019] bg-[#FFFCF7] hover:bg-[#FAF2E8] text-[#5D4B3E] hover:text-[#2C2019] text-xs font-medium transition cursor-pointer"
        >
          <MapIcon v-if="!showMap" class="w-4 h-4 text-[#857263]" />
          <List v-else class="w-4 h-4 text-[#857263]" />
          <span>{{ showMap ? 'Masquer la carte' : 'Afficher la carte' }}</span>
        </button>

        <button
          type="button"
          @click="copyShareLink"
          class="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl border border-[#ECCDBE] hover:border-[#C2542D] bg-[#FAF0E8] hover:bg-[#F5E5DC] text-[#C2542D] text-xs font-medium transition cursor-pointer"
        >
          <CheckCircle2 v-if="copySuccess" class="w-4 h-4 text-[#586F54]" />
          <Share2 v-else class="w-4 h-4 text-[#C2542D]" />
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
    <div class="bg-[#FFFCF7]/95 backdrop-blur-md rounded-2xl border border-[#E5D6C5] p-4 sm:p-5 sticky top-4 z-20 shadow-md shadow-[#5D4B3E]/5">
      <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <!-- Champ nom du votant -->
        <div class="w-full lg:w-72 shrink-0">
          <label for="voter-name" class="block text-xs font-semibold uppercase tracking-wider text-[#2C2019] mb-1">
            Votre prénom ou nom <span class="text-[#C2542D]">*</span>
          </label>
          <div class="relative rounded-xl">
            <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-[#857263]">
              <User class="h-4 w-4" />
            </div>
            <input
              id="voter-name"
              v-model="voterName"
              type="text"
              required
              placeholder="ex : Marc, Camille..."
              class="block w-full rounded-xl border border-[#E5D6C5] bg-[#FAF2E8] pl-9 pr-3 py-2 text-sm font-normal text-[#2C2019] placeholder:text-[#AC9B8D] focus:bg-[#FFFCF7] focus:border-[#C2542D] focus:ring-1 focus:ring-[#C2542D]/20 focus:outline-none transition"
            />
          </div>
        </div>

        <!-- Récapitulatif visuel des 3 choix -->
        <div class="flex-1 flex flex-wrap items-center gap-2 text-xs">
          <!-- Choix 1 : Vermillon Hanko -->
          <div 
            :class="[
              firstChoiceId ? 'bg-[#FAF0E8] border-[#ECCDBE] text-[#7C2D12] font-medium' : 'bg-[#FFFCF7] border-dashed border-[#DAC7B2] text-[#AC9B8D]',
              'px-3 py-2 rounded-xl border flex items-center gap-2 transition'
            ]"
          >
            <span class="w-5 h-5 rounded-full bg-[#C2542D] text-white flex items-center justify-center font-medium text-[10px]">1</span>
            <span class="truncate max-w-[130px] sm:max-w-[170px]">{{ firstChoiceName || '1er choix (+3 pts)' }}</span>
          </div>

          <!-- Choix 2 : Thé Matcha -->
          <div 
            :class="[
              secondChoiceId ? 'bg-[#F0F5EE] border-[#C8D7C4] text-[#2F3D2C] font-medium' : 'bg-[#FFFCF7] border-dashed border-[#DAC7B2] text-[#AC9B8D]',
              'px-3 py-2 rounded-xl border flex items-center gap-2 transition'
            ]"
          >
            <span class="w-5 h-5 rounded-full bg-[#586F54] text-white flex items-center justify-center font-medium text-[10px]">2</span>
            <span class="truncate max-w-[130px] sm:max-w-[170px]">{{ secondChoiceName || '2e choix (+2 pts)' }}</span>
          </div>

          <!-- Choix 3 : Galet / Bambou -->
          <div 
            :class="[
              thirdChoiceId ? 'bg-[#F4EDE5] border-[#DBCFBF] text-[#4A433A] font-medium' : 'bg-[#FFFCF7] border-dashed border-[#DAC7B2] text-[#AC9B8D]',
              'px-3 py-2 rounded-xl border flex items-center gap-2 transition'
            ]"
          >
            <span class="w-5 h-5 rounded-full bg-[#7E6C5C] text-white flex items-center justify-center font-medium text-[10px]">3</span>
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
                ? 'bg-[#C2542D] hover:bg-[#A64320] active:bg-[#8D3517] text-white font-medium'
                : 'bg-[#EFE4D6] text-[#AC9B8D] cursor-not-allowed border border-[#DAC7B2]',
              'px-6 py-3 rounded-xl text-sm transition flex items-center justify-center gap-2 cursor-pointer'
            ]"
          >
            <Lock class="w-4 h-4 shrink-0" />
            <span>{{ isSubmitting ? 'Enregistrement...' : submitButtonLabel }}</span>
          </button>
          <span class="text-[11px] text-[#857263] mt-1 text-center lg:text-right font-normal">
            Vote définitif • Enregistrement irrévocable
          </span>
        </div>
      </div>

      <!-- Erreur éventuelle -->
      <div v-if="errorMessage" class="mt-3 p-3 rounded-xl bg-[#FAF0E8] border border-[#ECCDBE] text-[#C2542D] text-xs flex items-center gap-2 font-medium">
        <AlertCircle class="w-4 h-4 shrink-0" />
        <span>{{ errorMessage }}</span>
      </div>
    </div>

    <!-- Barre de filtrage & tri -->
    <div class="bg-[#FFFCF7] rounded-2xl border border-[#E5D6C5] p-4 sm:p-5 space-y-3">
      <div class="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        <!-- Recherche textuelle -->
        <div class="relative flex-1">
          <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5 text-[#857263]">
            <Search class="w-4 h-4" />
          </div>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Rechercher par nom, cuisine ou adresse..."
            class="block w-full rounded-xl border border-[#E5D6C5] bg-[#FAF2E8] pl-10 pr-3 py-2 text-sm font-normal text-[#2C2019] placeholder:text-[#AC9B8D] focus:bg-[#FFFCF7] focus:border-[#C2542D] focus:ring-1 focus:ring-[#C2542D]/20 focus:outline-none transition"
          />
        </div>

        <!-- Bascule de Tri : Note vs Distance -->
        <div class="flex items-center gap-1.5 shrink-0 bg-[#EFE4D6] p-1 rounded-xl border border-[#E5D6C5]">
          <button
            type="button"
            @click="sortBy = 'rating'"
            :class="[
              sortBy === 'rating' ? 'bg-[#FFFCF7] text-[#2C2019] font-medium border border-[#E5D6C5]' : 'text-[#857263] hover:text-[#2C2019]',
              'px-3 py-1.5 rounded-lg text-xs transition flex items-center gap-1.5 cursor-pointer'
            ]"
          >
            <Star class="w-3.5 h-3.5 text-amber-600 fill-amber-500" />
            <span>Mieux notés ⭐</span>
          </button>
          <button
            type="button"
            @click="sortBy = 'distance'"
            :class="[
              sortBy === 'distance' ? 'bg-[#FFFCF7] text-[#2C2019] font-medium border border-[#E5D6C5]' : 'text-[#857263] hover:text-[#2C2019]',
              'px-3 py-1.5 rounded-lg text-xs transition flex items-center gap-1.5 cursor-pointer'
            ]"
          >
            <Footprints class="w-3.5 h-3.5 text-[#586F54]" />
            <span>Plus proches</span>
          </button>
        </div>
      </div>

      <!-- Filtres secondaires : Cuisines, Formules, Compteur -->
      <div class="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-[#E5D6C5] text-xs">
        <div class="flex flex-wrap items-center gap-2">
          <!-- Filtre Cuisine -->
          <div class="flex items-center gap-1.5 text-[#5D4B3E] font-medium">
            <Filter class="w-3.5 h-3.5 text-[#857263]" />
            <span>Cuisine :</span>
            <select
              v-model="selectedCuisine"
              class="rounded-lg border border-[#E5D6C5] bg-[#FAF2E8] px-2.5 py-1 text-xs font-medium text-[#2C2019] focus:border-[#C2542D] focus:outline-none cursor-pointer"
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
                ? 'bg-[#F0F5EE] text-[#364A32] border border-[#C8D7C4] font-medium' 
                : 'bg-[#FAF2E8] text-[#5D4B3E] border border-[#E5D6C5] hover:bg-[#FFFCF7]',
              'px-3 py-1 rounded-lg text-xs transition cursor-pointer flex items-center gap-1.5'
            ]"
          >
            <span>Avec carte / menu en ligne</span>
          </button>
        </div>

        <span class="text-[#857263] font-normal text-xs">
          <strong class="text-[#2C2019] font-medium">{{ filteredRestaurants.length }}</strong> sur {{ restaurants.length }} restaurants affichés
        </span>
      </div>
    </div>

    <!-- Grille des cartes de restaurants -->
    <div>
      <div class="flex items-center justify-between mb-4">
        <div>
          <h3 class="font-serif text-2xl font-normal text-[#2C2019] tracking-wide">
            Établissements accessibles à pied
          </h3>
          <p class="text-xs text-[#857263] mt-0.5">
            Attribuez vos 3 préférences avec les boutons 1er (+3 pts), 2e (+2 pts) ou 3e (+1 pt)
          </p>
        </div>
      </div>

      <!-- État vide si filtre trop restrictif -->
      <div v-if="filteredRestaurants.length === 0" class="rounded-2xl border border-[#E5D6C5] bg-[#FFFCF7] p-8 text-center text-[#5D4B3E] space-y-2">
        <p class="font-serif text-base font-medium text-[#2C2019]">Aucun restaurant ne correspond à votre filtre.</p>
        <p class="text-xs text-[#857263]">Essayez de réinitialiser la recherche ou de sélectionner "Toutes les cuisines".</p>
        <button
          type="button"
          @click="searchQuery = ''; selectedCuisine = 'ALL'; onlyWithMenu = false;"
          class="mt-2 inline-flex items-center px-3 py-1.5 rounded-lg bg-[#FAF2E8] border border-[#E5D6C5] text-xs font-medium text-[#2C2019] hover:bg-[#FFFCF7] cursor-pointer"
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
