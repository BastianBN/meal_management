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
      'rounded-2xl border p-5 sm:p-6 transition-all duration-200 relative flex flex-col justify-between bg-white',
      currentRank === 1 ? 'border-amber-600/70 ring-2 ring-amber-500/20 shadow-md bg-[#FFFCF5]' :
      currentRank === 2 ? 'border-slate-600/70 ring-2 ring-slate-500/20 shadow-sm bg-[#FAFAFA]' :
      currentRank === 3 ? 'border-amber-900/60 ring-2 ring-amber-900/15 shadow-sm bg-[#FDFBF7]' :
      'border-[#E7E2D9] hover:border-[#D5CEC2] shadow-[0_2px_8px_rgba(28,25,23,0.03)] hover:shadow-[0_4px_16px_rgba(28,25,23,0.06)]'
    ]"
  >
    <!-- Badge de choix actif sur la carte -->
    <div 
      v-if="currentRank"
      :class="[
        currentRank === 1 ? 'bg-amber-600 text-white' :
        currentRank === 2 ? 'bg-slate-800 text-white' :
        'bg-amber-950 text-white',
        'absolute -top-3 right-5 px-3 py-0.5 rounded-full text-xs font-bold shadow-xs flex items-center gap-1.5'
      ]"
    >
      <Check class="w-3.5 h-3.5 stroke-[2.5]" />
      <span>{{ currentRank === 1 ? '1er Choix (+3 pts)' : currentRank === 2 ? '2e Choix (+2 pts)' : '3e Choix (+1 pt)' }}</span>
    </div>

    <!-- Section principale de la carte -->
    <div>
      <!-- Ligne supérieure : Cuisine, Note & Distance -->
      <div class="flex items-center justify-between gap-2 flex-wrap mb-2">
        <div class="flex items-center gap-1.5 flex-wrap">
          <span class="inline-block text-[11px] font-semibold px-2.5 py-0.5 rounded-md bg-[#F3EFEA] text-[#57534E]">
            {{ restaurant.cuisine || 'Bistrot' }}
          </span>

          <!-- Badge Note / Avis -->
          <div 
            v-if="restaurant.rating"
            class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-[#FEF3C7] text-[#92400E] text-xs font-bold"
            :title="`${restaurant.rating_count || 100} avis clients vérifiés`"
          >
            <Star class="w-3 h-3 text-amber-500 fill-amber-400" />
            <span>{{ Number(restaurant.rating).toFixed(1) }}</span>
            <span v-if="restaurant.rating_count" class="text-[10px] text-amber-700 font-normal">({{ restaurant.rating_count }})</span>
          </div>

          <span 
            v-if="restaurant.rating >= 4.7"
            class="inline-block text-[10px] font-bold px-2 py-0.5 rounded-md bg-rose-50 text-rose-800 border border-rose-200/60"
          >
            Coup de cœur
          </span>
        </div>

        <!-- Temps de marche -->
        <div class="inline-flex items-center gap-1 text-xs font-medium text-[#78716C] shrink-0">
          <Footprints class="w-3.5 h-3.5 text-[#C2410C]" />
          <span class="font-semibold text-[#1C1917]">{{ restaurant.walking_time_min }} min</span>
          <span class="text-[#D5CEC2]">•</span>
          <span>{{ restaurant.distance_meters }} m</span>
        </div>
      </div>

      <!-- Titre du restaurant en police éditoriale Fraunces -->
      <h3 class="font-serif text-xl sm:text-2xl font-bold text-[#1C1917] tracking-tight leading-snug mb-1">
        {{ restaurant.name }}
      </h3>

      <p v-if="restaurant.address" class="text-xs text-[#78716C] mb-4 line-clamp-1">
        {{ restaurant.address }}
      </p>

      <!-- Formules du midi extraites -->
      <div class="mt-2 mb-4">
        <div v-if="hasFormulas" class="space-y-2">
          <div 
            v-for="(f, idx) in restaurant.lunch_formulas" 
            :key="idx"
            class="p-3 rounded-xl bg-[#FAF7F2] border border-[#EFE9E0] text-xs"
          >
            <div class="flex items-center justify-between gap-2 font-bold text-[#1C1917]">
              <span class="font-medium text-[#292524]">{{ f.name }}</span>
              <span class="text-[#C2410C] font-extrabold shrink-0 bg-white px-2 py-0.5 rounded-md border border-[#E7E2D9]">{{ f.price }}</span>
            </div>
            <p v-if="f.description" class="text-[#78716C] mt-1 text-[11px] leading-relaxed">
              {{ f.description }}
            </p>
          </div>
        </div>

        <div v-else-if="restaurant.menu_summary" class="p-3 rounded-xl bg-[#FAF7F2] border border-[#EFE9E0] text-xs text-[#57534E]">
          {{ restaurant.menu_summary }}
        </div>
      </div>
    </div>

    <!-- Section inférieure : Liens de découverte + Boutons de vote -->
    <div class="space-y-3 pt-3 border-t border-[#EFE9E0]">
      <!-- Ligne 1 : Liens externes (Site officiel, Carte en ligne, Google Maps) -->
      <div class="flex flex-wrap items-center gap-2 text-xs">
        <!-- Badge Carte en ligne (mise en avant si disponible) -->
        <a 
          v-if="restaurant.menu_url"
          :href="restaurant.menu_url"
          target="_blank"
          rel="noopener noreferrer"
          class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-emerald-50 text-emerald-800 border border-emerald-200/80 font-semibold hover:bg-emerald-100 transition"
        >
          <FileText v-if="isPdfMenu" class="w-3.5 h-3.5 text-emerald-600" />
          <ExternalLink v-else class="w-3.5 h-3.5 text-emerald-600" />
          <span>{{ isPdfMenu ? 'Carte PDF' : 'Carte en ligne' }}</span>
        </a>

        <!-- Fiche Google Maps -->
        <a 
          v-if="restaurant.google_maps_url"
          :href="restaurant.google_maps_url"
          target="_blank"
          rel="noopener noreferrer"
          class="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-[#F5F2EB] text-[#57534E] hover:text-[#1C1917] hover:bg-[#EAE4D9] font-medium transition"
          title="Consulter la fiche Google Maps avec avis et photos des plats"
        >
          <MapPin class="w-3.5 h-3.5 text-blue-600" />
          <span>Google & Avis</span>
        </a>

        <!-- Site officiel -->
        <a 
          v-if="restaurant.website_url"
          :href="restaurant.website_url"
          target="_blank"
          rel="noopener noreferrer"
          class="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-[#F5F2EB] text-[#57534E] hover:text-[#1C1917] hover:bg-[#EAE4D9] font-medium transition"
        >
          <span>Site officiel</span>
          <ExternalLink class="w-3 h-3 text-[#78716C]" />
        </a>
      </div>

      <!-- Ligne 2 : Boutons de classement (1er, 2e, 3e choix) garantis pleine largeur -->
      <div class="grid grid-cols-3 gap-2 w-full">
        <button
          type="button"
          :disabled="disabled"
          @click="handleRankClick(1)"
          :class="[
            currentRank === 1 
              ? 'bg-amber-600 text-white font-bold ring-2 ring-amber-500/40 shadow-sm border border-amber-700' 
              : 'bg-white hover:bg-amber-50/70 text-[#292524] border border-[#D5CEC2] hover:border-amber-400',
            'w-full py-2 px-1 rounded-xl text-xs font-bold transition btn-interaction flex items-center justify-center gap-1 cursor-pointer'
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
              ? 'bg-slate-800 text-white font-bold ring-2 ring-slate-600/40 shadow-sm border border-slate-900' 
              : 'bg-white hover:bg-slate-100 text-[#292524] border border-[#D5CEC2] hover:border-slate-500',
            'w-full py-2 px-1 rounded-xl text-xs font-bold transition btn-interaction flex items-center justify-center gap-1 cursor-pointer'
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
              ? 'bg-amber-950 text-white font-bold ring-2 ring-amber-900/40 shadow-sm border border-black' 
              : 'bg-white hover:bg-amber-50/70 text-[#292524] border border-[#D5CEC2] hover:border-amber-700',
            'w-full py-2 px-1 rounded-xl text-xs font-bold transition btn-interaction flex items-center justify-center gap-1 cursor-pointer'
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

