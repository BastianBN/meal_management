<script setup>
import { ref, computed, onMounted } from 'vue';

import { Trophy, Footprints, ExternalLink, Users, MapPin, Map as MapIcon, List, CheckCircle2, Lock, Star, Phone, Dices, Sparkles, X, AlertTriangle } from 'lucide-vue-next';
import RestaurantsMap from './RestaurantsMap.vue';


const props = defineProps({
  leaderboard: {
    type: Object,
    required: true,
  },
  session: {
    type: Object,
    required: true,
  },
  currentVoterName: {
    type: String,
    default: '',
  }
});

const showMap = ref(false); // Carte masquée par défaut pour mettre le classement en plein écran
const myChoices = ref(null);

// Roulette / Tirage express Top 3
const showTopDeciderModal = ref(false);
const isDeciderRolling = ref(false);
const deciderPick = ref(null);
let deciderTimer = null;

const rankings = computed(() => props.leaderboard?.rankings || []);
const totalVoters = computed(() => props.leaderboard?.total_voters || 0);
const voters = computed(() => props.leaderboard?.voters || []);
const winner = computed(() => rankings.value.length > 0 ? rankings.value[0] : null);

const winnerDetails = computed(() => {
  if (!winner.value) return null;
  const original = (props.session?.restaurants || []).find(r => r.id === winner.value.restaurant_id) || {};
  return {
    ...winner.value,
    dietary_tags: winner.value.dietary_tags || original.dietary_tags || [],
    allergen_info: winner.value.allergen_info || original.allergen_info,
    price_level: winner.value.price_level || original.price_level || 2,
    phone: winner.value.phone || original.phone,
  };
});

function getDietaryBadges(tags) {
  const map = {
    vegetarian: { label: 'Végétarien', icon: '🌿', class: 'bg-emerald-600 text-white shadow-sm border-emerald-700 dark:bg-emerald-500 dark:text-white dark:border-emerald-600 font-medium' },
    vegan: { label: 'Végan', icon: '🌱', class: 'bg-green-500/15 text-green-800 dark:text-green-300 border-green-500/30' },
    gluten_free: { label: 'Sans gluten', icon: '🌾', class: 'bg-amber-500/15 text-amber-800 dark:text-amber-300 border-amber-500/30' },
    halal: { label: 'Halal', icon: '☪️', class: 'bg-teal-500/15 text-teal-800 dark:text-teal-300 border-teal-500/30' },
  };
  return (tags || []).filter(t => map[t]).map(t => map[t]);
}

function openTopDecider() {
  const topList = rankings.value.slice(0, 3);
  if (topList.length === 0) return;
  showTopDeciderModal.value = true;
  triggerDecider();
}

function triggerDecider() {
  const topList = rankings.value.slice(0, 3);
  if (topList.length === 0) return;
  isDeciderRolling.value = true;
  let counter = 0;
  const maxIterations = 14;
  if (deciderTimer) clearInterval(deciderTimer);

  deciderTimer = setInterval(() => {
    counter++;
    const randomIdx = Math.floor(Math.random() * topList.length);
    deciderPick.value = topList[randomIdx];
    if (counter >= maxIterations) {
      clearInterval(deciderTimer);
      isDeciderRolling.value = false;
    }
  }, 85);
}

// Associer les coordonnées des restaurants pour la carte
const restaurantsWithCoords = computed(() => {
  const mapCoords = new Map((props.session?.restaurants || []).map(r => [r.id, r]));
  return rankings.value.map(item => {
    const original = mapCoords.get(item.restaurant_id) || {};
    return {
      ...item,
      id: item.restaurant_id,
      latitude: original.latitude,
      longitude: original.longitude,
      lunch_formulas: original.lunch_formulas || [],
      menu_summary: original.menu_summary || '',
      google_maps_url: item.google_maps_url || original.google_maps_url,
      website_url: item.website_url || original.website_url,
      menu_url: item.menu_url || original.menu_url,
      dietary_tags: item.dietary_tags || original.dietary_tags || [],
      allergen_info: item.allergen_info || original.allergen_info,
      price_level: item.price_level || original.price_level || 2,
      phone: item.phone || original.phone,
    };
  });
});

onMounted(() => {
  try {
    const raw = localStorage.getItem(`meal_choices_${props.session.id}`);
    if (raw) {
      myChoices.value = JSON.parse(raw);
    }
  } catch (err) {
    // Ignorer si localStorage indisponible
  }
});
</script>

