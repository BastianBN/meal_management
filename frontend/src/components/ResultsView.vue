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
    <div class="bg-[#FFFCF7] rounded-2xl border border-[#C8D7C4] p-5 sm:p-6">
      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-[#E5D6C5] pb-4 mb-4">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-[#F0F5EE] text-[#586F54] flex items-center justify-center shrink-0 border border-[#C8D7C4]">
            <CheckCircle2 class="w-5 h-5" />
          </div>
          <div>
            <h2 class="font-serif text-xl sm:text-2xl font-normal text-[#2C2019] tracking-wide leading-tight">
              Vote enregistré avec succès
            </h2>
            <p class="text-xs text-[#857263] mt-0.5">
              Merci <strong class="text-[#2C2019]">{{ currentVoterName }}</strong> • Votre vote est définitif. Le classement s'actualise en direct.
            </p>
          </div>
        </div>

        <div class="flex items-center gap-2 self-end sm:self-auto text-xs font-medium text-[#5D4B3E] bg-[#FAF2E8] border border-[#E5D6C5] px-3 py-1.5 rounded-xl shrink-0">
          <Users class="w-4 h-4 text-[#857263]" />
          <span>{{ totalVoters }} {{ totalVoters <= 1 ? 'participant' : 'participants' }}</span>
        </div>
      </div>

      <!-- Vos 3 choix validés -->
      <div v-if="myChoices" class="flex flex-wrap items-center gap-2 pt-1 text-xs">
        <span class="text-[#857263] mr-1 flex items-center gap-1 font-medium">
          <Lock class="w-3.5 h-3.5 text-[#AC9B8D]" /> Vos choix :
        </span>
        <span class="bg-[#FAF0E8] text-[#7C2D12] px-2.5 py-1 rounded-lg font-medium border border-[#ECCDBE]">
          1er (3 pts) : {{ myChoices.first }}
        </span>
        <span v-if="myChoices.second" class="bg-[#F0F5EE] text-[#2F3D2C] px-2.5 py-1 rounded-lg font-medium border border-[#C8D7C4]">
          2e (2 pts) : {{ myChoices.second }}
        </span>
        <span v-if="myChoices.third" class="bg-[#F4EDE5] text-[#4A433A] px-2.5 py-1 rounded-lg font-medium border border-[#DBCFBF]">
          3e (1 pt) : {{ myChoices.third }}
        </span>
      </div>

      <!-- Liste de tous les collègues ayant voté -->
      <div v-if="voters.length > 0" class="flex flex-wrap items-center gap-1.5 text-xs text-[#857263] mt-3 pt-3 border-t border-[#E5D6C5]">
        <span class="text-[#AC9B8D]">Ont voté :</span>
        <span
          v-for="(name, idx) in voters"
          :key="idx"
          :class="[
            name.toLowerCase() === currentVoterName.toLowerCase()
              ? 'bg-[#FAF0E8] text-[#C2542D] font-medium border border-[#ECCDBE]'
              : 'bg-[#FAF2E8] text-[#5D4B3E] border border-[#E5D6C5]',
            'px-2.5 py-0.5 rounded-md'
          ]"
        >
          {{ name }} {{ name.toLowerCase() === currentVoterName.toLowerCase() ? '(vous)' : '' }}
        </span>
      </div>
    </div>

    <!-- Le restaurant en tête (Estampe Washi & Sceau Hanko) -->
    <div 
      v-if="winner && winner.points > 0"
      class="rounded-2xl bg-[#FFFCF7] text-[#2C2019] p-6 sm:p-8 border-2 border-[#ECCDBE] relative overflow-hidden"
    >
      <div class="relative z-10">
        <!-- Sceau rouge Hanko -->
        <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-md bg-[#FAF0E8] border border-[#ECCDBE] text-[#C2542D] text-xs font-semibold uppercase tracking-widest mb-3">
          <Trophy class="w-3.5 h-3.5 text-[#C2542D] shrink-0" />
          <span>Sceau du Déjeuner • Choix du Groupe</span>
        </div>

        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-5">
          <div>
            <h3 class="font-serif text-3xl sm:text-4xl font-normal text-[#2C2019] tracking-wide leading-tight">
              {{ winner.name }}
            </h3>
            <div class="flex items-center gap-2.5 flex-wrap mt-2">
              <p class="text-sm text-[#5D4B3E]">
                {{ winner.cuisine }}
              </p>
              <div 
                v-if="winner.rating"
                class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-[#FAF2E8] border border-[#E5D6C5] text-[#78350F] text-xs font-medium"
              >
                <Star class="w-3 h-3 text-amber-600 fill-amber-500" />
                <span>{{ Number(winner.rating).toFixed(1) }}</span>
                <span v-if="winner.rating_count" class="text-[10px] text-[#AC9B8D] font-normal">({{ winner.rating_count }})</span>
              </div>
            </div>
            <div class="flex items-center gap-2 mt-3 text-xs font-medium text-[#857263]">
              <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#FAF2E8] border border-[#E5D6C5] text-[#2C2019]">
                <Footprints class="w-3.5 h-3.5 text-[#586F54]" />
                {{ winner.walking_time_min }} min à pied ({{ winner.distance_meters }} m)
              </span>
            </div>
          </div>

          <div class="flex sm:flex-col items-baseline sm:items-end justify-between sm:justify-center border-t sm:border-t-0 border-[#E5D6C5] pt-4 sm:pt-0 shrink-0">
            <span class="font-serif text-5xl sm:text-6xl font-normal text-[#C2542D] leading-none">
              {{ winner.points }} <span class="font-sans text-sm text-[#857263]">pts</span>
            </span>
            <span class="text-xs text-[#857263] mt-2 text-right">
              {{ winner.first_votes }}x 1er • {{ winner.second_votes }}x 2e • {{ winner.third_votes }}x 3e
            </span>
          </div>
        </div>

        <div class="mt-5 pt-4 border-t border-[#E5D6C5] flex flex-wrap items-center gap-4 text-xs">
          <a 
            v-if="winner.google_maps_url"
            :href="winner.google_maps_url"
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex items-center gap-1.5 font-medium text-[#5D4B3E] hover:text-[#2C2019] transition underline underline-offset-4"
          >
            <MapPin class="w-3.5 h-3.5 text-[#857263]" />
            <span>Fiche Google & Avis</span>
          </a>

          <a 
            v-if="winner.website_url"
            :href="winner.website_url"
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex items-center gap-1.5 font-medium text-[#C2542D] hover:text-[#A64320] transition underline underline-offset-4"
          >
            <span>Site officiel</span>
            <ExternalLink class="w-3.5 h-3.5" />
          </a>
        </div>
      </div>
    </div>

    <!-- Tableau de classement complet -->
    <div class="bg-[#FFFCF7] rounded-2xl border border-[#E5D6C5] overflow-hidden">
      <div class="p-4 sm:p-5 border-b border-[#E5D6C5] bg-[#FAF2E8] flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h3 class="font-serif text-lg font-normal text-[#2C2019] tracking-wide">
            Classement complet du groupe
          </h3>
          <p class="text-xs text-[#857263] mt-0.5">
            Total des points pondérés calculés selon les choix de l'équipe
          </p>
        </div>

        <div class="flex items-center gap-2">
          <button
            type="button"
            @click="showMap = !showMap"
            class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-[#E5D6C5] hover:border-[#2C2019] bg-[#FFFCF7] text-[#5D4B3E] hover:text-[#2C2019] text-xs font-medium transition cursor-pointer"
          >
            <MapIcon v-if="!showMap" class="w-3.5 h-3.5 text-[#857263]" />
            <List v-else class="w-3.5 h-3.5 text-[#857263]" />
            <span>{{ showMap ? 'Masquer la carte' : 'Afficher la carte' }}</span>
          </button>

          <span class="text-xs font-medium px-2.5 py-1 rounded-lg bg-[#F0F5EE] text-[#364A32] border border-[#C8D7C4]">
            En direct
          </span>
        </div>
      </div>

      <div class="divide-y divide-[#E5D6C5]">
        <div 
          v-for="item in rankings" 
          :key="item.restaurant_id"
          :class="[
            item.rank === 1 ? 'bg-[#FFFAF5]' : 'hover:bg-[#FAF2E8]',
            'p-4 sm:p-5 flex items-center justify-between gap-4 transition'
          ]"
        >
          <div class="flex items-center gap-3.5 min-w-0">
            <!-- Badge de Rang -->
            <div 
              :class="[
                item.rank === 1 ? 'bg-[#C2542D] text-white font-medium' :
                item.rank === 2 ? 'bg-[#586F54] text-white font-medium' :
                item.rank === 3 ? 'bg-[#7E6C5C] text-white font-medium' :
                'bg-[#FAF2E8] text-[#857263] font-medium border border-[#E5D6C5]',
                'w-8 h-8 rounded-xl flex items-center justify-center text-xs shrink-0'
              ]"
            >
              {{ item.rank }}
            </div>

            <!-- Infos Restaurant -->
            <div class="min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <span class="font-serif text-base font-normal text-[#2C2019] truncate">
                  {{ item.name }}
                </span>
                <a
                  v-if="item.google_maps_url"
                  :href="item.google_maps_url"
                  target="_blank"
                  rel="noopener"
                  class="text-[#857263] hover:text-[#2C2019] transition"
                  title="Fiche Google Maps"
                >
                  <MapPin class="w-3.5 h-3.5 inline" />
                </a>
                <a
                  v-if="item.website_url"
                  :href="item.website_url"
                  target="_blank"
                  rel="noopener"
                  class="text-[#857263] hover:text-[#2C2019] transition"
                  title="Site web"
                >
                  <ExternalLink class="w-3 h-3 inline" />
                </a>
              </div>

              <div class="flex items-center gap-2 mt-0.5 text-xs text-[#857263] flex-wrap">
                <span>{{ item.cuisine }}</span>
                <span v-if="item.rating" class="inline-flex items-center gap-0.5 text-[#78350F] font-medium px-1.5 py-0.2 rounded bg-[#FEF3C7]">
                  ⭐ {{ Number(item.rating).toFixed(1) }}
                </span>
                <span class="text-[#DAC7B2]">•</span>
                <span>{{ item.walking_time_min }} min ({{ item.distance_meters }} m)</span>
              </div>
            </div>
          </div>

          <!-- Total des Points et Détails des votes -->
          <div class="text-right shrink-0">
            <div class="flex items-baseline justify-end gap-1">
              <span 
                :class="[
                  item.rank === 1 ? 'text-[#C2542D]' : 'text-[#2C2019]',
                  'font-serif text-2xl font-normal leading-none'
                ]"
              >
                {{ item.points }}
              </span>
              <span class="text-xs text-[#857263]">pts</span>
            </div>
            <div class="text-[10px] text-[#857263] mt-0.5 whitespace-nowrap">
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
