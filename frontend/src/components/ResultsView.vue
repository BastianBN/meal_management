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
    <div class="bg-[#FFFDF9] rounded-2xl border border-[#CBD8C8] p-5 sm:p-6">
      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-[#E8E3DA] pb-4 mb-4">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-[#F3F6F2] text-[#5C6F5A] flex items-center justify-center shrink-0 border border-[#CBD8C8]">
            <CheckCircle2 class="w-5 h-5" />
          </div>
          <div>
            <h2 class="font-serif text-xl sm:text-2xl font-normal text-[#292524] tracking-wide leading-tight">
              Vote enregistré avec succès
            </h2>
            <p class="text-xs text-[#78716C] mt-0.5">
              Merci <strong class="text-[#292524]">{{ currentVoterName }}</strong> • Votre vote est définitif. Le classement s'actualise en direct.
            </p>
          </div>
        </div>

        <div class="flex items-center gap-2 self-end sm:self-auto text-xs font-medium text-[#57534E] bg-[#FAF8F5] border border-[#E8E3DA] px-3 py-1.5 rounded-xl shrink-0">
          <Users class="w-4 h-4 text-[#78716C]" />
          <span>{{ totalVoters }} {{ totalVoters <= 1 ? 'participant' : 'participants' }}</span>
        </div>
      </div>

      <!-- Vos 3 choix validés -->
      <div v-if="myChoices" class="flex flex-wrap items-center gap-2 pt-1 text-xs">
        <span class="text-[#78716C] mr-1 flex items-center gap-1 font-medium">
          <Lock class="w-3.5 h-3.5 text-[#A8A29E]" /> Vos choix :
        </span>
        <span class="bg-[#FBF4F1] text-[#7C2D12] px-2.5 py-1 rounded-lg font-medium border border-[#E8C7BE]">
          1er (3 pts) : {{ myChoices.first }}
        </span>
        <span v-if="myChoices.second" class="bg-[#F3F6F2] text-[#2F3D2C] px-2.5 py-1 rounded-lg font-medium border border-[#CBD8C8]">
          2e (2 pts) : {{ myChoices.second }}
        </span>
        <span v-if="myChoices.third" class="bg-[#F7F5F2] text-[#4A433A] px-2.5 py-1 rounded-lg font-medium border border-[#DDD7CD]">
          3e (1 pt) : {{ myChoices.third }}
        </span>
      </div>

      <!-- Liste de tous les collègues ayant voté -->
      <div v-if="voters.length > 0" class="flex flex-wrap items-center gap-1.5 text-xs text-[#78716C] mt-3 pt-3 border-t border-[#E8E3DA]">
        <span class="text-[#A8A29E]">Ont voté :</span>
        <span
          v-for="(name, idx) in voters"
          :key="idx"
          :class="[
            name.toLowerCase() === currentVoterName.toLowerCase()
              ? 'bg-[#FBF4F1] text-[#B85B43] font-medium border border-[#E8C7BE]'
              : 'bg-[#FAF8F5] text-[#57534E] border border-[#E8E3DA]',
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
      class="rounded-2xl bg-[#FFFDF9] text-[#292524] p-6 sm:p-8 border-2 border-[#E8E3DA] relative overflow-hidden"
    >
      <div class="relative z-10">
        <!-- Sceau rouge Hanko -->
        <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-md bg-[#FBF4F1] border border-[#E8C7BE] text-[#B85B43] text-xs font-semibold uppercase tracking-widest mb-3">
          <Trophy class="w-3.5 h-3.5 text-[#B85B43] shrink-0" />
          <span>Sceau du Déjeuner • Choix du Groupe</span>
        </div>

        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-5">
          <div>
            <h3 class="font-serif text-3xl sm:text-4xl font-normal text-[#292524] tracking-wide leading-tight">
              {{ winner.name }}
            </h3>
            <div class="flex items-center gap-2.5 flex-wrap mt-2">
              <p class="text-sm text-[#57534E]">
                {{ winner.cuisine }}
              </p>
              <div 
                v-if="winner.rating"
                class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-[#FAF8F5] border border-[#E8E3DA] text-[#78350F] text-xs font-medium"
              >
                <Star class="w-3 h-3 text-amber-600 fill-amber-500" />
                <span>{{ Number(winner.rating).toFixed(1) }}</span>
                <span v-if="winner.rating_count" class="text-[10px] text-[#A8A29E] font-normal">({{ winner.rating_count }})</span>
              </div>
            </div>
            <div class="flex items-center gap-2 mt-3 text-xs font-medium text-[#78716C]">
              <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#FAF8F5] border border-[#E8E3DA] text-[#292524]">
                <Footprints class="w-3.5 h-3.5 text-[#5C6F5A]" />
                {{ winner.walking_time_min }} min à pied ({{ winner.distance_meters }} m)
              </span>
            </div>
          </div>

          <div class="flex sm:flex-col items-baseline sm:items-end justify-between sm:justify-center border-t sm:border-t-0 border-[#E8E3DA] pt-4 sm:pt-0 shrink-0">
            <span class="font-serif text-5xl sm:text-6xl font-normal text-[#B85B43] leading-none">
              {{ winner.points }} <span class="font-sans text-sm text-[#78716C]">pts</span>
            </span>
            <span class="text-xs text-[#78716C] mt-2 text-right">
              {{ winner.first_votes }}x 1er • {{ winner.second_votes }}x 2e • {{ winner.third_votes }}x 3e
            </span>
          </div>
        </div>

        <div class="mt-5 pt-4 border-t border-[#E8E3DA] flex flex-wrap items-center gap-4 text-xs">
          <a 
            v-if="winner.google_maps_url"
            :href="winner.google_maps_url"
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex items-center gap-1.5 font-medium text-[#57534E] hover:text-[#292524] transition underline underline-offset-4"
          >
            <MapPin class="w-3.5 h-3.5 text-[#78716C]" />
            <span>Fiche Google & Avis</span>
          </a>

          <a 
            v-if="winner.website_url"
            :href="winner.website_url"
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex items-center gap-1.5 font-medium text-[#B85B43] hover:text-[#9E4C36] transition underline underline-offset-4"
          >
            <span>Site officiel</span>
            <ExternalLink class="w-3.5 h-3.5" />
          </a>
        </div>
      </div>
    </div>

    <!-- Tableau de classement complet -->
    <div class="bg-[#FFFDF9] rounded-2xl border border-[#E8E3DA] overflow-hidden">
      <div class="p-4 sm:p-5 border-b border-[#E8E3DA] bg-[#FAF8F5] flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h3 class="font-serif text-lg font-normal text-[#292524] tracking-wide">
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
            class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-[#E8E3DA] hover:border-[#292524] bg-[#FFFDF9] text-[#57534E] hover:text-[#292524] text-xs font-medium transition cursor-pointer"
          >
            <MapIcon v-if="!showMap" class="w-3.5 h-3.5 text-[#78716C]" />
            <List v-else class="w-3.5 h-3.5 text-[#78716C]" />
            <span>{{ showMap ? 'Masquer la carte' : 'Afficher la carte' }}</span>
          </button>

          <span class="text-xs font-medium px-2.5 py-1 rounded-lg bg-[#F3F6F2] text-[#3E503B] border border-[#CBD8C8]">
            En direct
          </span>
        </div>
      </div>

      <div class="divide-y divide-[#E8E3DA]">
        <div 
          v-for="item in rankings" 
          :key="item.restaurant_id"
          :class="[
            item.rank === 1 ? 'bg-[#FDFBF9]' : 'hover:bg-[#FAF8F5]',
            'p-4 sm:p-5 flex items-center justify-between gap-4 transition'
          ]"
        >
          <div class="flex items-center gap-3.5 min-w-0">
            <!-- Badge de Rang -->
            <div 
              :class="[
                item.rank === 1 ? 'bg-[#B85B43] text-white font-medium' :
                item.rank === 2 ? 'bg-[#5C6F5A] text-white font-medium' :
                item.rank === 3 ? 'bg-[#82786D] text-white font-medium' :
                'bg-[#FAF8F5] text-[#78716C] font-medium border border-[#E8E3DA]',
                'w-8 h-8 rounded-xl flex items-center justify-center shrink-0 text-sm'
              ]"
            >
              {{ item.rank }}
            </div>

            <div class="min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <h4 class="font-serif text-base sm:text-lg font-normal text-[#292524] truncate">
                  {{ item.name }}
                </h4>
                <a 
                  v-if="item.google_maps_url"
                  :href="item.google_maps_url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="text-[#78716C] hover:text-[#292524] transition shrink-0"
                  title="Voir la fiche Google & avis"
                >
                  <MapPin class="w-3.5 h-3.5" />
                </a>
                <a 
                  v-if="item.website_url"
                  :href="item.website_url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="text-[#A8A29E] hover:text-[#292524] transition shrink-0"
                  title="Voir le site officiel"
                >
                  <ExternalLink class="w-3.5 h-3.5" />
                </a>
              </div>
              <div class="flex items-center gap-2 text-xs text-[#78716C] mt-0.5 flex-wrap">
                <span class="font-medium text-[#57534E]">{{ item.cuisine }}</span>
                <span v-if="item.rating" class="inline-flex items-center gap-0.5 text-[#78350F] font-medium bg-[#FEF3C7] px-1.5 py-0.5 rounded border border-[#F59E0B]/30 text-[11px]">
                  <Star class="w-2.5 h-2.5 text-amber-600 fill-amber-500" />
                  <span>{{ Number(item.rating).toFixed(1) }}</span>
                </span>
                <span class="text-[#DDD7CD]">•</span>
                <span>{{ item.walking_time_min }} min ({{ item.distance_meters }} m)</span>
              </div>
            </div>
          </div>

          <!-- Total de points et votes reçus -->
          <div class="text-right shrink-0">
            <div class="font-serif text-xl sm:text-2xl font-normal text-[#292524]">
              {{ item.points }} <span class="font-sans text-xs text-[#78716C]">pts</span>
            </div>
            <div class="text-[11px] text-[#78716C] mt-0.5">
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
