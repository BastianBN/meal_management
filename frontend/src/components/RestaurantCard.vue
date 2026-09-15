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
      'rounded-2xl border p-5 sm:p-6 transition-all duration-200 relative flex flex-col justify-between bg-[#FFFCF7]',
      currentRank === 1 ? 'border-[#C2542D] ring-1 ring-[#C2542D]/30 bg-[#FFFAF5]' :
      currentRank === 2 ? 'border-[#586F54] ring-1 ring-[#586F54]/30 bg-[#FAFBF8]' :
      currentRank === 3 ? 'border-[#7E6C5C] ring-1 ring-[#7E6C5C]/30 bg-[#FBF9F6]' :
      'border-[#E5D6C5] hover:border-[#DAC7B2]'
    ]"
  >
    <!-- Badge de choix actif sur la carte -->
    <div 
      v-if="currentRank"
      :class="[
        currentRank === 1 ? 'bg-[#C2542D] text-white' :
        currentRank === 2 ? 'bg-[#586F54] text-white' :
        'bg-[#7E6C5C] text-white',
        'absolute -top-3 right-5 px-3 py-0.5 rounded-full text-xs font-medium flex items-center gap-1.5'
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
          <span class="inline-block text-[11px] font-medium px-2.5 py-0.5 rounded-md bg-[#FAF2E8] text-[#5D4B3E] border border-[#E5D6C5]">
            {{ restaurant.cuisine || 'Bistrot' }}
          </span>

          <!-- Badge Note / Avis -->
          <div 
            v-if="restaurant.rating"
            class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-[#FEF3C7] text-[#78350F] text-xs font-medium border border-[#F59E0B]/30"
            :title="`${restaurant.rating_count || 100} avis clients vérifiés`"
          >
            <Star class="w-3 h-3 text-amber-600 fill-amber-500" />
            <span>{{ Number(restaurant.rating).toFixed(1) }}</span>
            <span v-if="restaurant.rating_count" class="text-[10px] text-[#78350F]/70 font-normal">({{ restaurant.rating_count }})</span>
          </div>

          <span 
            v-if="restaurant.rating >= 4.7"
            class="inline-block text-[10px] font-medium px-2 py-0.5 rounded-md bg-[#FAF0E8] text-[#C2542D] border border-[#ECCDBE]"
          >
            Coup de cœur
          </span>
        </div>

        <!-- Temps de marche -->
        <div class="inline-flex items-center gap-1 text-xs font-medium text-[#857263] shrink-0">
          <Footprints class="w-3.5 h-3.5 text-[#C2542D]" />
          <span class="font-medium text-[#2C2019]">{{ restaurant.walking_time_min }} min</span>
          <span class="text-[#DAC7B2]">•</span>
          <span>{{ restaurant.distance_meters }} m</span>
        </div>
      </div>

      <!-- Titre du restaurant en police poétique Shippori Mincho -->
      <h3 class="font-serif text-xl sm:text-2xl font-normal text-[#2C2019] tracking-wide leading-snug mb-1">
        {{ restaurant.name }}
      </h3>

      <p v-if="restaurant.address" class="text-xs text-[#857263] mb-4 line-clamp-1">
        {{ restaurant.address }}
      </p>

      <!-- Formules du midi extraites -->
      <div class="mt-2 mb-4">
        <div v-if="hasFormulas" class="space-y-2">
          <div 
            v-for="(f, idx) in restaurant.lunch_formulas" 
            :key="idx"
            class="p-3 rounded-xl bg-[#FAF2E8] border border-[#EFE4D6] text-xs"
          >
            <div class="flex items-center justify-between gap-2 text-[#2C2019]">
              <span class="font-medium">{{ f.name }}</span>
              <span class="text-[#C2542D] font-semibold shrink-0 bg-[#FFFCF7] px-2 py-0.5 rounded-md border border-[#E5D6C5]">{{ f.price }}</span>
            </div>
            <p v-if="f.description" class="text-[#857263] mt-1 text-[11px] leading-relaxed">
              {{ f.description }}
            </p>
          </div>
        </div>

        <div v-else-if="restaurant.menu_summary" class="p-3 rounded-xl bg-[#FAF2E8] border border-[#EFE4D6] text-xs text-[#5D4B3E]">
          {{ restaurant.menu_summary }}
        </div>
      </div>
    </div>

    <!-- Section inférieure : Liens de découverte + Boutons de vote -->
    <div class="space-y-3 pt-3 border-t border-[#EFE4D6]">
      <!-- Ligne 1 : Liens externes (Site officiel, Carte en ligne, Google Maps) -->
      <div class="flex flex-wrap items-center gap-2 text-xs">
        <!-- Badge Carte en ligne (mise en avant si disponible) -->
        <a 
          v-if="restaurant.menu_url"
          :href="restaurant.menu_url"
          target="_blank"
          rel="noopener noreferrer"
          class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-[#F0F5EE] text-[#364A32] border border-[#C8D7C4] font-medium hover:bg-[#E3ECE0] transition"
        >
          <FileText v-if="isPdfMenu" class="w-3.5 h-3.5 text-[#586F54]" />
          <ExternalLink v-else class="w-3.5 h-3.5 text-[#586F54]" />
          <span>{{ isPdfMenu ? 'Carte PDF' : 'Carte en ligne' }}</span>
        </a>

        <!-- Fiche Google Maps -->
        <a 
          v-if="restaurant.google_maps_url"
          :href="restaurant.google_maps_url"
          target="_blank"
          rel="noopener noreferrer"
          class="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-[#FAF2E8] text-[#5D4B3E] hover:text-[#2C2019] hover:bg-[#F3E8DB] border border-[#E5D6C5] font-medium transition"
          title="Consulter la fiche Google Maps avec avis et photos des plats"
        >
          <MapPin class="w-3.5 h-3.5 text-[#857263]" />
          <span>Google & Avis</span>
        </a>

        <!-- Site officiel -->
        <a 
          v-if="restaurant.website_url"
          :href="restaurant.website_url"
          target="_blank"
          rel="noopener noreferrer"
          class="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-[#FAF2E8] text-[#5D4B3E] hover:text-[#2C2019] hover:bg-[#F3E8DB] border border-[#E5D6C5] font-medium transition"
        >
          <span>Site officiel</span>
          <ExternalLink class="w-3 h-3 text-[#AC9B8D]" />
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
              ? 'bg-[#C2542D] text-white font-medium border border-[#A64320]' 
              : 'bg-[#FFFCF7] hover:bg-[#FAF0E8] text-[#2C2019] hover:text-[#C2542D] border border-[#E5D6C5] hover:border-[#ECCDBE]',
            'w-full py-2 px-1 rounded-xl text-xs font-medium transition btn-interaction flex items-center justify-center gap-1 cursor-pointer'
          ]"
          title="1er Choix (attribue 3 points)"
        >
          <Check v-if="currentRank === 1" class="w-3.5 h-3.5 stroke-[2.5]" />
          <span>1er (3 pts)</span>
        </button>

        <button
          type="button"
          :disabled="disabled"
          @click="handleRankClick(2)"
          :class="[
            currentRank === 2 
              ? 'bg-[#586F54] text-white font-medium border border-[#465A42]' 
              : 'bg-[#FFFCF7] hover:bg-[#F0F5EE] text-[#2C2019] hover:text-[#586F54] border border-[#E5D6C5] hover:border-[#C8D7C4]',
            'w-full py-2 px-1 rounded-xl text-xs font-medium transition btn-interaction flex items-center justify-center gap-1 cursor-pointer'
          ]"
          title="2e Choix (attribue 2 points)"
        >
          <Check v-if="currentRank === 2" class="w-3.5 h-3.5 stroke-[2.5]" />
          <span>2e (2 pts)</span>
        </button>

        <button
          type="button"
          :disabled="disabled"
          @click="handleRankClick(3)"
          :class="[
            currentRank === 3 
              ? 'bg-[#7E6C5C] text-white font-medium border border-[#685749]' 
              : 'bg-[#FFFCF7] hover:bg-[#F4EDE5] text-[#2C2019] hover:text-[#7E6C5C] border border-[#E5D6C5] hover:border-[#DBCFBF]',
            'w-full py-2 px-1 rounded-xl text-xs font-medium transition btn-interaction flex items-center justify-center gap-1 cursor-pointer'
          ]"
          title="3e Choix (attribue 1 point)"
        >
          <Check v-if="currentRank === 3" class="w-3.5 h-3.5 stroke-[2.5]" />
          <span>3e (1 pt)</span>
        </button>
      </div>
    </div>
  </div>
</template>

