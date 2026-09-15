<script setup>
import { ref, computed, onMounted } from 'vue';

import { Trophy, Footprints, ExternalLink, Users, MapPin, Map as MapIcon, List, CheckCircle2, Lock, Star } from 'lucide-vue-next';
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

const rankings = computed(() => props.leaderboard?.rankings || []);
const totalVoters = computed(() => props.leaderboard?.total_voters || 0);
const voters = computed(() => props.leaderboard?.voters || []);
const winner = computed(() => rankings.value.length > 0 ? rankings.value[0] : null);

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
    <div class="bistro-card-frame rounded-3xl p-6 sm:p-7 shadow-md">
      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-[var(--border-subtle)] pb-4 mb-5">
        <div class="flex items-center gap-3.5">
          <div class="w-11 h-11 rounded-2xl bg-[var(--accent-brass-soft)] text-[var(--accent-brass)] flex items-center justify-center shrink-0 border border-[var(--accent-brass-border)] shadow-xs">
            <Users class="w-5 h-5" />
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h2 class="font-serif text-2xl sm:text-3xl font-bold text-[var(--text-main)] tracking-wide leading-tight">
                Réservation : {{ totalVoters }} {{ totalVoters <= 1 ? 'personne' : 'personnes' }}
              </h2>
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-[var(--accent-red-soft)] text-[var(--accent-red)] border border-[var(--accent-red-border)]">
                ● En direct
              </span>
            </div>
            <p class="text-xs text-[var(--text-muted)] mt-1 font-serif">
              {{ totalVoters <= 1 ? '1 personne a voté pour ce déjeuner.' : `${totalVoters} personnes ont voté et sont à compter pour la réservation.` }}
            </p>
          </div>
        </div>

        <div class="self-start sm:self-center">
          <span class="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[var(--bg-surface-inset)] border border-[var(--border-main)] text-sm font-serif font-bold text-[var(--text-main)] shadow-xs">
            <span>🍽️ Table de</span>
            <span class="text-[var(--accent-brass)] text-base font-bold">{{ totalVoters }}</span>
            <span>à réserver</span>
          </span>
        </div>
      </div>

      <!-- Liste détaillée des prénoms des votants -->
      <div class="space-y-2">
        <div class="flex items-center justify-between text-xs font-serif text-[var(--text-muted)]">
          <span class="font-bold uppercase tracking-wider text-[11px] text-[var(--text-faint)]">
            Participants ayant voté ({{ voters.length }}) :
          </span>
        </div>

        <div v-if="voters.length > 0" class="flex flex-wrap items-center gap-2 pt-1">
          <span
            v-for="(name, idx) in voters"
            :key="idx"
            :class="[
              name.toLowerCase() === currentVoterName.toLowerCase()
                ? 'badge-voter-me'
                : 'badge-voter-other',
              'px-3.5 py-1.5 rounded-xl text-xs sm:text-sm font-serif flex items-center gap-1.5 font-semibold'
            ]"
          >
            <span class="w-2 h-2 rounded-full" :class="name.toLowerCase() === currentVoterName.toLowerCase() ? 'bg-white' : 'bg-[var(--accent-brass)]'"></span>
            <span>{{ name }}</span>
            <span v-if="name.toLowerCase() === currentVoterName.toLowerCase()" class="text-[10px] opacity-90 font-sans font-normal">(vous)</span>
          </span>
        </div>
        <p v-else class="text-xs text-[var(--text-faint)] italic font-serif py-1">
          Aucun vote n'a encore été enregistré. Partagez le lien avec vos collègues pour débuter.
        </p>
      </div>

      <!-- Confirmation personnelle si l'utilisateur a voté -->
      <div v-if="myChoices" class="mt-4 pt-3.5 border-t border-[var(--border-subtle)] flex flex-wrap items-center gap-2 text-xs font-serif">
        <span class="text-[var(--text-muted)] mr-1 flex items-center gap-1 font-medium">
          <CheckCircle2 class="w-3.5 h-3.5 text-emerald-600" /> Vos 3 choix :
        </span>
        <span class="badge-choice-1 px-3 py-1 rounded-xl font-medium shadow-2xs">
          1er (3 pts) : {{ myChoices.first }}
        </span>
        <span v-if="myChoices.second" class="badge-choice-2 px-3 py-1 rounded-xl font-medium shadow-2xs">
          2e (2 pts) : {{ myChoices.second }}
        </span>
        <span v-if="myChoices.third" class="badge-choice-3 px-3 py-1 rounded-xl font-medium shadow-2xs">
          3e (1 pt) : {{ myChoices.third }}
        </span>
      </div>
    </div>

    <!-- Le restaurant en tête (« Restaurant le plus voté ») -->
    <div 
      v-if="winner && winner.points > 0"
      class="bistro-grand-frame rounded-3xl p-6 sm:p-10 relative overflow-hidden shadow-2xl"
    >
      <!-- 4 Coins Laiton Vénérable -->
      <div class="brass-corner-bracket brass-corner-tl"></div>
      <div class="brass-corner-bracket brass-corner-tr"></div>
      <div class="brass-corner-bracket brass-corner-bl"></div>
      <div class="brass-corner-bracket brass-corner-br"></div>

      <div class="relative z-10">
        <!-- Ruban de 1ère place -->
        <div class="badge-winner inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-serif font-bold uppercase tracking-wider mb-4 shadow-md">
          <Trophy class="w-4 h-4 text-amber-200 shrink-0" />
          <span>Restaurant en tête des votes</span>
        </div>

        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-6">
          <div>
            <h3 class="font-display sm:font-serif text-3xl sm:text-5xl lg:text-6xl font-normal text-[var(--text-main)] tracking-wide leading-tight">
              {{ winner.name }}
            </h3>
            <div class="flex items-center gap-3 flex-wrap mt-3">
              <p class="font-serif text-base text-[var(--text-muted)]">
                {{ winner.cuisine }}
              </p>
              <div 
                v-if="winner.rating"
                class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[var(--accent-brass-soft)] border border-[var(--accent-brass-border)] text-[var(--accent-brass)] text-xs font-serif font-bold shadow-2xs"
              >
                <Star class="w-3.5 h-3.5 fill-current" />
                <span>{{ Number(winner.rating).toFixed(1) }}</span>
                <span v-if="winner.rating_count" class="text-[10px] opacity-75 font-normal font-sans">({{ winner.rating_count }} avis)</span>
              </div>
            </div>
            <div class="flex items-center gap-2 mt-3 text-xs font-serif text-[var(--text-muted)]">
              <span class="inline-flex items-center gap-1.5 px-3.5 py-1 rounded-full bg-[var(--bg-surface-inset)] border border-[var(--border-subtle)] text-[var(--text-main)]">
                <Footprints class="w-4 h-4 text-[var(--accent-brass)]" />
                {{ winner.walking_time_min }} min à pied ({{ winner.distance_meters }} m)
              </span>
            </div>
          </div>

          <div class="flex sm:flex-col items-baseline sm:items-end justify-between sm:justify-center border-t sm:border-t-0 border-[var(--border-subtle)] pt-4 sm:pt-0 shrink-0">
            <span class="font-serif text-6xl sm:text-7xl lg:text-8xl font-normal text-[var(--accent-brass)] leading-none drop-shadow-sm">
              {{ winner.points }} <span class="font-serif text-xl text-[var(--text-faint)]">pts</span>
            </span>
            <span class="text-xs font-serif text-[var(--text-muted)] mt-2 text-right">
              {{ winner.first_votes }}x 1er • {{ winner.second_votes }}x 2e • {{ winner.third_votes }}x 3e
            </span>
          </div>
        </div>

        <div class="mt-6 pt-5 border-t border-[var(--border-subtle)] flex flex-wrap items-center gap-4 text-xs font-serif">
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
            <ExternalLink class="w-3.5 h-3.5" />
          </a>
        </div>
      </div>
    </div>

    <!-- Tableau de classement complet -->
    <div class="bistro-card-frame rounded-3xl overflow-hidden shadow-xl">
      <div class="p-5 sm:p-7 border-b border-[var(--border-main)] bg-[var(--bg-surface-subtle)] flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h3 class="font-display sm:font-serif text-2xl sm:text-3xl font-normal text-[var(--text-main)] tracking-wide">
            Classement complet des votes
          </h3>
          <p class="text-xs text-[var(--text-muted)] mt-0.5 font-serif">
            Points calculés en direct selon les votes : 1er choix (3 pts) • 2e choix (2 pts) • 3e choix (1 pt)
          </p>
        </div>

        <div class="flex items-center gap-2.5">
          <button
            type="button"
            @click="showMap = !showMap"
            class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-xl border border-[var(--border-main)] hover:border-[var(--accent-brass)] bg-[var(--bg-surface)] text-[var(--text-main)] text-xs font-serif font-medium transition cursor-pointer shadow-xs"
          >
            <MapIcon v-if="!showMap" class="w-3.5 h-3.5 text-[var(--accent-brass)]" />
            <List v-else class="w-3.5 h-3.5 text-[var(--accent-brass)]" />
            <span>{{ showMap ? 'Masquer la carte' : 'Afficher la carte' }}</span>
          </button>

          <span class="text-xs font-serif font-semibold px-3 py-1 rounded-lg bg-[var(--accent-red-soft)] text-[var(--accent-red)] border border-[var(--accent-red-border)]">
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
                'w-9 h-9 rounded-2xl flex items-center justify-center font-serif text-sm shrink-0'
              ]"
            >
              {{ item.rank }}
            </div>

            <!-- Infos Restaurant -->
            <div class="min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <span class="font-serif text-xl font-normal text-[var(--text-main)] truncate">
                  {{ item.name }}
                </span>
                <a
                  v-if="item.google_maps_url"
                  :href="item.google_maps_url"
                  target="_blank"
                  rel="noopener"
                  class="text-[var(--text-faint)] hover:text-[var(--text-main)] transition"
                  title="Fiche Google Maps"
                >
                  <MapPin class="w-3.5 h-3.5 inline" />
                </a>
                <a
                  v-if="item.website_url"
                  :href="item.website_url"
                  target="_blank"
                  rel="noopener"
                  class="text-[var(--text-faint)] hover:text-[var(--text-main)] transition"
                  title="Site web"
                >
                  <ExternalLink class="w-3 h-3 inline" />
                </a>
              </div>

              <div class="flex items-center gap-2 mt-0.5 text-xs text-[var(--text-muted)] font-serif flex-wrap">
                <span class="italic">{{ item.cuisine }}</span>
                <span v-if="item.rating" class="inline-flex items-center gap-1 text-[var(--accent-brass)] bg-[var(--accent-brass-soft)] border border-[var(--accent-brass-border)] px-2 py-0.5 rounded-full text-xs font-semibold">
                  ⭐ {{ Number(item.rating).toFixed(1) }}
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
                  'font-serif text-3xl font-normal leading-none'
                ]"
              >
                {{ item.points }}
              </span>
              <span class="text-xs font-serif text-[var(--text-faint)]">pts</span>
            </div>
            <div class="text-[11px] font-serif italic text-[var(--text-faint)] mt-1 whitespace-nowrap">
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
  </div>
</template>