<template>
  <div class="space-y-7">
    <!-- 1. Récapitulatif Réservation & Liste des Votants (Pour savoir combien réserver) -->
    <div class="bistro-card-frame rounded-3xl p-6 sm:p-8 shadow-md">
      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-[var(--border-subtle)] pb-4 mb-5">
        <div class="flex items-center gap-3.5">
          <div class="w-12 h-12 rounded-2xl bg-[var(--accent-brass-soft)] text-[var(--accent-brass)] flex items-center justify-center shrink-0 border border-[var(--accent-brass-border)] shadow-xs">
            <Users class="w-6 h-6" />
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h2 class="results-reservation-title font-serif text-3xl sm:text-4xl font-bold text-[var(--text-main)] tracking-wide leading-tight">
                Réservation : {{ totalVoters }} {{ totalVoters <= 1 ? 'personne' : 'personnes' }}
              </h2>
              <span class="inline-flex items-center px-3 py-1 rounded-full text-xs sm:text-sm font-semibold bg-[var(--accent-red-soft)] text-[var(--accent-red)] border border-[var(--accent-red-border)]">
                ● En direct
              </span>
            </div>
            <p class="text-sm sm:text-base text-[var(--text-muted)] mt-1.5 font-serif">
              {{ totalVoters <= 1 ? '1 personne a voté pour ce déjeuner.' : `${totalVoters} personnes ont voté et sont à compter pour la réservation.` }}
            </p>
          </div>
        </div>

        <div class="self-start sm:self-center">
          <span class="results-table-badge inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[var(--bg-surface-inset)] border border-[var(--border-main)] text-base font-serif font-bold text-[var(--text-main)] shadow-xs">
            <span>🍽️ Table de</span>
            <span class="text-[var(--accent-brass)] text-lg font-bold">{{ totalVoters }}</span>
            <span>à réserver</span>
          </span>
        </div>
      </div>

      <!-- Liste détaillée des prénoms des votants -->
      <div class="space-y-2.5">
        <div class="flex items-center justify-between text-sm font-serif text-[var(--text-muted)]">
          <span class="font-bold uppercase tracking-wider text-xs sm:text-sm text-[var(--text-muted)]">
            Participants ayant voté ({{ voters.length }}) :
          </span>
        </div>

        <div v-if="voters.length > 0" class="flex flex-wrap items-center gap-2.5 pt-1">
          <span
            v-for="(name, idx) in voters"
            :key="idx"
            :class="[
              name.toLowerCase() === currentVoterName.toLowerCase()
                ? 'badge-voter-me'
                : 'badge-voter-other',
              'px-4 py-2 rounded-xl text-sm sm:text-base font-serif flex items-center gap-2 font-semibold'
            ]"
          >
            <span class="w-2 h-2 rounded-full" :class="name.toLowerCase() === currentVoterName.toLowerCase() ? 'bg-white' : 'bg-[var(--accent-brass)]'"></span>
            <span>{{ name }}</span>
            <span v-if="name.toLowerCase() === currentVoterName.toLowerCase()" class="text-xs opacity-90 font-sans font-normal">(vous)</span>
          </span>
        </div>
        <p v-else class="text-sm text-[var(--text-faint)] italic font-serif py-1">
          Aucun vote n'a encore été enregistré. Partagez le lien avec vos collègues pour débuter.
        </p>
      </div>

      <!-- Confirmation personnelle si l'utilisateur a voté -->
      <div v-if="myChoices" class="mt-4 pt-4 border-t border-[var(--border-subtle)] flex flex-wrap items-center gap-2.5 text-sm sm:text-base font-serif">
        <span class="text-[var(--text-muted)] mr-1 flex items-center gap-1.5 font-medium">
          <CheckCircle2 class="w-4 h-4 text-emerald-600" /> Vos 3 choix :
        </span>
        <span class="badge-choice-1 px-3.5 py-1 rounded-xl font-medium shadow-2xs">
          1er (3 pts) : {{ myChoices.first }}
        </span>
        <span v-if="myChoices.second" class="badge-choice-2 px-3.5 py-1 rounded-xl font-medium shadow-2xs">
          2e (2 pts) : {{ myChoices.second }}
        </span>
        <span v-if="myChoices.third" class="badge-choice-3 px-3.5 py-1 rounded-xl font-medium shadow-2xs">
          3e (1 pt) : {{ myChoices.third }}
        </span>
      </div>
    </div>

    <!-- Le restaurant en tête (« Restaurant le plus voté ») -->
    <div 
      v-if="winner && winner.points > 0"
      class="bistro-grand-frame rounded-3xl p-6 sm:p-10 relative shadow-2xl"
    >
      <!-- Suspension à corde et anneaux en fonte (Ardoise) -->
      <div class="chalk-suspension-container">
        <div class="chalk-nail-top"></div>
        <div class="chalk-rope-left"></div>
        <div class="chalk-rope-right"></div>
        <div class="chalk-ring-left"></div>
        <div class="chalk-ring-right"></div>
      </div>

      <!-- 4 Coins Laiton Vénérable -->
      <div class="brass-corner-bracket brass-corner-tl"></div>
      <div class="brass-corner-bracket brass-corner-tr"></div>
      <div class="brass-corner-bracket brass-corner-bl"></div>
      <div class="brass-corner-bracket brass-corner-br"></div>

      <!-- Rebord porte-craie en bois avec craies et effaceur (Ardoise) -->
      <div class="chalk-ledge-container">
        <div class="chalk-ledge-groove">
          <div class="flex items-center gap-2">
            <span class="chalk-stick chalk-stick-white" title="Craie blanche"></span>
            <span class="chalk-stick chalk-stick-yellow" title="Craie jaune bistrot"></span>
            <span class="chalk-stick chalk-stick-coral" title="Craie rouge"></span>
          </div>
          <div class="flex items-center gap-2">
            <span class="chalk-eraser" title="Effaceur de bistrot"></span>
          </div>
        </div>
      </div>

      <div class="relative z-10">
        <!-- Ruban de 1ère place -->
        <div class="badge-winner inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs sm:text-sm font-serif font-bold uppercase tracking-wider mb-4 shadow-md">
          <Trophy class="w-4 h-4 text-amber-200 shrink-0" />
          <span>Restaurant en tête des votes</span>
        </div>

        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-6">
          <div>
            <h3 class="results-winner-title font-display sm:font-serif text-3xl sm:text-5xl lg:text-6xl font-normal text-[var(--text-main)] tracking-wide leading-tight">
              {{ winner.name }}
            </h3>
            <div class="flex items-center gap-3 flex-wrap mt-3">
              <p class="font-serif text-base sm:text-lg font-medium text-[var(--text-muted)]">
                {{ winner.cuisine }}
              </p>
              <div 
                v-if="winner.rating"
                class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[var(--accent-brass-soft)] border border-[var(--accent-brass-border)] text-[var(--accent-brass)] text-sm font-serif font-bold shadow-2xs"
              >
                <Star class="w-3.5 h-3.5 fill-current" />
                <span>{{ Number(winner.rating).toFixed(1) }}</span>
                <span v-if="winner.rating_count" class="text-xs opacity-75 font-normal font-sans">({{ winner.rating_count }} avis)</span>
              </div>

              <!-- Badge Prix Vainqueur -->
              <span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-serif font-bold bg-[var(--bg-surface-inset)] text-[var(--text-muted)] border border-[var(--border-subtle)]">
                {{ winnerDetails?.price_level === 1 ? '€ (Éco)' : winnerDetails?.price_level === 3 ? '€€€ (Gourmet)' : '€€ (Moyen)' }}
              </span>
            </div>

            <!-- Badges Régimes Alimentaires & Allergies du Vainqueur -->
            <div v-if="getDietaryBadges(winnerDetails?.dietary_tags).length > 0 || winnerDetails?.allergen_info" class="flex flex-wrap items-center gap-1.5 mt-3">
              <span 
                v-for="(badge, bIdx) in getDietaryBadges(winnerDetails?.dietary_tags)" 
                :key="bIdx"
                :class="['inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-serif font-medium border shadow-2xs', badge.class]"
              >
                <span>{{ badge.icon }}</span>
                <span>{{ badge.label }}</span>
              </span>

              <span 
                v-if="winnerDetails?.allergen_info" 
                class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-serif bg-amber-500/15 text-amber-900 dark:text-amber-200 border border-amber-500/30"
                :title="winnerDetails.allergen_info"
              >
                <AlertTriangle class="w-3 h-3 text-amber-600 dark:text-amber-400 shrink-0" />
                <span>{{ winnerDetails.allergen_info }}</span>
              </span>
            </div>

            <div class="flex items-center gap-2 mt-3 text-sm sm:text-base font-serif text-[var(--text-muted)]">
              <span class="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-[var(--bg-surface-inset)] border border-[var(--border-subtle)] text-[var(--text-main)]">
                <Footprints class="w-4 h-4 text-[var(--accent-brass)]" />
                {{ winner.walking_time_min }} min à pied ({{ winner.distance_meters }} m)
              </span>
            </div>
          </div>

          <div class="flex sm:flex-col items-baseline sm:items-end justify-between sm:justify-center border-t sm:border-t-0 border-[var(--border-subtle)] pt-4 sm:pt-0 shrink-0">
            <span class="results-winner-points font-serif text-6xl sm:text-7xl lg:text-8xl font-normal text-[var(--accent-brass)] leading-none drop-shadow-sm">
              {{ winner.points }} <span class="font-serif text-xl sm:text-2xl text-[var(--text-faint)]">pts</span>
            </span>
            <span class="text-sm font-serif text-[var(--text-muted)] mt-2 text-right">
              {{ winner.first_votes }}x 1er • {{ winner.second_votes }}x 2e • {{ winner.third_votes }}x 3e
            </span>
          </div>
        </div>

        <!-- Liens d'action et réservation -->
        <div class="mt-6 pt-5 border-t border-[var(--border-subtle)] flex flex-wrap items-center gap-4 text-sm sm:text-base font-serif">
          <!-- Bouton Appel Téléphonique Direct -->
          <a 
            v-if="winnerDetails?.phone"
            :href="'tel:' + winnerDetails.phone"
            class="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-[var(--accent-brass-soft)] hover:bg-[var(--accent-brass)] hover:text-white text-[var(--accent-brass)] border border-[var(--accent-brass-border)] font-semibold transition shadow-xs cursor-pointer"
            :title="`Appeler : ${winnerDetails.phone}`"
          >
            <Phone class="w-4 h-4" />
            <span>Appeler pour réserver ({{ winnerDetails.phone }})</span>
          </a>

          <a 
            v-if="winner.google_maps_url"
            :href="winner.google_maps_url"
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex items-center gap-1.5 text-[var(--text-muted)] hover:text-[var(--text-main)] transition underline underline-offset-4"
          >
            <MapPin class="w-4 h-4 text-[var(--text-faint)]" />
            <span>Fiche Google & Avis</span>
          </a>

          <a 
            v-if="winner.website_url"
            :href="winner.website_url"
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex items-center gap-1.5 font-semibold text-[var(--accent-brass)] hover:underline underline-offset-4 transition"
          >
            <span>Site officiel</span>
            <ExternalLink class="w-4 h-4" />
          </a>
        </div>
      </div>
    </div>

    <!-- Tableau de classement complet -->
    <div class="bistro-card-frame rounded-3xl overflow-hidden shadow-xl">
      <div class="p-5 sm:p-7 border-b border-[var(--border-main)] bg-[var(--bg-surface-subtle)] flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h3 class="results-ranking-title font-display sm:font-serif text-2xl sm:text-3xl font-normal text-[var(--text-main)] tracking-wide">
            Classement complet des votes
          </h3>
          <p class="text-sm sm:text-base text-[var(--text-muted)] mt-1 font-serif">
            Points calculés en direct selon les votes : 1er choix (3 pts) • 2e choix (2 pts) • 3e choix (1 pt)
          </p>
        </div>

        <div class="flex flex-wrap items-center gap-2.5">
          <!-- Bouton Décider entre le Top 3 -->
          <button
            v-if="rankings.length >= 2"
            type="button"
            @click="openTopDecider"
            class="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-gradient-to-r from-amber-600 via-amber-500 to-amber-700 text-white text-xs sm:text-sm font-serif font-bold shadow-xs hover:scale-[1.02] active:scale-[0.98] transition cursor-pointer border border-amber-300/30"
            title="Tirer au sort entre les favoris"
          >
            <Dices class="w-4 h-4" />
            <span>Départager le Top 3</span>
          </button>

          <button
            type="button"
            @click="showMap = !showMap"
            class="inline-flex items-center gap-2 px-4 py-2 rounded-xl border border-[var(--border-main)] hover:border-[var(--accent-brass)] bg-[var(--bg-surface)] text-[var(--text-main)] text-sm font-serif font-medium transition cursor-pointer shadow-xs"
          >
            <MapIcon v-if="!showMap" class="w-4 h-4 text-[var(--accent-brass)]" />
            <List v-else class="w-4 h-4 text-[var(--accent-brass)]" />
            <span>{{ showMap ? 'Masquer la carte' : 'Afficher la carte' }}</span>
          </button>

          <span class="text-xs sm:text-sm font-serif font-semibold px-3.5 py-1 rounded-lg bg-[var(--accent-red-soft)] text-[var(--accent-red)] border border-[var(--accent-red-border)]">
            ● En direct
          </span>
        </div>
      </div>

      <div class="divide-y divide-[var(--border-subtle)]">
        <div 
          v-for="item in rankings" 
          :key="item.restaurant_id"
          :class="[
            item.rank === 1 ? 'bg-[var(--accent-brass-soft)]/40' : 'hover:bg-[var(--bg-surface-subtle)]',
            'p-4 sm:p-5 flex items-center justify-between gap-4 transition'
          ]"
        >
          <div class="flex items-center gap-4 min-w-0">
            <!-- Badge de Rang Trio Bistrot -->
            <div 
              :class="[
                item.rank === 1 ? 'bg-[var(--accent-red)] text-white font-bold shadow-md' :
                item.rank === 2 ? 'bg-[var(--accent-brass)] text-white font-bold shadow-md' :
                item.rank === 3 ? 'bg-[var(--accent-zinc)] text-white font-bold shadow-md' :
                'bg-[var(--bg-surface-inset)] text-[var(--text-faint)] font-medium border border-[var(--border-subtle)]',
                'results-rank-badge w-10 h-10 rounded-2xl flex items-center justify-center font-serif text-base shrink-0'
              ]"
            >
              {{ item.rank }}
            </div>

            <!-- Infos Restaurant -->
            <div class="min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <span class="results-ranking-name font-serif text-xl sm:text-2xl font-normal text-[var(--text-main)] truncate">
                  {{ item.name }}
                </span>
                <a
                  v-if="item.phone"
                  :href="'tel:' + item.phone"
                  class="text-[var(--accent-brass)] hover:underline transition"
                  :title="`Appeler : ${item.phone}`"
                >
                  <Phone class="w-3.5 h-3.5 inline" />
                </a>
                <a
                  v-if="item.google_maps_url"
                  :href="item.google_maps_url"
                  target="_blank"
                  rel="noopener"
                  class="text-[var(--text-faint)] hover:text-[var(--text-main)] transition"
                  title="Fiche Google Maps"
                >
                  <MapPin class="w-4 h-4 inline" />
                </a>
                <a
                  v-if="item.website_url"
                  :href="item.website_url"
                  target="_blank"
                  rel="noopener"
                  class="text-[var(--text-faint)] hover:text-[var(--text-main)] transition"
                  title="Site web"
                >
                  <ExternalLink class="w-3.5 h-3.5 inline" />
                </a>
              </div>

              <div class="flex items-center gap-2 mt-1 text-sm sm:text-base text-[var(--text-muted)] font-serif flex-wrap">
                <span class="italic">{{ item.cuisine }}</span>
                <span v-if="item.rating" class="inline-flex items-center gap-1 text-[var(--accent-brass)] bg-[var(--accent-brass-soft)] border border-[var(--accent-brass-border)] px-2.5 py-0.5 rounded-full text-xs sm:text-sm font-semibold">
                  ⭐ {{ Number(item.rating).toFixed(1) }}
                </span>
                <!-- Badges régimes miniatures -->
                <span 
                  v-for="(b, bI) in getDietaryBadges(item.dietary_tags)" 
                  :key="bI"
                  class="text-xs px-2 py-0.5 rounded-full bg-[var(--bg-surface-inset)] border border-[var(--border-subtle)]"
                  :title="b.label"
                >
                  {{ b.icon }}
                </span>
                <span class="text-[var(--text-faint)]">•</span>
                <span>{{ item.walking_time_min }} min ({{ item.distance_meters }} m)</span>
              </div>
            </div>
          </div>

          <!-- Total des Points et Détails des votes -->
          <div class="text-right shrink-0">
            <div class="flex items-baseline justify-end gap-1">
              <span 
                :class="[
                  item.rank === 1 ? 'text-[var(--accent-brass)] font-semibold' : 'text-[var(--text-main)]',
                  'results-ranking-points font-serif text-3xl sm:text-4xl font-normal leading-none'
                ]"
              >
                {{ item.points }}
              </span>
              <span class="text-sm font-serif text-[var(--text-faint)]">pts</span>
            </div>
            <div class="text-xs sm:text-sm font-serif italic text-[var(--text-muted)] mt-1 whitespace-nowrap">
              {{ item.first_votes }}x 1er • {{ item.second_votes }}x 2e • {{ item.third_votes }}x 3e
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Carte des restaurants sous le classement -->
    <div v-show="showMap" class="transition-all duration-300">
      <RestaurantsMap
        :departure="{
          address: session.departure_address,
          latitude: session.latitude,
          longitude: session.longitude,
          radius_meters: session.radius_meters
        }"
        :restaurants="restaurantsWithCoords"
        :selected-rankings="{
          firstChoiceId: winner ? winner.restaurant_id : null
        }"
      />
    </div>

    <!-- Modal Tirage Top 3 : Départager les favoris -->
    <div 
      v-if="showTopDeciderModal" 
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs transition-opacity duration-200"
    >
      <div class="bistro-card-frame rounded-3xl p-6 sm:p-8 max-w-lg w-full shadow-2xl relative border-2 border-[var(--accent-brass)]">
        <button
          type="button"
          @click="showTopDeciderModal = false"
          class="absolute top-4 right-4 p-2 rounded-full text-[var(--text-muted)] hover:text-[var(--text-main)] hover:bg-[var(--bg-surface-inset)] transition cursor-pointer"
        >
          <X class="w-5 h-5" />
        </button>

        <div class="text-center mb-6">
          <div class="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-[var(--accent-brass-soft)] text-[var(--accent-brass)] border border-[var(--accent-brass-border)] mb-3 shadow-xs">
            <Dices class="w-8 h-8 stroke-[2.2]" />
          </div>
          <h3 class="font-serif text-3xl font-normal text-[var(--text-main)]">
            Départager le Top 3
          </h3>
          <p class="text-sm text-[var(--text-muted)] font-serif italic mt-1">
            Tirage au sort express entre les favoris du groupe !
          </p>
        </div>

        <div class="p-6 rounded-2xl bg-[var(--bg-surface-inset)] border border-[var(--border-main)] text-center mb-6 min-h-[160px] flex flex-col items-center justify-center">
          <div v-if="isDeciderRolling" class="space-y-3">
            <div class="inline-block animate-spin text-3xl">🎲</div>
            <p class="font-serif text-xl font-bold text-[var(--accent-brass)] animate-pulse">
              {{ deciderPick ? deciderPick.name : 'Suspense du chef...' }}
            </p>
            <p class="text-xs text-[var(--text-muted)] font-serif italic">Le sort est en train d'être scellé...</p>
          </div>

          <div v-else-if="deciderPick" class="space-y-3 w-full">
            <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-serif font-bold uppercase bg-[var(--accent-brass-soft)] text-[var(--accent-brass)] border border-[var(--accent-brass-border)]">
              <Sparkles class="w-3.5 h-3.5" />
              Choix officiel de la roulette
            </span>
            <h4 class="font-serif text-2xl sm:text-3xl font-bold text-[var(--text-main)] leading-tight">
              {{ deciderPick.name }}
            </h4>
            <div class="flex flex-wrap items-center justify-center gap-2 text-sm text-[var(--text-muted)] font-serif">
              <span>❧ {{ deciderPick.cuisine }} ☙</span>
              <span>•</span>
              <span>{{ deciderPick.points }} points</span>
              <span>•</span>
              <span>{{ deciderPick.walking_time_min }} min</span>
            </div>
          </div>
        </div>

        <div v-if="!isDeciderRolling && deciderPick" class="flex items-center justify-center gap-3">
          <a
            v-if="deciderPick.google_maps_url"
            :href="deciderPick.google_maps_url"
            target="_blank"
            rel="noopener"
            class="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[var(--accent-red)] text-white font-serif font-semibold text-sm shadow-md hover:bg-[var(--accent-red)]/90 transition cursor-pointer"
          >
            <MapPin class="w-4 h-4" />
            <span>Voir l'itinéraire</span>
          </a>
          <button
            type="button"
            @click="triggerDecider"
            class="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl border border-[var(--border-main)] hover:border-[var(--accent-brass)] bg-[var(--bg-surface-inset)] text-[var(--text-main)] text-sm font-serif font-medium transition cursor-pointer"
          >
            <Dices class="w-4 h-4 text-[var(--accent-brass)]" />
            <span>Relancer 🎲</span>
          </button>
          <button
            type="button"
            @click="showTopDeciderModal = false"
            class="px-4 py-2.5 rounded-xl text-sm font-serif text-[var(--text-muted)] hover:text-[var(--text-main)] cursor-pointer"
          >
            Fermer
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
