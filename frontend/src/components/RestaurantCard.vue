<script setup>
import { computed } from 'vue';
import { ExternalLink, Footprints, UtensilsCrossed, Check } from 'lucide-vue-next';

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

function handleRankClick(rank) {
  if (props.disabled) return;
  emit('toggleRank', { restaurantId: props.restaurant.id, rank });
}
</script>

<template>
  <div 
    :class="[
      'rounded-2xl border p-5 sm:p-6 transition-all duration-200 bg-white relative flex flex-col justify-between',
      currentRank === 1 ? 'border-amber-500 ring-2 ring-amber-500/20 shadow-md bg-amber-50/10' :
      currentRank === 2 ? 'border-slate-400 ring-2 ring-slate-400/20 shadow-sm' :
      currentRank === 3 ? 'border-amber-700/60 ring-2 ring-amber-700/10 shadow-sm' :
      'border-slate-200 hover:border-slate-300 shadow-xs'
    ]"
  >
    <!-- En-tête : Nom, Cuisine, Distance -->
    <div>
      <div class="flex items-start justify-between gap-3 mb-2">
        <div>
          <span class="inline-block text-xs font-semibold px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700 mb-1.5">
            {{ restaurant.cuisine || 'Restaurant' }}
          </span>
          <h3 class="text-lg font-bold text-slate-900 leading-tight">
            {{ restaurant.name }}
          </h3>
        </div>

        <!-- Badge temps de marche -->
        <div class="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-emerald-50 text-emerald-800 border border-emerald-200/60 text-xs font-medium shrink-0">
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
      <div class="mt-3 mb-4">
        <div v-if="hasFormulas" class="space-y-2">
          <div 
            v-for="(f, idx) in restaurant.lunch_formulas" 
            :key="idx"
            class="p-2.5 rounded-xl bg-slate-50 border border-slate-200/80 text-xs"
          >
            <div class="flex items-center justify-between gap-2 font-semibold text-slate-900">
              <span>{{ f.name }}</span>
              <span class="text-brand-700 font-bold shrink-0">{{ f.price }}</span>
            </div>
            <p v-if="f.description" class="text-slate-600 mt-0.5 text-[11px] leading-relaxed">
              {{ f.description }}
            </p>
          </div>
        </div>

        <div v-else-if="restaurant.menu_summary" class="p-3 rounded-xl bg-slate-50 border border-slate-200/70 text-xs text-slate-700 italic">
          {{ restaurant.menu_summary }}
        </div>
      </div>
    </div>

    <!-- Pied de carte : Lien externe & Sélecteur de rang -->
    <div class="pt-3 border-t border-slate-100 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
      <!-- Lien site web officiel si disponible -->
      <div>
        <a 
          v-if="restaurant.website_url || restaurant.menu_url"
          :href="restaurant.menu_url || restaurant.website_url"
          target="_blank"
          rel="noopener noreferrer"
          class="inline-flex items-center gap-1 text-xs font-medium text-slate-600 hover:text-brand-600 transition"
        >
          <span>Consulter le site / carte</span>
          <ExternalLink class="w-3 h-3" />
        </a>
        <span v-else class="text-xs text-slate-400 italic">
          Carte sur place
        </span>
      </div>

      <!-- Boutons de classement (1er, 2e, 3e choix) -->
      <div class="flex items-center gap-1.5 self-end sm:self-auto w-full sm:w-auto">
        <button
          type="button"
          :disabled="disabled"
          @click="handleRankClick(1)"
          :class="[
            currentRank === 1 
              ? 'bg-amber-500 text-white font-bold ring-2 ring-amber-500/40 shadow-xs' 
              : 'bg-slate-100 hover:bg-slate-200 text-slate-700',
            'flex-1 sm:flex-none px-3 py-1.5 rounded-lg text-xs font-medium transition btn-interaction flex items-center justify-center gap-1 cursor-pointer'
          ]"
          title="1er Choix (attribue 3 points)"
        >
          <Check v-if="currentRank === 1" class="w-3.5 h-3.5" />
          <span>1er (3 pts)</span>
        </button>

        <button
          type="button"
          :disabled="disabled"
          @click="handleRankClick(2)"
          :class="[
            currentRank === 2 
              ? 'bg-slate-700 text-white font-bold ring-2 ring-slate-700/40 shadow-xs' 
              : 'bg-slate-100 hover:bg-slate-200 text-slate-700',
            'flex-1 sm:flex-none px-3 py-1.5 rounded-lg text-xs font-medium transition btn-interaction flex items-center justify-center gap-1 cursor-pointer'
          ]"
          title="2e Choix (attribue 2 points)"
        >
          <Check v-if="currentRank === 2" class="w-3.5 h-3.5" />
          <span>2e (2 pts)</span>
        </button>

        <button
          type="button"
          :disabled="disabled"
          @click="handleRankClick(3)"
          :class="[
            currentRank === 3 
              ? 'bg-amber-800 text-white font-bold ring-2 ring-amber-800/40 shadow-xs' 
              : 'bg-slate-100 hover:bg-slate-200 text-slate-700',
            'flex-1 sm:flex-none px-3 py-1.5 rounded-lg text-xs font-medium transition btn-interaction flex items-center justify-center gap-1 cursor-pointer'
          ]"
          title="3e Choix (attribue 1 point)"
        >
          <Check v-if="currentRank === 3" class="w-3.5 h-3.5" />
          <span>3e (1 pt)</span>
        </button>
      </div>
    </div>
  </div>
</template>
