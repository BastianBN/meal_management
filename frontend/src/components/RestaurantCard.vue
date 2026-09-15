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
      'bistro-card-frame rounded-3xl p-5 sm:p-7 transition-all duration-200 relative flex flex-col justify-between group',
      currentRank === 1 ? 'ring-2 ring-[var(--accent-red)] shadow-xl' :
      currentRank === 2 ? 'ring-2 ring-[var(--accent-brass)] shadow-xl' :
      currentRank === 3 ? 'ring-2 ring-[var(--accent-zinc)] shadow-xl' :
      'hover:border-[var(--accent-brass)]'
    ]"
  >
    <!-- Sceau / Médaillon de choix actif en relief -->
    <div 
      v-if="currentRank"
      :class="[
        currentRank === 1 ? 'bg-[var(--accent-red)] text-white border-2 border-white/40 shadow-lg' :
        currentRank === 2 ? 'bg-[var(--accent-brass)] text-white border-2 border-white/40 shadow-lg' :
        'bg-[var(--accent-zinc)] text-white border-2 border-white/40 shadow-lg',
        'absolute -top-3.5 right-6 px-3.5 py-1 rounded-full text-xs font-serif tracking-wider uppercase font-bold flex items-center gap-1.5 z-10'
      ]"
    >
      <Check class="w-3.5 h-3.5 stroke-[2.5]" />
      <span>{{ currentRank === 1 ? '1er Choix (+3 pts)' : currentRank === 2 ? '2e Choix (+2 pts)' : '3e Choix (+1 pt)' }}</span>
    </div>

    <!-- Section principale du feuillet de table -->
    <div>
      <!-- Ligne supérieure : Spécialité & Allure de marche -->
      <div class="flex items-center justify-between gap-2 flex-wrap mb-2.5">
        <div class="flex items-center gap-2 flex-wrap">
          <span class="inline-block text-xs font-serif italic px-3 py-0.5 rounded-full bg-[var(--bg-surface-inset)] text-[var(--text-muted)] border border-[var(--border-subtle)]">
            ❧ {{ restaurant.cuisine || 'Bistrot de quartier' }} ☙
          </span>

          <!-- Badge Note & Avis -->
          <div 
            v-if="restaurant.rating"
            class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-[var(--accent-brass-soft)] text-[var(--accent-brass)] text-xs font-medium border border-[var(--accent-brass-border)]"
            :title="`${restaurant.rating_count || 100} avis clients vérifiés`"
          >
            <Star class="w-3 h-3 text-[var(--accent-brass)] fill-[var(--accent-brass)]" />
            <span class="font-serif font-bold text-sm leading-none">{{ Number(restaurant.rating).toFixed(1) }}</span>
            <span v-if="restaurant.rating_count" class="text-[10px] opacity-75 font-normal font-sans">({{ restaurant.rating_count }})</span>
          </div>

          <span 
            v-if="restaurant.rating >= 4.7"
            class="inline-block text-[10px] font-serif uppercase tracking-widest font-bold px-2.5 py-0.5 rounded-full bg-[var(--accent-red-soft)] text-[var(--accent-red)] border border-[var(--accent-red-border)]"
          >
            Coup de cœur
          </span>
        </div>

        <!-- Temps de marche avec compas -->
        <div class="inline-flex items-center gap-1.5 text-xs text-[var(--text-muted)] shrink-0 font-serif">
          <Footprints class="w-3.5 h-3.5 text-[var(--accent-brass)]" />
          <span class="font-bold text-[var(--text-main)]">{{ restaurant.walking_time_min }} min</span>
          <span class="text-[var(--text-faint)]">•</span>
          <span>{{ restaurant.distance_meters }} m</span>
        </div>
      </div>

      <!-- Titre du restaurant en majestueuse typographie -->
      <h3 class="font-display sm:font-serif text-2xl sm:text-3xl font-normal text-[var(--text-main)] tracking-wide leading-snug mb-1">
        {{ restaurant.name }}
      </h3>

      <p v-if="restaurant.address" class="text-xs text-[var(--text-faint)] mb-4 line-clamp-1 font-serif">
        {{ restaurant.address }}
      </p>

      <!-- Formules du midi façon carte de brasserie avec points de conduite (Leader dots) -->
      <div class="mt-3 mb-5">
        <div v-if="hasFormulas" class="space-y-3">
          <div 
            v-for="(f, idx) in restaurant.lunch_formulas" 
            :key="idx"
            class="p-3.5 rounded-2xl bg-[var(--bg-surface-subtle)] border border-[var(--border-subtle)] text-xs"
          >
            <div class="menu-leader-line">
              <span class="font-serif text-sm sm:text-base font-semibold text-[var(--text-main)] tracking-wide">{{ f.name }}</span>
              <span class="menu-leader-dots"></span>
              <span class="font-serif text-sm sm:text-base font-bold text-[var(--accent-brass)] shrink-0 bg-[var(--bg-surface)] px-2.5 py-0.5 rounded-lg border border-[var(--border-subtle)] shadow-2xs">{{ f.price }}</span>
            </div>
            <p v-if="f.description" class="text-[var(--text-muted)] mt-1.5 text-[11px] font-serif italic leading-relaxed">
              {{ f.description }}
            </p>
          </div>
        </div>

        <div v-else-if="restaurant.menu_summary" class="p-3.5 rounded-2xl bg-[var(--bg-surface-subtle)] border border-[var(--border-subtle)] text-xs text-[var(--text-muted)] font-serif italic leading-relaxed">
          {{ restaurant.menu_summary }}
        </div>
      </div>
    </div>

    <!-- Section inférieure : Liens de découverte + Trio de Jetons de vote -->
    <div class="space-y-3.5 pt-3.5 border-t border-[var(--border-subtle)]">
      <!-- Ligne 1 : Liens externes (Site officiel, Carte en ligne, Google Maps) -->
      <div class="flex flex-wrap items-center gap-2 text-xs">
        <!-- Badge Carte en ligne -->
        <a 
          v-if="restaurant.menu_url"
          :href="restaurant.menu_url"
          target="_blank"
          rel="noopener noreferrer"
          class="inline-flex items-center gap-1.5 px-3 py-1 rounded-xl bg-[var(--bg-surface-inset)] text-[var(--accent-brass)] border border-[var(--border-main)] font-medium hover:border-[var(--accent-brass)] transition"
        >
          <FileText v-if="isPdfMenu" class="w-3.5 h-3.5" />
          <ExternalLink v-else class="w-3.5 h-3.5" />
          <span class="font-serif text-xs">{{ isPdfMenu ? 'Carte PDF' : 'Carte en ligne' }}</span>
        </a>

        <!-- Fiche Google Maps -->
        <a 
          v-if="restaurant.google_maps_url"
          :href="restaurant.google_maps_url"
          target="_blank"
          rel="noopener noreferrer"
          class="inline-flex items-center gap-1 px-3 py-1 rounded-xl bg-[var(--bg-surface-inset)] text-[var(--text-muted)] hover:text-[var(--text-main)] border border-[var(--border-main)] font-medium transition"
          title="Consulter la fiche Google Maps avec avis et photos des plats"
        >
          <MapPin class="w-3.5 h-3.5 text-[var(--text-faint)]" />
          <span class="font-serif text-xs">Avis Google</span>
        </a>

        <!-- Site officiel -->
        <a 
          v-if="restaurant.website_url"
          :href="restaurant.website_url"
          target="_blank"
          rel="noopener noreferrer"
          class="inline-flex items-center gap-1 px-3 py-1 rounded-xl bg-[var(--bg-surface-inset)] text-[var(--text-muted)] hover:text-[var(--text-main)] border border-[var(--border-main)] font-medium transition"
        >
          <span class="font-serif text-xs">Site officiel</span>
          <ExternalLink class="w-3 h-3 text-[var(--text-faint)]" />
        </a>
      </div>

      <!-- Ligne 2 : Trio de Jetons de Bistrot pour le vote (1er Rouge Bordeaux, 2e Laiton, 3e Zinc) -->
      <div class="grid grid-cols-3 gap-2 w-full">
        <!-- Jeton 1 -->
        <button
          type="button"
          :disabled="disabled"
          @click="handleRankClick(1)"
          :class="[
            currentRank === 1 
              ? 'bg-[var(--accent-red)] text-white font-serif text-sm font-bold border-2 border-white/50 shadow-md scale-[1.02]' 
              : 'bg-[var(--bg-surface-inset)] hover:bg-[var(--accent-red-soft)] text-[var(--text-main)] hover:text-[var(--accent-red)] border border-[var(--border-main)] hover:border-[var(--accent-red)]',
            'w-full py-2.5 px-1 rounded-xl text-xs transition btn-interaction flex items-center justify-center gap-1.5 cursor-pointer select-none'
          ]"
          title="1er Choix (attribue 3 points)"
        >
          <span class="w-4 h-4 rounded-full bg-white/20 flex items-center justify-center text-[10px] font-sans font-bold">1</span>
          <span class="font-serif font-bold">3 pts</span>
          <Check v-if="currentRank === 1" class="w-3 h-3 stroke-[3]" />
        </button>

        <!-- Jeton 2 -->
        <button
          type="button"
          :disabled="disabled"
          @click="handleRankClick(2)"
          :class="[
            currentRank === 2 
              ? 'bg-[var(--accent-brass)] text-white font-serif text-sm font-bold border-2 border-white/50 shadow-md scale-[1.02]' 
              : 'bg-[var(--bg-surface-inset)] hover:bg-[var(--accent-brass-soft)] text-[var(--text-main)] hover:text-[var(--accent-brass)] border border-[var(--border-main)] hover:border-[var(--accent-brass)]',
            'w-full py-2.5 px-1 rounded-xl text-xs transition btn-interaction flex items-center justify-center gap-1.5 cursor-pointer select-none'
          ]"
          title="2e Choix (attribue 2 points)"
        >
          <span class="w-4 h-4 rounded-full bg-white/20 flex items-center justify-center text-[10px] font-sans font-bold">2</span>
          <span class="font-serif font-bold">2 pts</span>
          <Check v-if="currentRank === 2" class="w-3 h-3 stroke-[3]" />
        </button>

        <!-- Jeton 3 -->
        <button
          type="button"
          :disabled="disabled"
          @click="handleRankClick(3)"
          :class="[
            currentRank === 3 
              ? 'bg-[var(--accent-zinc)] text-white font-serif text-sm font-bold border-2 border-white/50 shadow-md scale-[1.02]' 
              : 'bg-[var(--bg-surface-inset)] hover:bg-[var(--accent-zinc-soft)] text-[var(--text-main)] hover:text-[var(--accent-zinc)] border border-[var(--border-main)] hover:border-[var(--accent-zinc)]',
            'w-full py-2.5 px-1 rounded-xl text-xs transition btn-interaction flex items-center justify-center gap-1.5 cursor-pointer select-none'
          ]"
          title="3e Choix (attribue 1 point)"
        >
          <span class="w-4 h-4 rounded-full bg-white/20 flex items-center justify-center text-[10px] font-sans font-bold">3</span>
          <span class="font-serif font-bold">1 pt</span>
          <Check v-if="currentRank === 3" class="w-3 h-3 stroke-[3]" />
        </button>
      </div>
    </div>
  </div>
</template>

