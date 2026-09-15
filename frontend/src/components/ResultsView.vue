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
    <!-- En-tête : Confirmation du vote et récapitulatif personnel (Addition / Fiche brasserie claire) -->
    <div class="bg-white rounded-2xl border border-[#E5D6C5] p-5 sm:p-6 shadow-sm">
      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-[#E5D6C5] pb-4 mb-4">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-[#DC2626]/10 text-[#DC2626] flex items-center justify-center shrink-0 border border-[#DC2626]/20">
            <CheckCircle2 class="w-5 h-5" />
          </div>
          <div>
            <h2 class="font-serif text-2xl font-normal text-[#1E232B] tracking-wide leading-tight">
              Vote enregistré avec succès
            </h2>
            <p class="text-xs text-[#6B7280] mt-0.5">
              Merci <strong class="text-[#1E232B]">{{ currentVoterName }}</strong> • Votre vote est scellé. L'ardoise s'actualise en direct.
            </p>
          </div>
        </div>

        <div class="flex items-center gap-2 self-end sm:self-auto text-xs font-medium text-[#1E232B] bg-[#F4EFEB] border border-[#E5D6C5] px-3 py-1.5 rounded-xl shrink-0">
          <Users class="w-4 h-4 text-[#78716C]" />
          <span>{{ totalVoters }} {{ totalVoters <= 1 ? 'convive' : 'convives' }}</span>
        </div>
      </div>

      <!-- Vos 3 choix validés (Badges Trio : Rouge Bistrot, Laiton, Zinc) -->
      <div v-if="myChoices" class="flex flex-wrap items-center gap-2 pt-1 text-xs">
        <span class="text-[#78716C] mr-1 flex items-center gap-1 font-medium">
          <Lock class="w-3.5 h-3.5 text-[#9CA3AF]" /> Vos choix :
        </span>
        <span class="bg-[#DC2626] text-white px-2.5 py-1 rounded-lg font-medium border border-[#B91C1C] shadow-xs">
          1er (3 pts) : {{ myChoices.first }}
        </span>
        <span v-if="myChoices.second" class="bg-[#D97706] text-white px-2.5 py-1 rounded-lg font-medium border border-[#B45309] shadow-xs">
          2e (2 pts) : {{ myChoices.second }}
        </span>
        <span v-if="myChoices.third" class="bg-[#64748B] text-white px-2.5 py-1 rounded-lg font-medium border border-[#475569] shadow-xs">
          3e (1 pt) : {{ myChoices.third }}
        </span>
      </div>

      <!-- Liste de tous les collègues ayant voté -->
      <div v-if="voters.length > 0" class="flex flex-wrap items-center gap-1.5 text-xs text-[#6B7280] mt-3 pt-3 border-t border-[#E5D6C5]">
        <span class="text-[#9CA3AF]">Convives à table :</span>
        <span
          v-for="(name, idx) in voters"
          :key="idx"
          :class="[
            name.toLowerCase() === currentVoterName.toLowerCase()
              ? 'bg-[#DC2626]/10 text-[#DC2626] font-medium border border-[#DC2626]/30'
              : 'bg-[#F4EFEB] text-[#1E232B] border border-[#E5D6C5]',
            'px-2.5 py-0.5 rounded-md'
          ]"
        >
          {{ name }} {{ name.toLowerCase() === currentVoterName.toLowerCase() ? '(vous)' : '' }}
        </span>
      </div>
    </div>

    <!-- Le restaurant en tête (« L'Ardoise du Chef ») -->
    <div 
      v-if="winner && winner.points > 0"
      class="rounded-2xl bg-[#191C22] text-[#F8FAFC] p-6 sm:p-8 border-2 border-[#D97706]/70 shadow-2xl relative overflow-hidden"
    >
      <div class="relative z-10">
        <!-- Ruban Rouge Bistrot -->
        <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-md bg-[#DC2626] text-white text-xs font-semibold uppercase tracking-widest mb-3 shadow-md">
          <Trophy class="w-3.5 h-3.5 text-amber-200 shrink-0" />
          <span>L'Ardoise du Chef • Choix de la Table</span>
        </div>

        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-5">
          <div>
            <h3 class="font-serif text-3xl sm:text-4xl font-normal text-[#F8FAFC] tracking-wide leading-tight">
              {{ winner.name }}
            </h3>
            <div class="flex items-center gap-2.5 flex-wrap mt-2">
              <p class="text-sm text-[#CBD5E1]">
                {{ winner.cuisine }}
              </p>
              <div 
                v-if="winner.rating"
                class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-[#242933] border border-[#383F4C] text-[#FBBF24] text-xs font-medium"
              >
                <Star class="w-3 h-3 text-amber-400 fill-amber-400" />
                <span>{{ Number(winner.rating).toFixed(1) }}</span>
                <span v-if="winner.rating_count" class="text-[10px] text-[#94A3B8] font-normal">({{ winner.rating_count }})</span>
              </div>
            </div>
            <div class="flex items-center gap-2 mt-3 text-xs font-medium text-[#94A3B8]">
              <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#242933] border border-[#383F4C] text-[#F1EADF]">
                <Footprints class="w-3.5 h-3.5 text-[#D97706]" />
                {{ winner.walking_time_min }} min à pied ({{ winner.distance_meters }} m)
              </span>
            </div>
          </div>

          <div class="flex sm:flex-col items-baseline sm:items-end justify-between sm:justify-center border-t sm:border-t-0 border-[#383F4C] pt-4 sm:pt-0 shrink-0">
            <span class="font-serif text-5xl sm:text-6xl font-normal text-[#F59E0B] leading-none drop-shadow-md">
              {{ winner.points }} <span class="font-sans text-sm text-[#94A3B8]">pts</span>
            </span>
            <span class="text-xs text-[#94A3B8] mt-2 text-right">
              {{ winner.first_votes }}x 1er • {{ winner.second_votes }}x 2e • {{ winner.third_votes }}x 3e
            </span>
          </div>
        </div>

        <div class="mt-5 pt-4 border-t border-[#383F4C] flex flex-wrap items-center gap-4 text-xs">
          <a 
            v-if="winner.google_maps_url"
            :href="winner.google_maps_url"
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex items-center gap-1.5 font-medium text-[#CBD5E1] hover:text-[#F8FAFC] transition underline underline-offset-4"
          >
            <MapPin class="w-3.5 h-3.5 text-[#94A3B8]" />
            <span>Fiche Google & Avis</span>
          </a>

          <a 
            v-if="winner.website_url"
            :href="winner.website_url"
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex items-center gap-1.5 font-medium text-[#F59E0B] hover:text-[#FBBF24] transition underline underline-offset-4"
          >
            <span>Site officiel</span>
            <ExternalLink class="w-3.5 h-3.5" />
          </a>
        </div>
      </div>
    </div>

    <!-- Tableau de classement complet (Ardoise Brasserie) -->
    <div class="bg-[#191C22] text-[#F8FAFC] rounded-2xl border border-[#383F4C] overflow-hidden shadow-xl">
      <div class="p-4 sm:p-5 border-b border-[#383F4C] bg-[#20252E] flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h3 class="font-serif text-xl font-normal text-[#F8FAFC] tracking-wide">
            Classement de la Brasserie
          </h3>
          <p class="text-xs text-[#94A3B8] mt-0.5">
            Total des points pondérés calculés selon les suffrages de la table
          </p>
        </div>

        <div class="flex items-center gap-2">
          <button
            type="button"
            @click="showMap = !showMap"
            class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-[#383F4C] hover:border-[#D97706] bg-[#191C22] text-[#CBD5E1] hover:text-[#F8FAFC] text-xs font-medium transition cursor-pointer"
          >
            <MapIcon v-if="!showMap" class="w-3.5 h-3.5 text-[#94A3B8]" />
            <List v-else class="w-3.5 h-3.5 text-[#94A3B8]" />
            <span>{{ showMap ? 'Masquer la carte' : 'Afficher la carte' }}</span>
          </button>

          <span class="text-xs font-medium px-2.5 py-1 rounded-lg bg-[#DC2626]/20 text-[#FCA5A5] border border-[#DC2626]/40">
            En direct
          </span>
        </div>
      </div>

      <div class="divide-y divide-[#2B313D]">
        <div 
          v-for="item in rankings" 
          :key="item.restaurant_id"
          :class="[
            item.rank === 1 ? 'bg-[#242933]/60' : 'hover:bg-[#20252E]',
            'p-4 sm:p-5 flex items-center justify-between gap-4 transition'
          ]"
        >
          <div class="flex items-center gap-3.5 min-w-0">
            <!-- Badge de Rang Trio Bistrot -->
            <div 
              :class="[
                item.rank === 1 ? 'bg-[#DC2626] text-white font-bold shadow-xs' :
                item.rank === 2 ? 'bg-[#D97706] text-white font-bold shadow-xs' :
                item.rank === 3 ? 'bg-[#64748B] text-white font-bold shadow-xs' :
                'bg-[#242933] text-[#94A3B8] font-medium border border-[#383F4C]',
                'w-8 h-8 rounded-xl flex items-center justify-center text-xs shrink-0'
              ]"
            >
              {{ item.rank }}
            </div>

            <!-- Infos Restaurant -->
            <div class="min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <span class="font-serif text-lg font-normal text-[#F8FAFC] truncate">
                  {{ item.name }}
                </span>
                <a
                  v-if="item.google_maps_url"
                  :href="item.google_maps_url"
                  target="_blank"
                  rel="noopener"
                  class="text-[#94A3B8] hover:text-[#F8FAFC] transition"
                  title="Fiche Google Maps"
                >
                  <MapPin class="w-3.5 h-3.5 inline" />
                </a>
                <a
                  v-if="item.website_url"
                  :href="item.website_url"
                  target="_blank"
                  rel="noopener"
                  class="text-[#94A3B8] hover:text-[#F8FAFC] transition"
                  title="Site web"
                >
                  <ExternalLink class="w-3 h-3 inline" />
                </a>
              </div>

              <div class="flex items-center gap-2 mt-0.5 text-xs text-[#94A3B8] flex-wrap">
                <span>{{ item.cuisine }}</span>
                <span v-if="item.rating" class="inline-flex items-center gap-1 text-[#FBBF24] bg-[#242933] border border-[#383F4C] px-1.5 py-0.2 rounded text-xs font-medium">
                  ⭐ {{ Number(item.rating).toFixed(1) }}
                </span>
                <span class="text-[#475569]">•</span>
                <span>{{ item.walking_time_min }} min ({{ item.distance_meters }} m)</span>
              </div>
            </div>
          </div>

          <!-- Total des Points et Détails des votes -->
          <div class="text-right shrink-0">
            <div class="flex items-baseline justify-end gap-1">
              <span 
                :class="[
                  item.rank === 1 ? 'text-[#F59E0B]' : 'text-[#F8FAFC]',
                  'font-serif text-2xl font-normal leading-none'
                ]"
              >
                {{ item.points }}
              </span>
              <span class="text-xs text-[#94A3B8]">pts</span>
            </div>
            <div class="text-[10px] text-[#94A3B8] mt-0.5 whitespace-nowrap">
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
