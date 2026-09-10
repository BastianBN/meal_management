<script setup>
import { computed } from 'vue';
import { Trophy, Footprints, ExternalLink, Users, Radio } from 'lucide-vue-next';

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

const rankings = computed(() => props.leaderboard?.rankings || []);
const totalVoters = computed(() => props.leaderboard?.total_voters || 0);
const voters = computed(() => props.leaderboard?.voters || []);
const winner = computed(() => rankings.value.length > 0 ? rankings.value[0] : null);
</script>

<template>
  <div class="space-y-8">
    <!-- Statut en direct et participation -->
    <div class="bg-white rounded-2xl border border-slate-200 p-5 sm:p-6 shadow-xs">
      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-100 pb-4 mb-4">
        <div class="flex items-center gap-2.5">
          <span class="relative flex h-3 w-3">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
          </span>
          <h2 class="text-xl font-bold text-slate-900">
            Résultats en direct
          </h2>
          <span class="text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
            Temps réel
          </span>
        </div>

        <div class="flex items-center gap-2 text-sm text-slate-600">
          <Users class="w-4 h-4 text-slate-400" />
          <span class="font-bold text-slate-900">{{ totalVoters }}</span>
          <span>{{ totalVoters <= 1 ? 'collègue a voté' : 'collègues ont voté' }}</span>
        </div>
      </div>

      <!-- Liste des votants -->
      <div v-if="voters.length > 0" class="flex flex-wrap items-center gap-1.5 text-xs text-slate-600">
        <span class="font-medium text-slate-400 mr-1">Votants :</span>
        <span
          v-for="(name, idx) in voters"
          :key="idx"
          :class="[
            name.toLowerCase() === currentVoterName.toLowerCase()
              ? 'bg-brand-50 text-brand-700 font-semibold ring-1 ring-brand-200'
              : 'bg-slate-100 text-slate-700',
            'px-2.5 py-1 rounded-md'
          ]"
        >
          {{ name }} {{ name.toLowerCase() === currentVoterName.toLowerCase() ? '(vous)' : '' }}
        </span>
      </div>
      <div v-else class="text-xs text-slate-400 italic">
        En attente des premiers votes...
      </div>
    </div>

    <!-- Le restaurant en tête (Gagnant actuel) -->
    <div 
      v-if="winner && winner.points > 0"
      class="rounded-2xl bg-gradient-to-br from-amber-500/10 via-amber-50/20 to-transparent border-2 border-amber-500/30 p-6 sm:p-8 shadow-sm relative overflow-hidden"
    >
      <div class="flex items-center gap-2 text-xs font-bold text-amber-800 uppercase tracking-wider mb-2">
        <Trophy class="w-4 h-4 text-amber-600" />
        <span>Choix favori pour le déjeuner</span>
      </div>

      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h3 class="text-2xl font-extrabold text-slate-900">
            {{ winner.name }}
          </h3>
          <p class="text-sm text-slate-600 mt-0.5">
            {{ winner.cuisine }}
          </p>
          <div class="flex items-center gap-2 mt-2 text-xs text-slate-500">
            <Footprints class="w-4 h-4 text-slate-400" />
            <span>{{ winner.walking_time_min }} min de marche ({{ winner.distance_meters }} m)</span>
          </div>
        </div>

        <div class="flex sm:flex-col items-baseline sm:items-end justify-between sm:justify-center border-t sm:border-t-0 border-amber-200/50 pt-3 sm:pt-0">
          <span class="text-3xl font-black text-amber-600">
            {{ winner.points }} <span class="text-sm font-semibold text-slate-600">pts</span>
          </span>
          <span class="text-xs text-slate-500 mt-1">
            {{ winner.first_votes }}x 1er • {{ winner.second_votes }}x 2e • {{ winner.third_votes }}x 3e
          </span>
        </div>
      </div>

      <div v-if="winner.website_url" class="mt-4 pt-3 border-t border-amber-200/40">
        <a 
          :href="winner.website_url"
          target="_blank"
          rel="noopener noreferrer"
          class="inline-flex items-center gap-1.5 text-xs font-semibold text-amber-800 hover:text-amber-900"
        >
          <span>Accéder au site officiel pour réserver ou voir la carte</span>
          <ExternalLink class="w-3.5 h-3.5" />
        </a>
      </div>
    </div>

    <!-- Tableau / Liste complète du classement -->
    <div class="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
      <div class="p-4 sm:p-5 border-b border-slate-100 bg-slate-50/60 flex items-center justify-between">
        <h3 class="text-sm font-bold text-slate-900">
          Classement complet des établissements
        </h3>
        <span class="text-xs text-slate-500">
          Barème : 1er (3 pts) • 2e (2 pts) • 3e (1 pt)
        </span>
      </div>

      <div class="divide-y divide-slate-100">
        <div 
          v-for="item in rankings" 
          :key="item.restaurant_id"
          class="p-4 sm:p-5 flex items-center justify-between gap-4 hover:bg-slate-50/50 transition"
        >
          <div class="flex items-center gap-3.5 min-w-0">
            <!-- Badge de Rang -->
            <div 
              :class="[
                item.rank === 1 ? 'bg-amber-500 text-white font-black ring-2 ring-amber-500/30' :
                item.rank === 2 ? 'bg-slate-300 text-slate-800 font-bold' :
                item.rank === 3 ? 'bg-amber-700/80 text-white font-bold' :
                'bg-slate-100 text-slate-500 font-medium',
                'w-8 h-8 rounded-xl flex items-center justify-center text-sm shrink-0'
              ]"
            >
              {{ item.rank }}
            </div>

            <div class="min-w-0">
              <div class="flex items-center gap-2">
                <h4 class="text-sm sm:text-base font-bold text-slate-900 truncate">
                  {{ item.name }}
                </h4>
                <a 
                  v-if="item.website_url"
                  :href="item.website_url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="text-slate-400 hover:text-brand-600 transition shrink-0"
                  title="Voir la carte / site web"
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
              {{ item.points }} <span class="text-xs font-normal text-slate-500">pts</span>
            </div>
            <div class="text-[11px] text-slate-400">
              {{ item.first_votes }} / {{ item.second_votes }} / {{ item.third_votes }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
