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
  <div class="space-y-6">
    <!-- En-tête : Confirmation du vote et récapitulatif personnel -->
    <div class="bg-white rounded-2xl border-2 border-emerald-500/30 p-5 sm:p-6 shadow-xs bg-gradient-to-r from-emerald-50/40 via-white to-white">
      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-slate-100 pb-4 mb-4">
        <div class="flex items-center gap-2.5">
          <div class="w-9 h-9 rounded-xl bg-emerald-600 text-white flex items-center justify-center shrink-0 shadow-xs">
            <CheckCircle2 class="w-5 h-5" />
          </div>
          <div>
            <h2 class="text-lg sm:text-xl font-black text-slate-900 leading-tight">
              Vote enregistré avec succès !
            </h2>
            <p class="text-xs text-slate-600 mt-0.5">
              Merci <strong>{{ currentVoterName }}</strong> • Votre vote est définitif et le classement ci-dessous se met à jour en direct.
            </p>
          </div>
        </div>

        <div class="flex items-center gap-2 self-end sm:self-auto text-xs font-bold text-slate-600 bg-slate-100 px-3 py-1.5 rounded-lg shrink-0">
          <Users class="w-4 h-4 text-slate-500" />
          <span>{{ totalVoters }} {{ totalVoters <= 1 ? 'participant' : 'participants' }}</span>
        </div>
      </div>

      <!-- Vos 3 choix validés -->
      <div v-if="myChoices" class="flex flex-wrap items-center gap-2 pt-1 text-xs">
        <span class="font-bold text-slate-500 mr-1 flex items-center gap-1">
          <Lock class="w-3.5 h-3.5 text-slate-400" /> Vos choix validés :
        </span>
        <span class="bg-amber-100 text-amber-950 px-2.5 py-1 rounded-lg font-bold border border-amber-300">
          🥇 1er (3 pts) : {{ myChoices.first }}
        </span>
        <span v-if="myChoices.second" class="bg-slate-200 text-slate-900 px-2.5 py-1 rounded-lg font-bold border border-slate-300">
          🥈 2e (2 pts) : {{ myChoices.second }}
        </span>
        <span v-if="myChoices.third" class="bg-amber-900/10 text-amber-950 px-2.5 py-1 rounded-lg font-bold border border-amber-900/20">
          🥉 3e (1 pt) : {{ myChoices.third }}
        </span>
      </div>

      <!-- Liste de tous les collègues ayant voté -->
      <div v-if="voters.length > 0" class="flex flex-wrap items-center gap-1.5 text-xs text-slate-500 mt-3 pt-3 border-t border-slate-100">
        <span class="font-semibold text-slate-400">Ont voté :</span>
        <span
          v-for="(name, idx) in voters"
          :key="idx"
          :class="[
            name.toLowerCase() === currentVoterName.toLowerCase()
              ? 'bg-orange-100 text-orange-950 font-bold'
              : 'bg-slate-100 text-slate-700 font-medium',
            'px-2.5 py-0.5 rounded-md'
          ]"
        >
          {{ name }} {{ name.toLowerCase() === currentVoterName.toLowerCase() ? '(vous)' : '' }}
        </span>
      </div>
    </div>

    <!-- Le restaurant en tête (Grand vainqueur actuel) -->
    <div 
      v-if="winner && winner.points > 0"
      class="rounded-2xl bg-gradient-to-br from-amber-500/15 via-amber-50/50 to-white border-2 border-amber-400 p-6 sm:p-7 shadow-sm"
    >
      <div class="flex items-center gap-2 text-xs font-black text-amber-900 uppercase tracking-wider mb-2">
        <Trophy class="w-4 h-4 text-amber-600 shrink-0" />
        <span>En tête pour le déjeuner de ce midi</span>
      </div>

      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h3 class="text-2xl sm:text-3xl font-black text-slate-900">
            {{ winner.name }}
          </h3>
          <div class="flex items-center gap-2 flex-wrap mt-1">
            <p class="text-sm font-semibold text-slate-700">
              {{ winner.cuisine }}
            </p>
            <div 
              v-if="winner.rating"
              class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-amber-100 text-amber-950 text-xs font-bold"
            >
              <Star class="w-3 h-3 text-amber-600 fill-amber-500" />
              <span>{{ Number(winner.rating).toFixed(1) }}</span>
              <span v-if="winner.rating_count" class="text-[10px] text-amber-800 font-normal">({{ winner.rating_count }})</span>
            </div>
          </div>
          <div class="flex items-center gap-2 mt-2 text-xs font-bold text-emerald-800">
            <Footprints class="w-4 h-4 text-emerald-600" />
            <span>{{ winner.walking_time_min }} min à pied ({{ winner.distance_meters }} m)</span>
          </div>

        </div>

        <div class="flex sm:flex-col items-baseline sm:items-end justify-between sm:justify-center border-t sm:border-t-0 border-amber-200 pt-3 sm:pt-0 shrink-0">
          <span class="text-4xl font-black text-amber-600">
            {{ winner.points }} <span class="text-base font-bold text-slate-600">points</span>
          </span>
          <span class="text-xs font-bold text-slate-600 mt-1">
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
          <span>Site officiel</span>
          <ExternalLink class="w-3.5 h-3.5" />
        </a>
      </div>
    </div>

    <!-- Tableau de classement complet (immédiatement visible) -->
    <div class="bg-white rounded-2xl border-2 border-slate-200 shadow-sm overflow-hidden">
      <div class="p-4 sm:p-5 border-b border-slate-200 bg-slate-50 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <h3 class="text-base font-extrabold text-slate-900">
            Classement complet en direct
          </h3>
          <p class="text-xs text-slate-500">
            Total des points attribués par tous les votants
          </p>
        </div>

        <div class="flex items-center gap-2">
          <button
            type="button"
            @click="showMap = !showMap"
            class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-slate-300 hover:border-slate-400 bg-white text-slate-700 text-xs font-bold transition btn-interaction cursor-pointer"
          >
            <MapIcon v-if="!showMap" class="w-3.5 h-3.5 text-slate-500" />
            <List v-else class="w-3.5 h-3.5 text-slate-500" />
            <span>{{ showMap ? 'Masquer la carte' : 'Afficher la carte' }}</span>
          </button>

          <span class="text-xs font-semibold px-2.5 py-1 rounded-lg bg-emerald-50 text-emerald-800 border border-emerald-200">
            En direct
          </span>
        </div>
      </div>

      <div class="divide-y divide-slate-100">
        <div 
          v-for="item in rankings" 
          :key="item.restaurant_id"
          class="p-4 sm:p-5 flex items-center justify-between gap-4 hover:bg-slate-50/80 transition"
        >
          <div class="flex items-center gap-3.5 min-w-0">
            <!-- Badge de Rang -->
            <div 
              :class="[
                item.rank === 1 ? 'bg-amber-500 text-white font-black ring-2 ring-amber-400 shadow-xs text-base' :
                item.rank === 2 ? 'bg-slate-700 text-white font-bold' :
                item.rank === 3 ? 'bg-amber-900 text-white font-bold' :
                'bg-slate-100 text-slate-600 font-bold',
                'w-9 h-9 rounded-xl flex items-center justify-center shrink-0'
              ]"
            >
              {{ item.rank }}
            </div>

            <div class="min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <h4 class="text-sm sm:text-base font-extrabold text-slate-900 truncate">
                  {{ item.name }}
                </h4>
                <a 
                  v-if="item.google_maps_url"
                  :href="item.google_maps_url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="text-blue-600 hover:text-blue-800 transition shrink-0"
                  title="Voir la fiche Google & avis"
                >
                  <MapPin class="w-3.5 h-3.5" />
                </a>
                <a 
                  v-if="item.website_url"
                  :href="item.website_url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="text-slate-400 hover:text-orange-600 transition shrink-0"
                  title="Voir le site officiel"
                >
                  <ExternalLink class="w-3.5 h-3.5" />
                </a>
              </div>
              <div class="flex items-center gap-2 text-xs text-slate-500 mt-0.5 flex-wrap">
                <span class="font-medium text-slate-700">{{ item.cuisine }}</span>
                <span v-if="item.rating" class="inline-flex items-center gap-0.5 text-amber-900 font-bold bg-amber-50 px-1.5 py-0.5 rounded border border-amber-200/80 text-[11px]">
                  <Star class="w-2.5 h-2.5 text-amber-500 fill-amber-400" />
                  <span>{{ Number(item.rating).toFixed(1) }}</span>
                </span>
                <span>•</span>
                <span>{{ item.walking_time_min }} min ({{ item.distance_meters }} m)</span>
              </div>

            </div>
          </div>

          <!-- Total de points et votes reçus -->
          <div class="text-right shrink-0">
            <div class="text-xl font-black text-slate-900">
              {{ item.points }} <span class="text-xs font-bold text-slate-500">pts</span>
            </div>
            <div class="text-[11px] font-semibold text-slate-500 mt-0.5">
              {{ item.first_votes }}x 1er • {{ item.second_votes }}x 2e • {{ item.third_votes }}x 3e
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Carte des restaurants (placée sous le classement pour ne pas masquer les résultats) -->
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
