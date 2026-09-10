<script setup>
import { ref, computed } from 'vue';
import RestaurantCard from './RestaurantCard.vue';
import { submitVote } from '../api';
import { Share2, MapPin, Footprints, AlertCircle, CheckCircle2, User, Lock } from 'lucide-vue-next';

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

const restaurants = computed(() => props.session.restaurants || []);

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

async function copyShareLink() {
  const url = window.location.href;
  try {
    await navigator.clipboard.writeText(url);
    copySuccess.value = true;
    setTimeout(() => {
      copySuccess.value = false;
    }, 3000);
  } catch (err) {
    // Fallback manuel
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

    // Enregistrer localement que cet utilisateur a voté pour cette session
    localStorage.setItem(`meal_voter_${props.session.id}`, name);

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
    <!-- En-tête de la session : Adresse, Rayon, Partage -->
    <div class="bg-white rounded-2xl border border-slate-200 p-5 sm:p-6 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <div class="flex items-center gap-2 text-xs font-semibold text-brand-700 mb-1">
          <MapPin class="w-4 h-4 text-brand-600 shrink-0" />
          <span>Lieu de départ :</span>
        </div>
        <h2 class="text-lg sm:text-xl font-bold text-slate-900 leading-snug">
          {{ session.departure_address }}
        </h2>
        <p class="text-xs text-slate-500 mt-1 flex items-center gap-1.5">
          <Footprints class="w-3.5 h-3.5 text-slate-400" />
          <span>Rayon : {{ session.radius_meters }} mètres (~{{ Math.round(session.radius_meters / 80) }} min max à pied)</span>
          <span>•</span>
          <span>{{ restaurants.length }} restaurants détectés</span>
        </p>
      </div>

      <!-- Bouton copier le lien -->
      <div class="shrink-0">
        <button
          type="button"
          @click="copyShareLink"
          class="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl border border-slate-200 hover:border-slate-300 bg-slate-50 hover:bg-slate-100 text-slate-700 text-sm font-semibold transition btn-interaction cursor-pointer"
        >
          <CheckCircle2 v-if="copySuccess" class="w-4 h-4 text-emerald-600" />
          <Share2 v-else class="w-4 h-4 text-slate-500" />
          <span>{{ copySuccess ? 'Lien d’invitation copié !' : 'Partager le lien de vote' }}</span>
        </button>
      </div>
    </div>

    <!-- Barre récapitulative des choix du votant -->
    <div class="bg-white rounded-2xl border border-slate-200 p-5 sm:p-6 shadow-xs sticky top-4 z-20 backdrop-blur-md bg-white/95">
      <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <!-- Champ nom du votant -->
        <div class="flex-1 max-w-xs">
          <label for="voter-name" class="block text-xs font-semibold text-slate-700 mb-1">
            Votre prénom ou nom
          </label>
          <div class="relative rounded-lg shadow-xs">
            <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">
              <User class="h-4 w-4" />
            </div>
            <input
              id="voter-name"
              v-model="voterName"
              type="text"
              required
              placeholder="ex : Alexandre, Sophie..."
              class="block w-full rounded-lg border border-slate-300 pl-9 pr-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:border-brand-600 focus:ring-2 focus:ring-brand-500/20 focus:outline-none"
            />
          </div>
        </div>

        <!-- Récapitulatif des 3 choix -->
        <div class="flex-2 flex flex-wrap items-center gap-2 text-xs">
          <div :class="['px-3 py-2 rounded-xl border flex items-center gap-1.5', firstChoiceId ? 'bg-amber-50 border-amber-300 text-amber-900 font-semibold' : 'bg-slate-50 border-slate-200 text-slate-400']">
            <span class="w-5 h-5 rounded-full bg-amber-500 text-white flex items-center justify-center font-bold text-[10px]">1</span>
            <span class="truncate max-w-[140px]">{{ firstChoiceName || '1er choix (3 pts)' }}</span>
          </div>

          <div :class="['px-3 py-2 rounded-xl border flex items-center gap-1.5', secondChoiceId ? 'bg-slate-100 border-slate-300 text-slate-900 font-semibold' : 'bg-slate-50 border-slate-200 text-slate-400']">
            <span class="w-5 h-5 rounded-full bg-slate-600 text-white flex items-center justify-center font-bold text-[10px]">2</span>
            <span class="truncate max-w-[140px]">{{ secondChoiceName || '2e choix (2 pts)' }}</span>
          </div>

          <div :class="['px-3 py-2 rounded-xl border flex items-center gap-1.5', thirdChoiceId ? 'bg-amber-100/50 border-amber-300 text-amber-950 font-semibold' : 'bg-slate-50 border-slate-200 text-slate-400']">
            <span class="w-5 h-5 rounded-full bg-amber-800 text-white flex items-center justify-center font-bold text-[10px]">3</span>
            <span class="truncate max-w-[140px]">{{ thirdChoiceName || '3e choix (1 pt)' }}</span>
          </div>
        </div>

        <!-- Bouton Soumettre le vote -->
        <div class="shrink-0 flex flex-col items-end">
          <button
            type="button"
            :disabled="isSubmitting || !firstChoiceId || !voterName.trim()"
            @click="handleVoteSubmit"
            class="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 disabled:opacity-50 text-white font-semibold text-sm shadow-xs transition btn-interaction cursor-pointer"
          >
            <Lock class="w-4 h-4" />
            <span>{{ isSubmitting ? 'Enregistrement...' : 'Valider mon vote (Définitif)' }}</span>
          </button>
          <span class="text-[11px] text-slate-400 mt-1">Vote définitif • non modifiable</span>
        </div>
      </div>

      <!-- Erreur éventuelle -->
      <div v-if="errorMessage" class="mt-3 p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2">
        <AlertCircle class="w-4 h-4 text-red-500 shrink-0" />
        <span>{{ errorMessage }}</span>
      </div>
    </div>

    <!-- Grille des restaurants -->
    <div>
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-base font-bold text-slate-900">
          Sélectionnez vos 3 préférences
        </h3>
        <span class="text-xs text-slate-500">
          Cliquez sur 1er, 2e ou 3e pour attribuer vos points
        </span>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <RestaurantCard
          v-for="r in restaurants"
          :key="r.id"
          :restaurant="r"
          :current-rank="getRestaurantRank(r.id)"
          @toggle-rank="handleToggleRank"
        />
      </div>
    </div>
  </div>
</template>
