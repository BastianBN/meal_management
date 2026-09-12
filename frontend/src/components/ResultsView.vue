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
    <div class="bg-white/90 backdrop-blur-sm rounded-2xl border border-emerald-600/30 p-5 sm:p-6 shadow-xs">
      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-[#E7E2D9] pb-4 mb-4">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-emerald-700 text-white flex items-center justify-center shrink-0 shadow-2xs">
            <CheckCircle2 class="w-5 h-5" />
          </div>
          <div>
            <h2 class="font-serif text-xl sm:text-2xl font-bold text-[#1C1917] tracking-tight leading-tight">
              Vote enregistré avec succès !
            </h2>
            <p class="text-xs text-[#78716C] mt-0.5">
              Merci <strong class="text-[#1C1917]">{{ currentVoterName }}</strong> • Votre vote est définitif. Le classement se met à jour en temps réel.
            </p>
          </div>
        </div>

        <div class="flex items-center gap-2 self-end sm:self-auto text-xs font-bold text-[#44403C] bg-[#FAF7F2] border border-[#E7E2D9] px-3 py-1.5 rounded-xl shrink-0">
          <Users class="w-4 h-4 text-[#78716C]" />
          <span>{{ totalVoters }} {{ totalVoters <= 1 ? 'participant' : 'participants' }}</span>
        </div>
      </div>

      <!-- Vos 3 choix validés -->
      <div v-if="myChoices" class="flex flex-wrap items-center gap-2 pt-1 text-xs">
        <span class="font-bold text-[#78716C] mr-1 flex items-center gap-1">
          <Lock class="w-3.5 h-3.5 text-[#A8A29E]" /> Vos choix :
        </span>
        <span class="bg-[#FEF3C7] text-[#78350F] px-2.5 py-1 rounded-lg font-bold border border-[#F59E0B]/50 shadow-2xs">
          🥇 1er (3 pts) : {{ myChoices.first }}
        </span>
        <span v-if="myChoices.second" class="bg-[#F3EFEA] text-[#1C1917] px-2.5 py-1 rounded-lg font-bold border border-[#D5CEC2]">
          🥈 2e (2 pts) : {{ myChoices.second }}
        </span>
        <span v-if="myChoices.third" class="bg-[#FFEDD5] text-[#7C2D12] px-2.5 py-1 rounded-lg font-bold border border-[#FB923C]/50">
          🥉 3e (1 pt) : {{ myChoices.third }}
        </span>
      </div>

      <!-- Liste de tous les collègues ayant voté -->
      <div v-if="voters.length > 0" class="flex flex-wrap items-center gap-1.5 text-xs text-[#78716C] mt-3 pt-3 border-t border-[#E7E2D9]">
        <span class="font-semibold text-[#A8A29E]">Ont voté :</span>
        <span
          v-for="(name, idx) in voters"
          :key="idx"
          :class="[
            name.toLowerCase() === currentVoterName.toLowerCase()
              ? 'bg-[#FFF7ED] text-[#9A3412] font-bold border border-[#EA580C]/30'
              : 'bg-[#F3EFEA] text-[#44403C] font-medium border border-[#E7E2D9]',
            'px-2.5 py-0.5 rounded-md'
          ]"
        >
          {{ name }} {{ name.toLowerCase() === currentVoterName.toLowerCase() ? '(vous)' : '' }}
        </span>
      </div>
    </div>

    <!-- Le restaurant en tête (Grand vainqueur actuel stylisé Ardoise Bistrot) -->
    <div 
      v-if="winner && winner.points > 0"
      class="rounded-3xl bg-[#1C1917] text-[#FAF7F2] p-6 sm:p-8 shadow-xl border border-[#292524] relative overflow-hidden"
    >
      <!-- Halo d'accent bistrot -->
      <div class="pointer-events-none absolute -right-12 -top-12 w-64 h-64 rounded-full bg-[#C2410C]/15 blur-3xl"></div>

      <div class="relative z-10">
        <div class="flex items-center gap-2 text-xs font-black text-[#F59E0B] uppercase tracking-widest mb-3">
          <Trophy class="w-4 h-4 text-[#F59E0B] shrink-0" />
          <span>L'Ardoise Gagnante du Déjeuner</span>
        </div>

        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-5">
          <div>
            <h3 class="font-serif text-3xl sm:text-4xl font-extrabold text-white tracking-tight leading-tight">
              {{ winner.name }}
            </h3>
            <div class="flex items-center gap-2.5 flex-wrap mt-2">
              <p class="text-sm font-semibold text-[#D6D3D1]">
                {{ winner.cuisine }}
              </p>
              <div 
                v-if="winner.rating"
                class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-[#292524] border border-[#44403C] text-[#F59E0B] text-xs font-bold"
              >
                <Star class="w-3 h-3 text-[#F59E0B] fill-[#F59E0B]" />
                <span>{{ Number(winner.rating).toFixed(1) }}</span>
                <span v-if="winner.rating_count" class="text-[10px] text-[#A8A29E] font-normal">({{ winner.rating_count }})</span>
              </div>
            </div>
            <div class="flex items-center gap-2 mt-3 text-xs font-semibold text-[#A8A29E]">
              <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#292524] border border-[#44403C] text-[#E7E2D9]">
                <Footprints class="w-3.5 h-3.5 text-emerald-400" />
                {{ winner.walking_time_min }} min à pied ({{ winner.distance_meters }} m)
              </span>
            </div>
          </div>

          <div class="flex sm:flex-col items-baseline sm:items-end justify-between sm:justify-center border-t sm:border-t-0 border-[#292524] pt-4 sm:pt-0 shrink-0">
            <span class="font-serif text-5xl sm:text-6xl font-black text-[#F59E0B] leading-none">
              {{ winner.points }} <span class="text-lg font-sans font-bold text-[#A8A29E]">pts</span>
            </span>
            <span class="text-xs font-medium text-[#A8A29E] mt-2 text-right">
              {{ winner.first_votes }}x 1er • {{ winner.second_votes }}x 2e • {{ winner.third_votes }}x 3e
            </span>
          </div>
        </div>

        <div class="mt-5 pt-4 border-t border-[#292524] flex flex-wrap items-center gap-4 text-xs">
          <a 
            v-if="winner.google_maps_url"
            :href="winner.google_maps_url"
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex items-center gap-1.5 font-bold text-[#38BDF8] hover:text-sky-300 transition underline underline-offset-4"
          >
            <MapPin class="w-3.5 h-3.5 text-[#38BDF8]" />
            <span>Fiche Google & Avis</span>
          </a>

          <a 
            v-if="winner.website_url"
            :href="winner.website_url"
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex items-center gap-1.5 font-bold text-[#F59E0B] hover:text-amber-300 transition underline underline-offset-4"
          >
            <span>Site officiel</span>
            <ExternalLink class="w-3.5 h-3.5" />
          </a>
        </div>
      </div>
    </div>

    <!-- Tableau de classement complet (immédiatement visible) -->
    <div class="bg-white/95 rounded-2xl border border-[#E7E2D9] shadow-xs overflow-hidden">
      <div class="p-4 sm:p-5 border-b border-[#E7E2D9] bg-[#FAF7F2] flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h3 class="font-serif text-xl font-bold text-[#1C1917] tracking-tight">
            Classement complet du groupe
          </h3>
          <p class="text-xs text-[#78716C] mt-0.5">
            Total des points pondérés calculés selon les choix de l'équipe
          </p>
        </div>

        <div class="flex items-center gap-2">
          <button
            type="button"
            @click="showMap = !showMap"
            class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-[#D5CEC2] hover:border-[#1C1917] bg-white text-[#44403C] hover:text-[#1C1917] text-xs font-bold transition cursor-pointer"
          >
            <MapIcon v-if="!showMap" class="w-3.5 h-3.5 text-[#78716C]" />
            <List v-else class="w-3.5 h-3.5 text-[#78716C]" />
            <span>{{ showMap ? 'Masquer la carte' : 'Afficher la carte' }}</span>
          </button>

          <span class="text-xs font-semibold px-2.5 py-1 rounded-lg bg-emerald-50 text-emerald-900 border border-emerald-300">
            En direct
          </span>
        </div>
      </div>

      <div class="divide-y divide-[#E7E2D9]">
        <div 
          v-for="item in rankings" 
          :key="item.restaurant_id"
          :class="[
            item.rank === 1 ? 'bg-amber-50/40' : 'hover:bg-[#FAF7F2]/80',
            'p-4 sm:p-5 flex items-center justify-between gap-4 transition'
          ]"
        >
          <div class="flex items-center gap-3.5 min-w-0">
            <!-- Badge de Rang -->
            <div 
              :class="[
                item.rank === 1 ? 'bg-[#D97706] text-white font-black shadow-2xs text-base' :
                item.rank === 2 ? 'bg-[#44403C] text-white font-bold' :
                item.rank === 3 ? 'bg-[#C2410C] text-white font-bold' :
                'bg-[#F3EFEA] text-[#78716C] font-bold border border-[#E7E2D9]',
                'w-9 h-9 rounded-xl flex items-center justify-center shrink-0'
              ]"
            >
              {{ item.rank }}
            </div>

            <div class="min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <h4 class="font-serif text-base sm:text-lg font-bold text-[#1C1917] truncate">
                  {{ item.name }}
                </h4>
                <a 
                  v-if="item.google_maps_url"
                  :href="item.google_maps_url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="text-[#C2410C] hover:text-[#9A3412] transition shrink-0"
                  title="Voir la fiche Google & avis"
                >
                  <MapPin class="w-3.5 h-3.5" />
                </a>
                <a 
                  v-if="item.website_url"
                  :href="item.website_url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="text-[#78716C] hover:text-[#1C1917] transition shrink-0"
                  title="Voir le site officiel"
                >
                  <ExternalLink class="w-3.5 h-3.5" />
                </a>
              </div>
              <div class="flex items-center gap-2 text-xs text-[#78716C] mt-0.5 flex-wrap">
                <span class="font-medium text-[#44403C]">{{ item.cuisine }}</span>
                <span v-if="item.rating" class="inline-flex items-center gap-0.5 text-[#78350F] font-bold bg-[#FEF3C7] px-1.5 py-0.5 rounded border border-[#F59E0B]/50 text-[11px]">
                  <Star class="w-2.5 h-2.5 text-amber-500 fill-amber-400" />
                  <span>{{ Number(item.rating).toFixed(1) }}</span>
                </span>
                <span class="text-[#D5CEC2]">•</span>
                <span>{{ item.walking_time_min }} min ({{ item.distance_meters }} m)</span>
              </div>
            </div>
          </div>

          <!-- Total de points et votes reçus -->
          <div class="text-right shrink-0">
            <div class="font-serif text-xl sm:text-2xl font-black text-[#1C1917]">
              {{ item.points }} <span class="font-sans text-xs font-bold text-[#78716C]">pts</span>
            </div>
            <div class="text-[11px] font-medium text-[#78716C] mt-0.5">
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
