<script setup>
import { computed } from 'vue';
import { ExternalLink, Footprints, Check, MapPin, FileText, Star } from 'lucide-vue-next';

const props = defineProps({
  restaurant: {
    type: Object,
    required: true,
  },
  currentRank: {
    type: Number,
    default: null, // 1, 2, 3 ou null
  },
  disabled: {
    type: Boolean,
    default: false,
  }
});

const emit = defineEmits(['toggleRank']);

const hasFormulas = computed(() => {
  return props.restaurant.lunch_formulas && props.restaurant.lunch_formulas.length > 0;
});

const isPdfMenu = computed(() => {
  return props.restaurant.menu_url && (
    props.restaurant.menu_url.toLowerCase().endsWith('.pdf') || 
    props.restaurant.menu_url.includes('.pdf?')
  );
});

function handleRankClick(rank) {
  if (props.disabled) return;
  emit('toggleRank', { restaurantId: props.restaurant.id, rank });
}
</script>

<template>
  <div 
    :class="[
      'rounded-2xl border p-5 sm:p-6 transition-all duration-200 bg-white relative flex flex-col justify-between',
      currentRank === 1 ? 'border-amber-500 ring-2 ring-amber-500/20 shadow-md bg-amber-50/15' :
      currentRank === 2 ? 'border-slate-500 ring-2 ring-slate-500/20 shadow-sm bg-slate-50/20' :
      currentRank === 3 ? 'border-amber-800 ring-2 ring-amber-800/15 shadow-sm bg-amber-900/5' :
      'border-slate-200 hover:border-slate-300 shadow-xs'
    ]"
  >
    <!-- Badge de choix actif sur la carte -->
    <div 
      v-if="currentRank"
      :class="[
        currentRank === 1 ? 'bg-amber-500 text-white' :
        currentRank === 2 ? 'bg-slate-700 text-white' :
        'bg-amber-900 text-white',
        'absolute -top-3 right-5 px-3 py-0.5 rounded-full text-xs font-bold shadow-xs flex items-center gap-1.5'
      ]"
    >
      <Check class="w-3.5 h-3.5" />
      <span>{{ currentRank === 1 ? '1er Choix (+3 pts)' : currentRank === 2 ? '2e Choix (+2 pts)' : '3e Choix (+1 pt)' }}</span>
    </div>

    <!-- En-tête : Nom, Cuisine, Note, Distance -->
    <div>
      <div class="flex items-start justify-between gap-3 mb-2">
        <div>
          <div class="flex items-center gap-1.5 flex-wrap mb-1.5">
            <span class="inline-block text-xs font-semibold px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700">
              {{ restaurant.cuisine || 'Bistrot' }}
            </span>
            <!-- Badge Note / Avis -->
            <div 
              v-if="restaurant.rating"
              class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-amber-50 border border-amber-200/80 text-amber-900 text-xs font-bold"
              :title="`${restaurant.rating_count || 100} avis clients vérifiés`"
            >
              <Star class="w-3 h-3 text-amber-500 fill-amber-400" />
              <span>{{ Number(restaurant.rating).toFixed(1) }}</span>
              <span v-if="restaurant.rating_count" class="text-[10px] text-amber-700 font-normal">({{ restaurant.rating_count }})</span>
            </div>
            <!-- Badge Top avis -->
            <span 
              v-if="restaurant.rating >= 4.7"
              class="inline-block text-[10px] font-bold px-2 py-0.5 rounded-full bg-rose-50 border border-rose-200 text-rose-700"
            >
              Top avis
            </span>
          </div>

          <h3 class="text-lg font-bold text-slate-900 leading-tight">
            {{ restaurant.name }}
          </h3>
        </div>

        <!-- Badge temps de marche -->
        <div class="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-emerald-50 text-emerald-800 border border-emerald-200/60 text-xs font-semibold shrink-0">
          <Footprints class="w-3.5 h-3.5 text-emerald-600" />
          <span>{{ restaurant.walking_time_min }} min</span>
          <span class="text-emerald-400">•</span>
          <span>{{ restaurant.distance_meters }} m</span>
        </div>
      </div>


      <p v-if="restaurant.address" class="text-xs text-slate-500 mb-4">
        {{ restaurant.address }}
      </p>

      <!-- Formules du midi extraites -->
      <div class="mt-2 mb-4">
        <div v-if="hasFormulas" class="space-y-2">
          <div 
            v-for="(f, idx) in restaurant.lunch_formulas" 
            :key="idx"
            class="p-2.5 rounded-xl bg-amber-50/40 border border-amber-200/60 text-xs"
          >
            <div class="flex items-center justify-between gap-2 font-bold text-slate-900">
              <span class="text-slate-800">{{ f.name }}</span>
              <span class="text-orange-700 font-extrabold shrink-0 bg-white px-2 py-0.5 rounded-md border border-amber-200/80">{{ f.price }}</span>
            </div>
            <p v-if="f.description" class="text-slate-600 mt-1 text-[11px] leading-relaxed">
              {{ f.description }}
            </p>
          </div>
        </div>

        <div v-else-if="restaurant.menu_summary" class="p-3 rounded-xl bg-slate-50 border border-slate-200/80 text-xs text-slate-700">
          {{ restaurant.menu_summary }}
        </div>
      </div>
    </div>

    <!-- Pied de carte : Liens & Sélecteur de rang -->
    <div class="pt-3 border-t border-slate-100 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
      <!-- Liens externes (Site officiel & Fiche Google) -->
      <div class="flex flex-wrap items-center gap-3 text-xs">
        <a 
          v-if="restaurant.website_url"
          :href="restaurant.website_url"
          target="_blank"
          rel="noopener noreferrer"
          class="inline-flex items-center gap-1 font-semibold text-orange-700 hover:text-orange-800 hover:underline transition"
        >
          <span>Site officiel</span>
          <ExternalLink class="w-3 h-3" />
        </a>

        <a 
          v-if="restaurant.menu_url"
          :href="restaurant.menu_url"
          target="_blank"
          rel="noopener noreferrer"
          class="inline-flex items-center gap-1 font-semibold text-emerald-700 hover:text-emerald-800 hover:underline transition"
        >
          <FileText v-if="isPdfMenu" class="w-3 h-3" />
          <ExternalLink v-else class="w-3 h-3" />
          <span>{{ isPdfMenu ? 'Carte (PDF)' : 'Carte en ligne' }}</span>
        </a>

        <a 
          v-if="restaurant.google_maps_url"
          :href="restaurant.google_maps_url"
          target="_blank"
          rel="noopener noreferrer"
          class="inline-flex items-center gap-1 font-medium text-blue-600 hover:text-blue-800 hover:underline transition"
          title="Consulter la fiche Google Maps avec avis et photos des plats"
        >
          <MapPin class="w-3 h-3 text-blue-500" />
          <span>Fiche Google & Avis</span>
        </a>
      </div>

      <!-- Boutons de classement (1er, 2e, 3e choix) -->
      <div class="flex items-center gap-1.5 self-end sm:self-auto w-full sm:w-auto">
        <button
          type="button"
          :disabled="disabled"
          @click="handleRankClick(1)"
          :class="[
            currentRank === 1 
              ? 'bg-amber-500 text-white font-bold ring-2 ring-amber-400 shadow-sm border border-amber-600' 
              : 'bg-white hover:bg-amber-50 text-slate-800 border-2 border-slate-200 hover:border-amber-400',
            'flex-1 sm:flex-none px-3.5 py-2 rounded-xl text-xs font-bold transition btn-interaction flex items-center justify-center gap-1 cursor-pointer'
          ]"
          title="1er Choix (attribue 3 points)"
        >
          <Check v-if="currentRank === 1" class="w-3.5 h-3.5 stroke-[3]" />
          <span>1er (3 pts)</span>
        </button>

        <button
          type="button"
          :disabled="disabled"
          @click="handleRankClick(2)"
          :class="[
            currentRank === 2 
              ? 'bg-slate-700 text-white font-bold ring-2 ring-slate-500 shadow-sm border border-slate-800' 
              : 'bg-white hover:bg-slate-100 text-slate-800 border-2 border-slate-200 hover:border-slate-500',
            'flex-1 sm:flex-none px-3.5 py-2 rounded-xl text-xs font-bold transition btn-interaction flex items-center justify-center gap-1 cursor-pointer'
          ]"
          title="2e Choix (attribue 2 points)"
        >
          <Check v-if="currentRank === 2" class="w-3.5 h-3.5 stroke-[3]" />
          <span>2e (2 pts)</span>
        </button>

        <button
          type="button"
          :disabled="disabled"
          @click="handleRankClick(3)"
          :class="[
            currentRank === 3 
              ? 'bg-amber-900 text-white font-bold ring-2 ring-amber-700 shadow-sm border border-amber-950' 
              : 'bg-white hover:bg-amber-50 text-slate-800 border-2 border-slate-200 hover:border-amber-700',
            'flex-1 sm:flex-none px-3.5 py-2 rounded-xl text-xs font-bold transition btn-interaction flex items-center justify-center gap-1 cursor-pointer'
          ]"
          title="3e Choix (attribue 1 point)"
        >
          <Check v-if="currentRank === 3" class="w-3.5 h-3.5 stroke-[3]" />
          <span>3e (1 pt)</span>
        </button>
      </div>
    </div>
  </div>
</template>
