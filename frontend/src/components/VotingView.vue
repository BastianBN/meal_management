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
  return "Valider mon vote";
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
  <div class="space-y-8">
    <!-- En-tête de Session (Grand Fronton Brasserie & Point de Ralliement) -->
    <div class="bistro-grand-frame rounded-3xl p-6 sm:p-9 relative">
      <!-- 4 Coins Laiton Vénérable -->
      <div class="brass-corner-bracket brass-corner-tl"></div>
      <div class="brass-corner-bracket brass-corner-tr"></div>
      <div class="brass-corner-bracket brass-corner-bl"></div>
      <div class="brass-corner-bracket brass-corner-br"></div>

      <div class="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <div class="flex items-center gap-2 text-sm font-serif font-bold text-[var(--accent-brass)] mb-1.5 uppercase tracking-wider">
            <span>🍽️</span>
            <span>Point de départ</span>
            <span>🍽️</span>
          </div>
          <h2 class="font-display sm:font-serif text-3xl sm:text-4xl lg:text-5xl font-normal text-[var(--text-main)] tracking-wide leading-tight">
            {{ session.departure_address }}
          </h2>
          <div class="text-sm text-[var(--text-muted)] mt-3 flex items-center gap-3 flex-wrap font-serif">
            <span class="inline-flex items-center gap-1.5 px-4 py-2 rounded-full bg-[var(--bg-surface-inset)] border border-[var(--border-subtle)] text-[var(--text-main)] text-sm sm:text-base shadow-2xs">
              <Footprints class="w-4 h-4 text-[var(--accent-red)]" />
              Périmètre : <strong class="text-[var(--text-main)] font-semibold">{{ session.radius_meters >= 1000 ? (session.radius_meters / 1000).toFixed(1).replace('.', ',') + ' km' : session.radius_meters + ' m' }}</strong> (~{{ Math.round(session.radius_meters / 100) }} min à pied)
            </span>
            <span class="text-[var(--text-faint)]">•</span>
            <span class="font-medium text-sm sm:text-base text-[var(--text-main)]">{{ restaurants.length }} restaurants trouvés</span>
          </div>
        </div>

        <!-- Boutons Partager & Bascule Carte -->
        <div class="flex items-center gap-3 shrink-0">
          <button
            type="button"
            @click="showMap = !showMap"
            class="inline-flex items-center gap-2 px-4 py-2.5 rounded-2xl border border-[var(--border-main)] hover:border-[var(--accent-brass)] bg-[var(--bg-surface-inset)] hover:bg-[var(--bg-surface)] text-[var(--text-main)] text-sm font-serif font-semibold transition cursor-pointer shadow-xs"
          >
            <MapIcon v-if="!showMap" class="w-4 h-4 text-[var(--accent-brass)]" />
            <List v-else class="w-4 h-4 text-[var(--accent-brass)]" />
            <span>{{ showMap ? 'Masquer la carte' : 'Afficher la carte' }}</span>
          </button>

          <button
            type="button"
            @click="copyShareLink"
            class="inline-flex items-center gap-2 px-4 py-2.5 rounded-2xl border border-[var(--accent-red-border)] hover:border-[var(--accent-red)] bg-[var(--accent-red-soft)] hover:bg-[var(--accent-red-soft)]/80 text-[var(--accent-red)] text-sm font-serif font-semibold transition cursor-pointer shadow-xs"
          >
            <CheckCircle2 v-if="copySuccess" class="w-4 h-4 text-emerald-600" />
            <Share2 v-else class="w-4 h-4 text-[var(--accent-red)]" />
            <span>{{ copySuccess ? 'Lien copié !' : 'Inviter des collègues' }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Carte interactive Leaflet OpenStreetMap avec cadre façon plan d'architecte -->
    <div v-show="showMap" class="transition-all duration-300">
      <div class="bistro-card-frame rounded-3xl overflow-hidden shadow-lg p-2 sm:p-3">
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
    </div>

    <!-- Barre d'action fixe : Le Bon de Commande du Garçon (Waiter's Docket) -->
    <div class="waiter-docket rounded-3xl p-5 sm:p-6 sticky top-4 z-20 shadow-2xl backdrop-blur-md bg-[var(--bg-surface)]/98 border-2 border-[var(--border-main)]">
      <!-- Pince métallique dorée en haut -->
      <div class="waiter-clip"></div>

      <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-5 pt-2">
        <!-- Champ nom du convive -->
        <div class="w-full lg:w-72 shrink-0">
          <label for="voter-name" class="block font-serif text-base font-bold text-[var(--text-main)] mb-1.5 tracking-wide">
            Votre prénom <span class="text-[var(--accent-red)]">*</span>
          </label>
          <div class="relative rounded-2xl">
            <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5 text-[var(--text-faint)]">
              <User class="h-4 w-4" />
            </div>
            <input
              id="voter-name"
              v-model="voterName"
              type="text"
              required
              placeholder="ex : Marc, Camille..."
              class="block w-full rounded-2xl border border-[var(--border-main)] bg-[var(--bg-surface-inset)] pl-10 pr-3 py-2.5 text-base font-normal text-[var(--text-main)] placeholder:text-[var(--text-faint)] focus:bg-[var(--bg-surface)] focus:border-[var(--accent-brass)] focus:ring-2 focus:ring-[var(--accent-brass)]/20 focus:outline-none transition"
            />
          </div>
        </div>

        <!-- Récapitulatif visuel des 3 choix (Trio Rouge Bordeaux, Laiton, Zinc) -->
        <div class="flex-1 flex flex-wrap items-center gap-2.5 text-sm font-serif">
          <!-- Choix 1 : Rouge Bordeaux -->
          <div 
            :class="[
              firstChoiceId ? 'bg-[var(--accent-red-soft)] border-[var(--accent-red)] text-[var(--accent-red)] font-bold shadow-xs' : 'bg-[var(--bg-surface-inset)] border-dashed border-[var(--border-main)] text-[var(--text-faint)]',
              'px-3.5 py-2.5 rounded-2xl border flex items-center gap-2 transition'
            ]"
          >
            <span class="w-5 h-5 rounded-full bg-[var(--accent-red)] text-white flex items-center justify-center font-sans font-bold text-xs shadow-xs">1</span>
            <span class="truncate max-w-[130px] sm:max-w-[170px] text-sm sm:text-base font-medium">{{ firstChoiceName || '1er choix (+3 pts)' }}</span>
          </div>

          <!-- Choix 2 : Laiton Doré -->
          <div 
            :class="[
              secondChoiceId ? 'bg-[var(--accent-brass-soft)] border-[var(--accent-brass)] text-[var(--accent-brass)] font-bold shadow-xs' : 'bg-[var(--bg-surface-inset)] border-dashed border-[var(--border-main)] text-[var(--text-faint)]',
              'px-3.5 py-2.5 rounded-2xl border flex items-center gap-2 transition'
            ]"
          >
            <span class="w-5 h-5 rounded-full bg-[var(--accent-brass)] text-white flex items-center justify-center font-sans font-bold text-xs shadow-xs">2</span>
            <span class="truncate max-w-[130px] sm:max-w-[170px] text-sm sm:text-base font-medium">{{ secondChoiceName || '2e choix (+2 pts)' }}</span>
          </div>

          <!-- Choix 3 : Zinc Étain -->
          <div 
            :class="[
              thirdChoiceId ? 'bg-[var(--accent-zinc-soft)] border-[var(--accent-zinc)] text-[var(--accent-zinc)] font-bold shadow-xs' : 'bg-[var(--bg-surface-inset)] border-dashed border-[var(--border-main)] text-[var(--text-faint)]',
              'px-3.5 py-2.5 rounded-2xl border flex items-center gap-2 transition'
            ]"
          >
            <span class="w-5 h-5 rounded-full bg-[var(--accent-zinc)] text-white flex items-center justify-center font-sans font-bold text-xs shadow-xs">3</span>
            <span class="truncate max-w-[130px] sm:max-w-[170px] text-sm sm:text-base font-medium">{{ thirdChoiceName || '3e choix (+1 pt)' }}</span>
          </div>
        </div>

        <!-- Bouton de validation (Sceau de Cire si valide) -->
        <div class="shrink-0 flex flex-col items-stretch lg:items-end">
          <button
            type="button"
            :disabled="isSubmitting || !canSubmit"
            @click="handleVoteSubmit"
            :class="[
              canSubmit
                ? 'wax-seal-btn font-serif font-bold shadow-lg cursor-pointer scale-[1.02]'
                : 'bg-[var(--bg-surface-inset)] text-[var(--text-faint)] cursor-not-allowed border border-[var(--border-main)] font-serif',
              'px-6 py-3.5 rounded-2xl text-base transition flex items-center justify-center gap-2'
            ]"
          >
            <Lock class="w-4 h-4 shrink-0" />
            <span class="text-base sm:text-lg tracking-wide">{{ isSubmitting ? 'Envoi du vote...' : submitButtonLabel }}</span>
          </button>
          <span class="text-xs sm:text-sm text-[var(--text-faint)] mt-1.5 text-center lg:text-right font-serif italic">
            Vote comptabilisé en direct • 1 vote par personne
          </span>
        </div>
      </div>

      <!-- Erreur éventuelle -->
      <div v-if="errorMessage" class="mt-3 p-3 rounded-xl bg-[var(--accent-red-soft)] border border-[var(--accent-red-border)] text-[var(--accent-red)] text-sm flex items-center gap-2 font-medium">
        <AlertCircle class="w-4 h-4 shrink-0" />
        <span>{{ errorMessage }}</span>
      </div>
    </div>

    <!-- Barre de filtrage & tri brasserie -->
    <div class="bistro-card-frame rounded-2xl p-4 sm:p-5 space-y-3 shadow-sm">
      <div class="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        <!-- Recherche textuelle -->
        <div class="relative flex-1">
          <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5 text-[var(--text-faint)]">
            <Search class="w-4 h-4" />
          </div>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Rechercher un restaurant, cuisine ou rue..."
            class="block w-full rounded-xl border border-[var(--border-main)] bg-[var(--bg-surface-inset)] pl-10 pr-3 py-2.5 text-base font-normal text-[var(--text-main)] placeholder:text-[var(--text-faint)] focus:bg-[var(--bg-surface)] focus:border-[var(--accent-brass)] focus:ring-1 focus:ring-[var(--accent-brass)]/20 focus:outline-none transition"
          />
        </div>

        <!-- Bascule de Tri : Note vs Distance -->
        <div class="flex items-center gap-1.5 shrink-0 bg-[var(--bg-surface-inset)] p-1 rounded-xl border border-[var(--border-main)]">
          <button
            type="button"
            @click="sortBy = 'rating'"
            :class="[
              sortBy === 'rating' ? 'bg-[var(--bg-surface)] text-[var(--text-main)] font-semibold border border-[var(--border-main)] shadow-xs' : 'text-[var(--text-faint)] hover:text-[var(--text-main)]',
              'px-4 py-2 rounded-lg text-sm font-serif transition flex items-center gap-1.5 cursor-pointer'
            ]"
          >
            <Star class="w-4 h-4 text-[var(--accent-brass)] fill-[var(--accent-brass)]" />
            <span>Mieux notées ⭐</span>
          </button>
          <button
            type="button"
            @click="sortBy = 'distance'"
            :class="[
              sortBy === 'distance' ? 'bg-[var(--bg-surface)] text-[var(--text-main)] font-semibold border border-[var(--border-main)] shadow-xs' : 'text-[var(--text-faint)] hover:text-[var(--text-main)]',
              'px-4 py-2 rounded-lg text-sm font-serif transition flex items-center gap-1.5 cursor-pointer'
            ]"
          >
            <Footprints class="w-4 h-4 text-[var(--accent-brass)]" />
            <span>Plus proches</span>
          </button>
        </div>
      </div>

      <!-- Filtres secondaires : Cuisines, Formules, Compteur -->
      <div class="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-[var(--border-subtle)] text-sm">
        <div class="flex flex-wrap items-center gap-2.5">
          <!-- Filtre Cuisine -->
          <div class="flex items-center gap-1.5 text-[var(--text-muted)] font-serif text-base">
            <Filter class="w-4 h-4 text-[var(--accent-brass)]" />
            <span>Spécialité :</span>
            <select
              v-model="selectedCuisine"
              class="rounded-lg border border-[var(--border-main)] bg-[var(--bg-surface-inset)] px-3 py-1.5 text-sm font-medium text-[var(--text-main)] focus:border-[var(--accent-brass)] focus:outline-none cursor-pointer"
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
                ? 'bg-[var(--accent-brass)] text-white border border-[var(--accent-brass)] font-medium shadow-xs' 
                : 'bg-[var(--bg-surface-inset)] text-[var(--text-muted)] border border-[var(--border-main)] hover:bg-[var(--bg-surface)]',
              'px-3.5 py-1.5 rounded-lg text-sm font-serif transition cursor-pointer flex items-center gap-1.5'
            ]"
          >
            <span>📜 Avec carte / menu du jour</span>
          </button>
        </div>

        <span class="text-[var(--text-faint)] font-serif text-base">
          <strong class="text-[var(--text-main)] font-semibold">{{ filteredRestaurants.length }}</strong> sur {{ restaurants.length }} adresses
        </span>
      </div>
    </div>

    <!-- Grille des tables de restaurant -->
    <div>
      <div class="flex items-center justify-between mb-4">
        <div>
          <h3 class="font-serif text-3xl sm:text-4xl font-normal text-[var(--text-main)] tracking-wide">
            Restaurants à proximité
          </h3>
          <p class="text-sm sm:text-base text-[var(--text-muted)] mt-1 font-serif italic">
            Choisissez vos 3 restaurants favoris (1er : 3 pts, 2e : 2 pts, 3e : 1 pt)
          </p>
        </div>
      </div>

      <!-- État vide si filtre trop restrictif -->
      <div v-if="filteredRestaurants.length === 0" class="bistro-card-frame rounded-2xl p-8 text-center text-[var(--text-muted)] space-y-2 shadow-sm">
        <p class="font-serif text-2xl font-normal text-[var(--text-main)]">Aucun restaurant ne correspond à vos filtres.</p>
        <p class="text-sm">Essayez de réinitialiser la recherche ou de sélectionner "Toutes les cuisines".</p>
        <button
          type="button"
          @click="searchQuery = ''; selectedCuisine = 'ALL'; onlyWithMenu = false;"
          class="mt-2 inline-flex items-center px-4 py-2 rounded-xl bg-[var(--bg-surface-inset)] border border-[var(--border-main)] text-sm font-serif font-medium text-[var(--text-main)] hover:bg-[var(--bg-surface)] cursor-pointer shadow-xs"
        >
          Réinitialiser les filtres
        </button>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-5">
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
