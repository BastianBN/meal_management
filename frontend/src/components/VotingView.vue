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
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-[#FFFFFF] rounded-2xl border border-[#E2D9CF] p-5 sm:p-6 shadow-sm">
      <div>
        <div class="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-[#DC2626] mb-1 font-sans">
          <MapPin class="w-3.5 h-3.5 text-[#DC2626] shrink-0" />
          <span>Point de départ</span>
        </div>
        <h2 class="font-serif text-2xl sm:text-3xl font-normal text-[#191C22] tracking-wide leading-snug">
          {{ session.departure_address }}
        </h2>
        <p class="text-xs text-[#64748B] mt-1.5 flex items-center gap-2 flex-wrap font-sans">
          <span class="inline-flex items-center gap-1.5 font-medium text-[#191C22] bg-[#F8F5F2] px-2.5 py-0.5 rounded-md border border-[#E2D9CF]">
            <Footprints class="w-3.5 h-3.5 text-[#D97706]" />
            Périmètre : {{ session.radius_meters >= 1000 ? (session.radius_meters / 1000).toFixed(1).replace('.', ',') + ' km' : session.radius_meters + ' m' }} (~{{ Math.round(session.radius_meters / 100) }} min à pied)
          </span>
          <span class="text-[#CBD5E1]">•</span>
          <span class="font-medium text-[#475569]">{{ restaurants.length }} adresses trouvées</span>
        </p>
      </div>

      <!-- Boutons Partager & Bascule Carte -->
      <div class="flex items-center gap-2 shrink-0 font-sans">
        <button
          type="button"
          @click="showMap = !showMap"
          class="inline-flex items-center gap-1.5 px-3.5 py-2.5 rounded-xl border border-[#E2D9CF] hover:border-[#191C22] bg-[#FFFFFF] hover:bg-[#F8F5F2] text-[#475569] hover:text-[#191C22] text-xs font-medium transition cursor-pointer shadow-xs"
        >
          <MapIcon v-if="!showMap" class="w-4 h-4 text-[#64748B]" />
          <List v-else class="w-4 h-4 text-[#64748B]" />
          <span>{{ showMap ? 'Masquer la carte' : 'Afficher la carte' }}</span>
        </button>

        <button
          type="button"
          @click="copyShareLink"
          class="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl border border-[#FECACA] hover:border-[#DC2626] bg-[#FEF2F2] hover:bg-[#FEE2E2] text-[#DC2626] text-xs font-medium transition cursor-pointer shadow-xs"
        >
          <CheckCircle2 v-if="copySuccess" class="w-4 h-4 text-[#16A34A]" />
          <Share2 v-else class="w-4 h-4 text-[#DC2626]" />
          <span>{{ copySuccess ? 'Lien copié !' : 'Partager l\'ardoise' }}</span>
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

    <!-- Barre d'action fixe : L'Ardoise de Vote flottante -->
    <div class="bg-[#191C22]/95 backdrop-blur-md rounded-2xl border border-[#383F4C] p-4 sm:p-5 sticky top-4 z-20 shadow-xl shadow-black/25 text-[#F8FAFC]">
      <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4 font-sans">
        <!-- Champ nom du votant -->
        <div class="w-full lg:w-72 shrink-0">
          <label for="voter-name" class="block text-xs font-semibold uppercase tracking-wider text-[#F8FAFC] mb-1">
            Votre prénom ou table <span class="text-[#DC2626]">*</span>
          </label>
          <div class="relative rounded-xl">
            <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-[#94A3B8]">
              <User class="h-4 w-4" />
            </div>
            <input
              id="voter-name"
              v-model="voterName"
              type="text"
              required
              placeholder="ex : Marc, Camille..."
              class="block w-full rounded-xl border border-[#383F4C] bg-[#22262E] pl-9 pr-3 py-2 text-sm font-normal text-[#F8FAFC] placeholder:text-[#94A3B8] focus:bg-[#2A2F39] focus:border-[#DC2626] focus:ring-1 focus:ring-[#DC2626]/30 focus:outline-none transition"
            />
          </div>
        </div>

        <!-- Récapitulatif visuel des 3 choix (Trio Rouge, Laiton, Zinc) -->
        <div class="flex-1 flex flex-wrap items-center gap-2 text-xs">
          <!-- Choix 1 : Rouge Bistrot -->
          <div 
            :class="[
              firstChoiceId ? 'bg-[#2E1819] border-[#DC2626] text-[#FCA5A5] font-medium' : 'bg-[#22262E] border-dashed border-[#383F4C] text-[#64748B]',
              'px-3 py-2 rounded-xl border flex items-center gap-2 transition'
            ]"
          >
            <span class="w-5 h-5 rounded-full bg-[#DC2626] text-white flex items-center justify-center font-medium text-[10px] shadow-xs">1</span>
            <span class="truncate max-w-[130px] sm:max-w-[170px] font-serif text-sm">{{ firstChoiceName || '1er choix (+3 pts)' }}</span>
          </div>

          <!-- Choix 2 : Laiton Doré -->
          <div 
            :class="[
              secondChoiceId ? 'bg-[#2B2317] border-[#D97706] text-[#FDE68A] font-medium' : 'bg-[#22262E] border-dashed border-[#383F4C] text-[#64748B]',
              'px-3 py-2 rounded-xl border flex items-center gap-2 transition'
            ]"
          >
            <span class="w-5 h-5 rounded-full bg-[#D97706] text-white flex items-center justify-center font-medium text-[10px] shadow-xs">2</span>
            <span class="truncate max-w-[130px] sm:max-w-[170px] font-serif text-sm">{{ secondChoiceName || '2e choix (+2 pts)' }}</span>
          </div>

          <!-- Choix 3 : Zinc Étain -->
          <div 
            :class="[
              thirdChoiceId ? 'bg-[#242933] border-[#64748B] text-[#CBD5E1] font-medium' : 'bg-[#22262E] border-dashed border-[#383F4C] text-[#64748B]',
              'px-3 py-2 rounded-xl border flex items-center gap-2 transition'
            ]"
          >
            <span class="w-5 h-5 rounded-full bg-[#64748B] text-white flex items-center justify-center font-medium text-[10px] shadow-xs">3</span>
            <span class="truncate max-w-[130px] sm:max-w-[170px] font-serif text-sm">{{ thirdChoiceName || '3e choix (+1 pt)' }}</span>
          </div>
        </div>

        <!-- Bouton de validation Rouge Bistrot -->
        <div class="shrink-0 flex flex-col items-stretch lg:items-end">
          <button
            type="button"
            :disabled="isSubmitting || !canSubmit"
            @click="handleVoteSubmit"
            :class="[
              canSubmit
                ? 'bg-[#DC2626] hover:bg-[#B91C1C] active:bg-[#991B1B] text-white font-medium shadow-sm'
                : 'bg-[#22262E] text-[#64748B] cursor-not-allowed border border-[#383F4C]',
              'px-6 py-3 rounded-xl text-sm transition flex items-center justify-center gap-2 cursor-pointer'
            ]"
          >
            <Lock class="w-4 h-4 shrink-0" />
            <span>{{ isSubmitting ? 'Transmission...' : submitButtonLabel }}</span>
          </button>
          <span class="text-[11px] text-[#94A3B8] mt-1 text-center lg:text-right font-normal">
            Choix définitif • Transmis à la cuisine
          </span>
        </div>
      </div>

      <!-- Erreur éventuelle -->
      <div v-if="errorMessage" class="mt-3 p-3 rounded-xl bg-[#2E1819] border border-[#DC2626] text-[#FCA5A5] text-xs flex items-center gap-2 font-medium">
        <AlertCircle class="w-4 h-4 shrink-0" />
        <span>{{ errorMessage }}</span>
      </div>
    </div>

    <!-- Barre de filtrage & tri brasserie -->
    <div class="bg-[#FFFFFF] rounded-2xl border border-[#E2D9CF] p-4 sm:p-5 space-y-3 shadow-sm font-sans">
      <div class="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        <!-- Recherche textuelle -->
        <div class="relative flex-1">
          <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5 text-[#94A3B8]">
            <Search class="w-4 h-4" />
          </div>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Rechercher une table, cuisine ou rue..."
            class="block w-full rounded-xl border border-[#E2D9CF] bg-[#F8F5F2] pl-10 pr-3 py-2 text-sm font-normal text-[#191C22] placeholder:text-[#94A3B8] focus:bg-[#FFFFFF] focus:border-[#DC2626] focus:ring-1 focus:ring-[#DC2626]/20 focus:outline-none transition"
          />
        </div>

        <!-- Bascule de Tri : Note vs Distance -->
        <div class="flex items-center gap-1.5 shrink-0 bg-[#E7DED4] p-1 rounded-xl border border-[#D5CBC0]">
          <button
            type="button"
            @click="sortBy = 'rating'"
            :class="[
              sortBy === 'rating' ? 'bg-[#191C22] text-[#F8FAFC] font-medium border border-[#383F4C] shadow-xs' : 'text-[#64748B] hover:text-[#191C22]',
              'px-3 py-1.5 rounded-lg text-xs transition flex items-center gap-1.5 cursor-pointer'
            ]"
          >
            <Star class="w-3.5 h-3.5 text-[#D97706] fill-[#D97706]" />
            <span>Mieux notées ⭐</span>
          </button>
          <button
            type="button"
            @click="sortBy = 'distance'"
            :class="[
              sortBy === 'distance' ? 'bg-[#191C22] text-[#F8FAFC] font-medium border border-[#383F4C] shadow-xs' : 'text-[#64748B] hover:text-[#191C22]',
              'px-3 py-1.5 rounded-lg text-xs transition flex items-center gap-1.5 cursor-pointer'
            ]"
          >
            <Footprints class="w-3.5 h-3.5 text-[#D97706]" />
            <span>Plus proches</span>
          </button>
        </div>
      </div>

      <!-- Filtres secondaires : Cuisines, Formules, Compteur -->
      <div class="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-[#E2D9CF] text-xs">
        <div class="flex flex-wrap items-center gap-2">
          <!-- Filtre Cuisine -->
          <div class="flex items-center gap-1.5 text-[#475569] font-medium">
            <Filter class="w-3.5 h-3.5 text-[#64748B]" />
            <span>Cuisine :</span>
            <select
              v-model="selectedCuisine"
              class="rounded-lg border border-[#E2D9CF] bg-[#F8F5F2] px-2.5 py-1 text-xs font-medium text-[#191C22] focus:border-[#DC2626] focus:outline-none cursor-pointer"
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
                ? 'bg-[#191C22] text-[#F8FAFC] border border-[#383F4C] font-medium shadow-xs' 
                : 'bg-[#F8F5F2] text-[#475569] border border-[#E2D9CF] hover:bg-[#FFFFFF]',
              'px-3 py-1 rounded-lg text-xs transition cursor-pointer flex items-center gap-1.5'
            ]"
          >
            <span>Avec carte / formules du jour</span>
          </button>
        </div>

        <span class="text-[#64748B] font-normal text-xs">
          <strong class="text-[#191C22] font-medium">{{ filteredRestaurants.length }}</strong> sur {{ restaurants.length }} adresses affichées
        </span>
      </div>
    </div>

    <!-- Grille des ardoises de restaurants -->
    <div>
      <div class="flex items-center justify-between mb-4">
        <div>
          <h3 class="font-serif text-3xl font-normal text-[#191C22] tracking-wide">
            Les Tables du Quartier
          </h3>
          <p class="text-xs text-[#64748B] mt-0.5 font-sans">
            Attribuez vos 3 préférences avec les boutons 1er (+3 pts), 2e (+2 pts) ou 3e (+1 pt)
          </p>
        </div>
      </div>

      <!-- État vide si filtre trop restrictif -->
      <div v-if="filteredRestaurants.length === 0" class="rounded-2xl border border-[#E2D9CF] bg-[#FFFFFF] p-8 text-center text-[#475569] space-y-2 shadow-sm font-sans">
        <p class="font-serif text-xl font-normal text-[#191C22]">Aucune table ne correspond à vos filtres.</p>
        <p class="text-xs text-[#64748B]">Essayez de réinitialiser la recherche ou de sélectionner "Toutes les cuisines".</p>
        <button
          type="button"
          @click="searchQuery = ''; selectedCuisine = 'ALL'; onlyWithMenu = false;"
          class="mt-2 inline-flex items-center px-3 py-1.5 rounded-lg bg-[#F8F5F2] border border-[#E2D9CF] text-xs font-medium text-[#191C22] hover:bg-[#FFFFFF] cursor-pointer shadow-xs"
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
