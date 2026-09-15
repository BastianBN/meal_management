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
    <div class="bg-[#FFFDF9] rounded-2xl border border-[#E8E3DA] p-5 sm:p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <div class="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-[#B85B43] mb-1">
          <MapPin class="w-3.5 h-3.5 text-[#B85B43] shrink-0" />
          <span>Point de départ</span>
        </div>
        <h2 class="font-serif text-xl sm:text-2xl font-normal text-[#292524] tracking-wide leading-snug">
          {{ session.departure_address }}
        </h2>
        <p class="text-xs text-[#78716C] mt-1.5 flex items-center gap-2 flex-wrap">
          <span class="inline-flex items-center gap-1.5 font-medium text-[#292524] bg-[#FAF8F5] px-2.5 py-0.5 rounded-md border border-[#E8E3DA]">
            <Footprints class="w-3.5 h-3.5 text-[#5C6F5A]" />
            Rayon : {{ session.radius_meters >= 1000 ? (session.radius_meters / 1000).toFixed(1).replace('.', ',') + ' km' : session.radius_meters + ' m' }} (~{{ Math.round(session.radius_meters / 100) }} min à pied)
          </span>
          <span class="text-[#DDD7CD]">•</span>
          <span class="font-medium text-[#57534E]">{{ restaurants.length }} restaurants repérés</span>
        </p>
      </div>

      <!-- Boutons Partager & Bascule Carte -->
      <div class="flex items-center gap-2 shrink-0">
        <button
          type="button"
          @click="showMap = !showMap"
          class="inline-flex items-center gap-1.5 px-3.5 py-2.5 rounded-xl border border-[#E8E3DA] hover:border-[#292524] bg-[#FFFDF9] hover:bg-[#FAF8F5] text-[#57534E] hover:text-[#292524] text-xs font-medium transition cursor-pointer"
        >
          <MapIcon v-if="!showMap" class="w-4 h-4 text-[#78716C]" />
          <List v-else class="w-4 h-4 text-[#78716C]" />
          <span>{{ showMap ? 'Masquer la carte' : 'Afficher la carte' }}</span>
        </button>

        <button
          type="button"
          @click="copyShareLink"
          class="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl border border-[#E8C7BE] hover:border-[#B85B43] bg-[#FBF4F1] hover:bg-[#F6ECE8] text-[#B85B43] text-xs font-medium transition cursor-pointer"
        >
          <CheckCircle2 v-if="copySuccess" class="w-4 h-4 text-[#5C6F5A]" />
          <Share2 v-else class="w-4 h-4 text-[#B85B43]" />
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
    <div class="bg-[#F7F4EE]/95 backdrop-blur-md rounded-2xl border border-[#E8E3DA] p-4 sm:p-5 sticky top-4 z-20">
      <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <!-- Champ nom du votant -->
        <div class="w-full lg:w-72 shrink-0">
          <label for="voter-name" class="block text-xs font-semibold uppercase tracking-wider text-[#292524] mb-1">
            Votre prénom ou nom <span class="text-[#B85B43]">*</span>
          </label>
          <div class="relative rounded-xl">
            <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-[#78716C]">
              <User class="h-4 w-4" />
            </div>
            <input
              id="voter-name"
              v-model="voterName"
              type="text"
              required
              placeholder="ex : Marc, Camille..."
              class="block w-full rounded-xl border border-[#E8E3DA] bg-[#FFFDF9] pl-9 pr-3 py-2 text-sm font-normal text-[#292524] placeholder:text-[#A8A29E] focus:border-[#B85B43] focus:ring-1 focus:ring-[#B85B43]/20 focus:outline-none transition"
            />
          </div>
        </div>

        <!-- Récapitulatif visuel des 3 choix -->
        <div class="flex-1 flex flex-wrap items-center gap-2 text-xs">
          <!-- Choix 1 : Vermillon Hanko -->
          <div 
            :class="[
              firstChoiceId ? 'bg-[#FBF4F1] border-[#E8C7BE] text-[#7C2D12] font-medium' : 'bg-[#FFFDF9] border-dashed border-[#DDD7CD] text-[#A8A29E]',
              'px-3 py-2 rounded-xl border flex items-center gap-2 transition'
            ]"
          >
            <span class="w-5 h-5 rounded-full bg-[#B85B43] text-white flex items-center justify-center font-medium text-[10px]">1</span>
            <span class="truncate max-w-[130px] sm:max-w-[170px]">{{ firstChoiceName || '1er choix (+3 pts)' }}</span>
          </div>

          <!-- Choix 2 : Thé Matcha -->
          <div 
            :class="[
              secondChoiceId ? 'bg-[#F3F6F2] border-[#CBD8C8] text-[#2F3D2C] font-medium' : 'bg-[#FFFDF9] border-dashed border-[#DDD7CD] text-[#A8A29E]',
              'px-3 py-2 rounded-xl border flex items-center gap-2 transition'
            ]"
          >
            <span class="w-5 h-5 rounded-full bg-[#5C6F5A] text-white flex items-center justify-center font-medium text-[10px]">2</span>
            <span class="truncate max-w-[130px] sm:max-w-[170px]">{{ secondChoiceName || '2e choix (+2 pts)' }}</span>
          </div>

          <!-- Choix 3 : Galet / Bambou -->
          <div 
            :class="[
              thirdChoiceId ? 'bg-[#F7F5F2] border-[#DDD7CD] text-[#4A433A] font-medium' : 'bg-[#FFFDF9] border-dashed border-[#DDD7CD] text-[#A8A29E]',
              'px-3 py-2 rounded-xl border flex items-center gap-2 transition'
            ]"
          >
            <span class="w-5 h-5 rounded-full bg-[#82786D] text-white flex items-center justify-center font-medium text-[10px]">3</span>
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
                ? 'bg-[#B85B43] hover:bg-[#9E4C36] active:bg-[#853B27] text-white font-medium'
                : 'bg-[#EFEBE3] text-[#A8A29E] cursor-not-allowed border border-[#DDD7CD]',
              'px-6 py-3 rounded-xl text-sm transition flex items-center justify-center gap-2 cursor-pointer'
            ]"
          >
            <Lock class="w-4 h-4 shrink-0" />
            <span>{{ isSubmitting ? 'Enregistrement...' : submitButtonLabel }}</span>
          </button>
          <span class="text-[11px] text-[#78716C] mt-1 text-center lg:text-right font-normal">
            Vote définitif • Enregistrement irrévocable
          </span>
        </div>
      </div>

      <!-- Erreur éventuelle -->
      <div v-if="errorMessage" class="mt-3 p-3 rounded-xl bg-[#FBF4F1] border border-[#E8C7BE] text-[#B85B43] text-xs flex items-center gap-2 font-medium">
        <AlertCircle class="w-4 h-4 shrink-0" />
        <span>{{ errorMessage }}</span>
      </div>
    </div>

    <!-- Barre de filtrage & tri -->
    <div class="bg-[#FFFDF9] rounded-2xl border border-[#E8E3DA] p-4 sm:p-5 space-y-3">
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
            class="block w-full rounded-xl border border-[#E8E3DA] bg-[#FAF8F5] pl-10 pr-3 py-2 text-sm font-normal text-[#292524] placeholder:text-[#A8A29E] focus:bg-[#FFFDF9] focus:border-[#B85B43] focus:ring-1 focus:ring-[#B85B43]/20 focus:outline-none transition"
          />
        </div>

        <!-- Bascule de Tri : Note vs Distance -->
        <div class="flex items-center gap-1.5 shrink-0 bg-[#EFEBE3] p-1 rounded-xl border border-[#E8E3DA]">
          <button
            type="button"
            @click="sortBy = 'rating'"
            :class="[
              sortBy === 'rating' ? 'bg-[#FFFDF9] text-[#292524] font-medium border border-[#E8E3DA]' : 'text-[#78716C] hover:text-[#292524]',
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
              sortBy === 'distance' ? 'bg-[#FFFDF9] text-[#292524] font-medium border border-[#E8E3DA]' : 'text-[#78716C] hover:text-[#292524]',
              'px-3 py-1.5 rounded-lg text-xs transition flex items-center gap-1.5 cursor-pointer'
            ]"
          >
            <Footprints class="w-3.5 h-3.5 text-[#5C6F5A]" />
            <span>Plus proches</span>
          </button>
        </div>
      </div>

      <!-- Filtres secondaires : Cuisines, Formules, Compteur -->
      <div class="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-[#E8E3DA] text-xs">
        <div class="flex flex-wrap items-center gap-2">
          <!-- Filtre Cuisine -->
          <div class="flex items-center gap-1.5 text-[#57534E] font-medium">
            <Filter class="w-3.5 h-3.5 text-[#78716C]" />
            <span>Cuisine :</span>
            <select
              v-model="selectedCuisine"
              class="rounded-lg border border-[#E8E3DA] bg-[#FAF8F5] px-2.5 py-1 text-xs font-medium text-[#292524] focus:border-[#B85B43] focus:outline-none cursor-pointer"
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
                ? 'bg-[#F3F6F2] text-[#3E503B] border border-[#CBD8C8] font-medium' 
                : 'bg-[#FAF8F5] text-[#57534E] border border-[#E8E3DA] hover:bg-[#FFFDF9]',
              'px-3 py-1 rounded-lg text-xs transition cursor-pointer flex items-center gap-1.5'
            ]"
          >
            <span>Avec carte / menu en ligne</span>
          </button>
        </div>

        <span class="text-[#78716C] font-normal text-xs">
          <strong class="text-[#292524] font-medium">{{ filteredRestaurants.length }}</strong> sur {{ restaurants.length }} restaurants affichés
        </span>
      </div>
    </div>

    <!-- Grille des cartes de restaurants -->
    <div>
      <div class="flex items-center justify-between mb-4">
        <div>
          <h3 class="font-serif text-2xl font-normal text-[#292524] tracking-wide">
            Établissements accessibles à pied
          </h3>
          <p class="text-xs text-[#78716C] mt-0.5">
            Attribuez vos 3 préférences avec les boutons 1er (+3 pts), 2e (+2 pts) ou 3e (+1 pt)
          </p>
        </div>
      </div>

      <!-- État vide si filtre trop restrictif -->
      <div v-if="filteredRestaurants.length === 0" class="rounded-2xl border border-[#E8E3DA] bg-[#FFFDF9] p-8 text-center text-[#57534E] space-y-2">
        <p class="font-serif text-base font-medium text-[#292524]">Aucun restaurant ne correspond à votre filtre.</p>
        <p class="text-xs text-[#78716C]">Essayez de réinitialiser la recherche ou de sélectionner "Toutes les cuisines".</p>
        <button
          type="button"
          @click="searchQuery = ''; selectedCuisine = 'ALL'; onlyWithMenu = false;"
          class="mt-2 inline-flex items-center px-3 py-1.5 rounded-lg bg-[#FAF8F5] border border-[#E8E3DA] text-xs font-medium text-[#292524] hover:bg-[#FFFDF9] cursor-pointer"
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

