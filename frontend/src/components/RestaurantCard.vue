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
      'rounded-2xl border p-5 sm:p-6 transition-all duration-200 relative flex flex-col justify-between bg-[#FFFDF9]',
      currentRank === 1 ? 'border-[#B85B43] ring-1 ring-[#B85B43]/30 bg-[#FDFBF9]' :
      currentRank === 2 ? 'border-[#5C6F5A] ring-1 ring-[#5C6F5A]/30 bg-[#FAFBF9]' :
      currentRank === 3 ? 'border-[#82786D] ring-1 ring-[#82786D]/30 bg-[#FAF9F7]' :
      'border-[#E8E3DA] hover:border-[#DDD7CD]'
    ]"
  >
    <!-- Badge de choix actif sur la carte -->
    <div 
      v-if="currentRank"
      :class="[
        currentRank === 1 ? 'bg-[#B85B43] text-white' :
        currentRank === 2 ? 'bg-[#5C6F5A] text-white' :
        'bg-[#82786D] text-white',
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
          <span class="inline-block text-[11px] font-medium px-2.5 py-0.5 rounded-md bg-[#FAF8F5] text-[#57534E] border border-[#E8E3DA]">
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
            class="inline-block text-[10px] font-medium px-2 py-0.5 rounded-md bg-[#FBF4F1] text-[#B85B43] border border-[#E8C7BE]"
          >
            Coup de cœur
          </span>
        </div>

        <!-- Temps de marche -->
        <div class="inline-flex items-center gap-1 text-xs font-medium text-[#78716C] shrink-0">
          <Footprints class="w-3.5 h-3.5 text-[#B85B43]" />
          <span class="font-medium text-[#292524]">{{ restaurant.walking_time_min }} min</span>
          <span class="text-[#DDD7CD]">•</span>
          <span>{{ restaurant.distance_meters }} m</span>
        </div>
      </div>

      <!-- Titre du restaurant en police poétique Shippori Mincho -->
      <h3 class="font-serif text-xl sm:text-2xl font-normal text-[#292524] tracking-wide leading-snug mb-1">
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
            class="p-3 rounded-xl bg-[#FAF8F5] border border-[#EFEBE3] text-xs"
          >
            <div class="flex items-center justify-between gap-2 text-[#292524]">
              <span class="font-medium">{{ f.name }}</span>
              <span class="text-[#B85B43] font-semibold shrink-0 bg-[#FFFDF9] px-2 py-0.5 rounded-md border border-[#E8E3DA]">{{ f.price }}</span>
            </div>
            <p v-if="f.description" class="text-[#78716C] mt-1 text-[11px] leading-relaxed">
              {{ f.description }}
            </p>
          </div>
        </div>

        <div v-else-if="restaurant.menu_summary" class="p-3 rounded-xl bg-[#FAF8F5] border border-[#EFEBE3] text-xs text-[#57534E]">
          {{ restaurant.menu_summary }}
        </div>
      </div>
    </div>

    <!-- Section inférieure : Liens de découverte + Boutons de vote -->
    <div class="space-y-3 pt-3 border-t border-[#EFEBE3]">
      <!-- Ligne 1 : Liens externes (Site officiel, Carte en ligne, Google Maps) -->
      <div class="flex flex-wrap items-center gap-2 text-xs">
        <!-- Badge Carte en ligne (mise en avant si disponible) -->
        <a 
          v-if="restaurant.menu_url"
          :href="restaurant.menu_url"
          target="_blank"
          rel="noopener noreferrer"
          class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-[#F3F6F2] text-[#3E503B] border border-[#CBD8C8] font-medium hover:bg-[#E5ECE4] transition"
        >
          <FileText v-if="isPdfMenu" class="w-3.5 h-3.5 text-[#5C6F5A]" />
          <ExternalLink v-else class="w-3.5 h-3.5 text-[#5C6F5A]" />
          <span>{{ isPdfMenu ? 'Carte PDF' : 'Carte en ligne' }}</span>
        </a>

        <!-- Fiche Google Maps -->
        <a 
          v-if="restaurant.google_maps_url"
          :href="restaurant.google_maps_url"
          target="_blank"
          rel="noopener noreferrer"
          class="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-[#FAF8F5] text-[#57534E] hover:text-[#292524] hover:bg-[#F3EFEA] border border-[#E8E3DA] font-medium transition"
          title="Consulter la fiche Google Maps avec avis et photos des plats"
        >
          <MapPin class="w-3.5 h-3.5 text-[#78716C]" />
          <span>Google & Avis</span>
        </a>

        <!-- Site officiel -->
        <a 
          v-if="restaurant.website_url"
          :href="restaurant.website_url"
          target="_blank"
          rel="noopener noreferrer"
          class="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-[#FAF8F5] text-[#57534E] hover:text-[#292524] hover:bg-[#F3EFEA] border border-[#E8E3DA] font-medium transition"
        >
          <span>Site officiel</span>
          <ExternalLink class="w-3 h-3 text-[#A8A29E]" />
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
              ? 'bg-[#B85B43] text-white font-medium border border-[#9E4C36]' 
              : 'bg-[#FFFDF9] hover:bg-[#FBF4F1] text-[#292524] hover:text-[#B85B43] border border-[#E8E3DA] hover:border-[#E8C7BE]',
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
              ? 'bg-[#5C6F5A] text-white font-medium border border-[#4A5B48]' 
              : 'bg-[#FFFDF9] hover:bg-[#F3F6F2] text-[#292524] hover:text-[#5C6F5A] border border-[#E8E3DA] hover:border-[#CBD8C8]',
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
              ? 'bg-[#82786D] text-white font-medium border border-[#6E655B]' 
              : 'bg-[#FFFDF9] hover:bg-[#F7F5F2] text-[#292524] hover:text-[#82786D] border border-[#E8E3DA] hover:border-[#DDD7CD]',
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

