<script setup>
import { ref, computed } from 'vue';
import { Trophy, Footprints, ExternalLink, Users, MapPin, Map as MapIcon, List } from 'lucide-vue-next';
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

const showMap = ref(true);
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
</script>

<template>
  <div class="space-y-6">
    <!-- Statut en direct et participation -->
    <div class="bg-white rounded-2xl border border-slate-200 p-5 sm:p-6 shadow-xs">
      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-100 pb-4 mb-4">
        <div class="flex items-center gap-2.5">
          <span class="relative flex h-3 w-3">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
          </span>
          <h2 class="text-xl font-extrabold text-slate-900">
            Résultats en direct
          </h2>
          <span class="text-xs font-bold px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200">
            Temps réel
          </span>
        </div>

        <div class="flex items-center gap-4">
          <button
            type="button"
            @click="showMap = !showMap"
            class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-slate-300 hover:border-slate-400 bg-white text-slate-700 text-xs font-bold transition btn-interaction cursor-pointer"
          >
            <MapIcon v-if="!showMap" class="w-3.5 h-3.5 text-slate-500" />
            <List v-else class="w-3.5 h-3.5 text-slate-500" />
            <span>{{ showMap ? 'Masquer la carte' : 'Afficher la carte' }}</span>
          </button>

          <div class="flex items-center gap-2 text-sm text-slate-600">
            <Users class="w-4 h-4 text-slate-400" />
            <span class="font-extrabold text-slate-900">{{ totalVoters }}</span>
            <span>{{ totalVoters <= 1 ? 'collègue a voté' : 'collègues ont voté' }}</span>
          </div>
        </div>
      </div>

      <!-- Liste des votants -->
      <div v-if="voters.length > 0" class="flex flex-wrap items-center gap-2 text-xs text-slate-600">
        <span class="font-bold text-slate-500 mr-1">Participants :</span>
        <span
          v-for="(name, idx) in voters"
          :key="idx"
          :class="[
            name.toLowerCase() === currentVoterName.toLowerCase()
              ? 'bg-orange-100 text-orange-950 font-extrabold ring-1 ring-orange-300'
              : 'bg-slate-100 text-slate-800 font-semibold',
            'px-3 py-1 rounded-lg'
          ]"
        >
          {{ name }} {{ name.toLowerCase() === currentVoterName.toLowerCase() ? '(vous)' : '' }}
        </span>
      </div>
      <div v-else class="text-xs text-slate-400 italic">
        En attente des premiers votes...
      </div>
    </div>

    <!-- Carte des restaurants en direct -->
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

    <!-- Le restaurant en tête (Gagnant actuel) -->
    <div 
      v-if="winner && winner.points > 0"
      class="rounded-2xl bg-gradient-to-br from-amber-500/15 via-amber-50/40 to-white border-2 border-amber-400 p-6 sm:p-8 shadow-sm relative overflow-hidden"
    >
      <div class="flex items-center gap-2 text-xs font-extrabold text-amber-900 uppercase tracking-wider mb-2">
        <Trophy class="w-4 h-4 text-amber-600 shrink-0" />
        <span>En tête pour le déjeuner de ce midi</span>
      </div>

      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h3 class="text-2xl font-black text-slate-900">
            {{ winner.name }}
          </h3>
          <p class="text-sm font-medium text-slate-600 mt-0.5">
            {{ winner.cuisine }}
          </p>
          <div class="flex items-center gap-2 mt-2 text-xs font-semibold text-slate-600">
            <Footprints class="w-4 h-4 text-emerald-600" />
            <span>{{ winner.walking_time_min }} min à pied ({{ winner.distance_meters }} m)</span>
          </div>
        </div>

        <div class="flex sm:flex-col items-baseline sm:items-end justify-between sm:justify-center border-t sm:border-t-0 border-amber-200 pt-3 sm:pt-0">
          <span class="text-3xl font-black text-amber-600">
            {{ winner.points }} <span class="text-sm font-bold text-slate-600">points</span>
          </span>
          <span class="text-xs font-medium text-slate-500 mt-1">
            {{ winner.first_votes }}x 1er (3 pts) • {{ winner.second_votes }}x 2e (2 pts) • {{ winner.third_votes }}x 3e (1 pt)
          </span>
        </div>
      </div>

      <div class="mt-4 pt-3 border-t border-amber-200/60 flex flex-wrap items-center gap-4 text-xs">
        <a 
          v-if="winner.google_maps_url"
          :href="winner.google_maps_url"
          target="_blank"
          rel="noopener noreferrer"
          class="inline-flex items-center gap-1.5 font-bold text-blue-700 hover:text-blue-900 underline"
        >
          <MapPin class="w-3.5 h-3.5 text-blue-600" />
          <span>Fiche Google Maps & Avis</span>
        </a>

        <a 
          v-if="winner.website_url"
          :href="winner.website_url"
          target="_blank"
          rel="noopener noreferrer"
          class="inline-flex items-center gap-1.5 font-bold text-amber-900 hover:text-amber-950 underline"
        >
          <span>Accéder au site officiel</span>
          <ExternalLink class="w-3.5 h-3.5" />
        </a>
      </div>
    </div>

    <!-- Tableau / Liste complète du classement -->
    <div class="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
      <div class="p-4 sm:p-5 border-b border-slate-100 bg-slate-50/70 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <h3 class="text-sm font-extrabold text-slate-900">
          Classement complet des établissements
        </h3>
        <span class="text-xs text-slate-500 font-medium">
          Barème : 1er (3 pts) • 2e (2 pts) • 3e (1 pt)
        </span>
      </div>

      <div class="divide-y divide-slate-100">
        <div 
          v-for="item in rankings" 
          :key="item.restaurant_id"
          class="p-4 sm:p-5 flex items-center justify-between gap-4 hover:bg-slate-50/70 transition"
        >
          <div class="flex items-center gap-3.5 min-w-0">
            <!-- Badge de Rang -->
            <div 
              :class="[
                item.rank === 1 ? 'bg-amber-500 text-white font-black ring-2 ring-amber-400 shadow-xs' :
                item.rank === 2 ? 'bg-slate-700 text-white font-bold' :
                item.rank === 3 ? 'bg-amber-900 text-white font-bold' :
                'bg-slate-100 text-slate-500 font-semibold',
                'w-8 h-8 rounded-xl flex items-center justify-center text-sm shrink-0'
              ]"
            >
              {{ item.rank }}
            </div>

            <div class="min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <h4 class="text-sm sm:text-base font-bold text-slate-900 truncate">
                  {{ item.name }}
                </h4>
                <a 
                  v-if="item.google_maps_url"
                  :href="item.google_maps_url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="text-blue-500 hover:text-blue-700 transition shrink-0"
                  title="Voir la fiche Google"
                >
                  <MapPin class="w-3.5 h-3.5" />
                </a>
                <a 
                  v-if="item.website_url"
                  :href="item.website_url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="text-slate-400 hover:text-orange-600 transition shrink-0"
                  title="Voir le site web"
                >
                  <ExternalLink class="w-3.5 h-3.5" />
                </a>
              </div>
              <div class="flex items-center gap-2 text-xs text-slate-500 mt-0.5">
                <span>{{ item.cuisine }}</span>
                <span>•</span>
                <span>{{ item.walking_time_min }} min ({{ item.distance_meters }} m)</span>
              </div>
            </div>
          </div>

          <!-- Score & Détail des votes -->
          <div class="text-right shrink-0">
            <div class="text-lg font-black text-slate-900">
              {{ item.points }} <span class="text-xs font-semibold text-slate-500">pts</span>
            </div>
            <div class="text-[11px] text-slate-500 font-medium">
              {{ item.first_votes }}x 1er • {{ item.second_votes }}x 2e • {{ item.third_votes }}x 3e
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
