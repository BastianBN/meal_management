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
      'rounded-2xl border p-5 sm:p-6 transition-all duration-200 relative flex flex-col justify-between bg-[#191C22] shadow-sm',
      currentRank === 1 ? 'border-[#DC2626] ring-1 ring-[#DC2626]/40 shadow-md shadow-[#DC2626]/10' :
      currentRank === 2 ? 'border-[#D97706] ring-1 ring-[#D97706]/40 shadow-md shadow-[#D97706]/10' :
      currentRank === 3 ? 'border-[#64748B] ring-1 ring-[#64748B]/40 shadow-md shadow-[#64748B]/10' :
      'border-[#383F4C] hover:border-[#4A5364]'
    ]"
  >
    <!-- Badge de choix actif sur l'ardoise -->
    <div 
      v-if="currentRank"
      :class="[
        currentRank === 1 ? 'bg-[#DC2626] text-white border border-[#B91C1C]' :
        currentRank === 2 ? 'bg-[#D97706] text-white border border-[#B45309]' :
        'bg-[#64748B] text-white border border-[#475569]',
        'absolute -top-3 right-5 px-3 py-0.5 rounded-full text-xs font-medium flex items-center gap-1.5 shadow-sm font-sans'
      ]"
    >
      <Check class="w-3.5 h-3.5 stroke-[2.5]" />
      <span>{{ currentRank === 1 ? '1er Choix (+3 pts)' : currentRank === 2 ? '2e Choix (+2 pts)' : '3e Choix (+1 pt)' }}</span>
    </div>

    <!-- Section principale de l'ardoise -->
    <div>
      <!-- Ligne supérieure : Cuisine, Note & Distance -->
      <div class="flex items-center justify-between gap-2 flex-wrap mb-2">
        <div class="flex items-center gap-1.5 flex-wrap">
          <span class="inline-block text-[11px] font-medium px-2.5 py-0.5 rounded-md bg-[#22262E] text-[#CBD5E1] border border-[#383F4C] font-sans">
            {{ restaurant.cuisine || 'Bistrot' }}
          </span>

          <!-- Badge Note / Avis -->
          <div 
            v-if="restaurant.rating"
            class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-[#2A2315] text-[#FDE68A] text-xs font-medium border border-[#D97706]/40 font-sans"
            :title="`${restaurant.rating_count || 100} avis clients vérifiés`"
          >
            <Star class="w-3 h-3 text-[#D97706] fill-[#D97706]" />
            <span>{{ Number(restaurant.rating).toFixed(1) }}</span>
            <span v-if="restaurant.rating_count" class="text-[10px] text-[#FDE68A]/70 font-normal">({{ restaurant.rating_count }})</span>
          </div>

          <span 
            v-if="restaurant.rating >= 4.7"
            class="inline-block text-[10px] font-medium px-2 py-0.5 rounded-md bg-[#2E1819] text-[#FCA5A5] border border-[#DC2626]/40 font-sans"
          >
            Coup de cœur
          </span>
        </div>

        <!-- Temps de marche -->
        <div class="inline-flex items-center gap-1 text-xs font-medium text-[#94A3B8] shrink-0 font-sans">
          <Footprints class="w-3.5 h-3.5 text-[#D97706]" />
          <span class="font-medium text-[#F8FAFC]">{{ restaurant.walking_time_min }} min</span>
          <span class="text-[#475569]">•</span>
          <span>{{ restaurant.distance_meters }} m</span>
        </div>
      </div>

      <!-- Titre du restaurant en police Cormorant Garamond façon écriture craie -->
      <h3 class="font-serif text-2xl sm:text-3xl font-normal text-[#F8FAFC] tracking-wide leading-snug mb-1">
        {{ restaurant.name }}
      </h3>

      <p v-if="restaurant.address" class="text-xs text-[#94A3B8] mb-4 line-clamp-1 font-sans">
        {{ restaurant.address }}
      </p>

      <!-- Formules du midi façon ardoise des suggestions -->
      <div class="mt-2 mb-4">
        <div v-if="hasFormulas" class="space-y-2">
          <div 
            v-for="(f, idx) in restaurant.lunch_formulas" 
            :key="idx"
            class="p-3 rounded-xl bg-[#22262E] border border-[#2F3642] text-xs"
          >
            <div class="flex items-center justify-between gap-2 text-[#F8FAFC]">
              <span class="font-medium font-serif text-sm tracking-wide text-[#F1EADF]">{{ f.name }}</span>
              <span class="text-[#FDE68A] font-medium shrink-0 bg-[#191C22] px-2 py-0.5 rounded-md border border-[#383F4C] font-sans">{{ f.price }}</span>
            </div>
            <p v-if="f.description" class="text-[#94A3B8] mt-1 text-[11px] leading-relaxed font-sans">
              {{ f.description }}
            </p>
          </div>
        </div>

        <div v-else-if="restaurant.menu_summary" class="p-3 rounded-xl bg-[#22262E] border border-[#2F3642] text-xs text-[#CBD5E1] font-sans">
          {{ restaurant.menu_summary }}
        </div>
      </div>
    </div>

    <!-- Section inférieure : Liens de découverte + Boutons de vote Trio Bistrot -->
    <div class="space-y-3 pt-3 border-t border-[#2A2F39]">
      <!-- Ligne 1 : Liens externes (Site officiel, Carte en ligne, Google Maps) -->
      <div class="flex flex-wrap items-center gap-2 text-xs font-sans">
        <!-- Badge Carte en ligne -->
        <a 
          v-if="restaurant.menu_url"
          :href="restaurant.menu_url"
          target="_blank"
          rel="noopener noreferrer"
          class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-[#1E293B] text-[#93C5FD] border border-[#3B82F6]/30 font-medium hover:bg-[#283548] transition"
        >
          <FileText v-if="isPdfMenu" class="w-3.5 h-3.5 text-[#60A5FA]" />
          <ExternalLink v-else class="w-3.5 h-3.5 text-[#60A5FA]" />
          <span>{{ isPdfMenu ? 'Carte PDF' : 'Carte en ligne' }}</span>
        </a>

        <!-- Fiche Google Maps -->
        <a 
          v-if="restaurant.google_maps_url"
          :href="restaurant.google_maps_url"
          target="_blank"
          rel="noopener noreferrer"
          class="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-[#22262E] text-[#CBD5E1] hover:text-[#F8FAFC] hover:bg-[#2A2F39] border border-[#383F4C] font-medium transition"
          title="Consulter la fiche Google Maps avec avis et photos des plats"
        >
          <MapPin class="w-3.5 h-3.5 text-[#94A3B8]" />
          <span>Google & Avis</span>
        </a>

        <!-- Site officiel -->
        <a 
          v-if="restaurant.website_url"
          :href="restaurant.website_url"
          target="_blank"
          rel="noopener noreferrer"
          class="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-[#22262E] text-[#CBD5E1] hover:text-[#F8FAFC] hover:bg-[#2A2F39] border border-[#383F4C] font-medium transition"
        >
          <span>Site officiel</span>
          <ExternalLink class="w-3 h-3 text-[#94A3B8]" />
        </a>
      </div>

      <!-- Ligne 2 : Boutons de classement (1er Rouge Bistrot, 2e Laiton, 3e Zinc) -->
      <div class="grid grid-cols-3 gap-2 w-full font-sans">
        <button
          type="button"
          :disabled="disabled"
          @click="handleRankClick(1)"
          :class="[
            currentRank === 1 
              ? 'bg-[#DC2626] text-white font-medium border border-[#B91C1C] shadow-sm' 
              : 'bg-[#22262E] hover:bg-[#2E1819] text-[#E2E8F0] hover:text-[#FCA5A5] border border-[#383F4C] hover:border-[#DC2626]/60',
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
              ? 'bg-[#D97706] text-white font-medium border border-[#B45309] shadow-sm' 
              : 'bg-[#22262E] hover:bg-[#2B2317] text-[#E2E8F0] hover:text-[#FDE68A] border border-[#383F4C] hover:border-[#D97706]/60',
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
              ? 'bg-[#64748B] text-white font-medium border border-[#475569] shadow-sm' 
              : 'bg-[#22262E] hover:bg-[#242933] text-[#E2E8F0] hover:text-[#CBD5E1] border border-[#383F4C] hover:border-[#64748B]/60',
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

