<script setup>
import { ref, computed, watch } from 'vue';
import { createSession } from '../api';
import { MapPin, Navigation, Utensils, ArrowRight, Loader2, AlertCircle, Footprints, Clock, Star } from 'lucide-vue-next';

const emit = defineEmits(['sessionCreated']);

const departureAddress = ref('');
const walkMinutes = ref(15);
const maxRestaurants = ref(30);
const selectedMinRating = ref(3.5); // slider 1 décimale de 3.5 à 5.0 (3.5 = Toutes les notes)
const selectedDietary = ref([]); // ['vegan', 'vegetarian', 'gluten_free', 'halal']

const WALKING_SPEED_M_PER_MIN = 100; // Allure dynamique ~6 km/h (100 m/min)
const radiusMeters = computed(() => Math.round(walkMinutes.value * WALKING_SPEED_M_PER_MIN));
const isLoading = ref(false);
const loadingStep = ref('');
const errorMessage = ref('');

// Efface l'erreur dès que l'utilisateur modifie l'adresse, la durée ou les filtres
watch([departureAddress, walkMinutes, maxRestaurants, selectedMinRating, selectedDietary], () => {
  if (errorMessage.value) errorMessage.value = '';
});

const durationPresets = [
  { minutes: 5, label: '5 min', meters: '~500 m' },
  { minutes: 10, label: '10 min', meters: '~1 km' },
  { minutes: 15, label: '15 min', meters: '~1,5 km' },
  { minutes: 20, label: '20 min', meters: '~2 km' },
  { minutes: 30, label: '30 min', meters: '~3 km' },
];

const dietaryOptions = [
  { id: 'vegan', label: 'Végan', icon: '🌱', desc: '100% végétal' },
  { id: 'vegetarian', label: 'Végétarien', icon: '🌿', desc: 'Sans viande/poisson' },
  { id: 'gluten_free', label: 'Sans gluten', icon: '🌾', desc: 'Plats sans gluten' },
  { id: 'halal', label: 'Halal', icon: '☪️', desc: 'Viandes certifiées' },
];

function toggleDietary(id) {
  const index = selectedDietary.value.indexOf(id);
  if (index >= 0) {
    selectedDietary.value.splice(index, 1);
  } else {
    selectedDietary.value.push(id);
  }
}

async function handleCreateSession() {
  const address = departureAddress.value.trim();
  if (!address) {
    errorMessage.value = "Veuillez renseigner une adresse ou un lieu de départ.";
    return;
  }

  isLoading.value = true;
  errorMessage.value = '';
  loadingStep.value = "Recherche des restaurants les plus proches et extraction des menus...";

  try {
    const options = {
      minRating: Number(selectedMinRating.value) > 3.5 ? Number(selectedMinRating.value) : null,
      dietaryPreferences: selectedDietary.value,
    };
    const session = await createSession(address, radiusMeters.value, maxRestaurants.value, options);
    emit('sessionCreated', session);
  } catch (err) {
    errorMessage.value = err.message || "Une erreur est survenue lors de la création de la session.";
  } finally {
    isLoading.value = false;
  }
}

</script>

<template>
  <div class="max-w-5xl mx-auto px-4 py-6 sm:py-10">
    <!-- En-tête Brasserie -->
    <div class="text-center mb-8 sm:mb-12">
      <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-[var(--border-ornament)] bg-[var(--bg-surface)] text-[var(--accent-brass)] text-sm uppercase tracking-wider font-serif font-bold shadow-xs mb-3.5">
        <span>🍽️</span>
        <span class="tracking-widest">Organisation du Déjeuner</span>
        <span>🍽️</span>
      </div>
      <h1 class="create-hero-title font-display sm:font-serif text-4xl sm:text-5xl lg:text-6xl font-normal tracking-wide text-[var(--text-main)] mb-3 leading-tight">
        Où déjeunons-nous ce midi ?
      </h1>
      <div class="flex items-center justify-center gap-3 text-[var(--accent-brass)] text-sm mb-2">
        <span>❧</span>
        <span class="font-serif italic text-base sm:text-lg">Trouvez où manger et votez avec vos collègues</span>
        <span>☙</span>
      </div>
      <p class="text-base sm:text-lg text-[var(--text-muted)] max-w-xl mx-auto leading-relaxed">
        Indiquez votre adresse de départ pour trouver les restaurants accessibles à pied, consulter leurs cartes et voter ensemble.
      </p>
    </div>

    <!-- Le Grand Registre / Livre d'Accueil Déployé (Cadre Brasserie Grand Format) -->
    <div class="bistro-grand-frame rounded-3xl p-6 sm:p-10 relative">
      <!-- Suspension à corde et anneaux en fonte (Ardoise) -->
      <div class="chalk-suspension-container">
        <div class="chalk-nail-top"></div>
        <div class="chalk-rope-left"></div>
        <div class="chalk-rope-right"></div>
        <div class="chalk-ring-left"></div>
        <div class="chalk-ring-right"></div>
      </div>

      <!-- 4 Coins en Laiton Vénérable -->
      <div class="brass-corner-bracket brass-corner-tl"></div>
      <div class="brass-corner-bracket brass-corner-tr"></div>
      <div class="brass-corner-bracket brass-corner-bl"></div>
      <div class="brass-corner-bracket brass-corner-br"></div>

      <!-- Rebord porte-craie en bois avec craies et effaceur (Ardoise) -->
      <div class="chalk-ledge-container">
        <div class="chalk-ledge-groove">
          <div class="flex items-center gap-2">
            <span class="chalk-stick chalk-stick-white" title="Craie blanche"></span>
            <span class="chalk-stick chalk-stick-yellow" title="Craie jaune bistrot"></span>
            <span class="chalk-stick chalk-stick-coral" title="Craie rouge"></span>
          </div>
          <div class="flex items-center gap-2">
            <span class="chalk-eraser" title="Effaceur de bistrot"></span>
          </div>
        </div>
      </div>

      <form @submit.prevent="handleCreateSession" class="relative z-10">
        <!-- Grille en 2 volets ouverts (Façon Livre d'Or de Brasserie) -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-10">
          
          <!-- Volet Gauche : Adresse & Périmètre de marche -->
          <div class="lg:col-span-7 space-y-6">
            <div class="flex items-center gap-2 border-b border-[var(--border-subtle)] pb-2 mb-1">
              <span class="font-serif text-sm font-bold text-[var(--accent-brass)] uppercase tracking-wider">Étape 1</span>
              <span class="text-[var(--text-faint)]">•</span>
              <h2 class="font-serif text-xl sm:text-2xl font-bold text-[var(--text-main)]">
                Point de départ & Distance
              </h2>
            </div>

            <!-- Champ Adresse de départ -->
            <div>
              <label for="address-input" class="block font-serif text-base font-semibold text-[var(--text-main)] mb-2 tracking-wide">
                📍 Adresse de départ ou lieu de rendez-vous
              </label>
              <div class="relative rounded-2xl">
                <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-4 text-[var(--text-faint)]">
                  <MapPin class="h-5 w-5 text-[var(--accent-red)]" />
                </div>
                <input
                  id="address-input"
                  v-model="departureAddress"
                  type="text"
                  required
                  :disabled="isLoading"
                  placeholder="ex : 12 rue de la Paix, Paris ou 31 allée Christine Pascal, Lyon"
                  class="block w-full rounded-2xl border border-[var(--border-main)] bg-[var(--bg-surface-inset)] pl-12 pr-4 py-3.5 text-[var(--text-main)] placeholder:text-[var(--text-faint)] focus:border-[var(--accent-brass)] focus:bg-[var(--bg-surface)] focus:ring-2 focus:ring-[var(--accent-brass)]/20 focus:outline-none text-base sm:text-lg transition font-normal"
                />
              </div>
              <p class="mt-2 text-sm text-[var(--text-muted)] font-serif">
                Tous les restaurants seront recherchés à pied autour de cette adresse.
              </p>
            </div>

            <!-- Réglette Périmètre de marche -->
            <div class="bg-[var(--bg-surface-subtle)] rounded-2xl p-5 sm:p-6 border border-[var(--border-subtle)] space-y-4">
              <div class="flex items-center justify-between gap-2">
                <label for="walk-slider" class="font-serif text-lg font-semibold text-[var(--text-main)] flex items-center gap-2">
                  <Footprints class="w-5 h-5 text-[var(--accent-red)]" />
                  <span>Temps de marche maximal</span>
                </label>
                <div class="inline-flex items-center gap-1.5 px-3.5 py-1 rounded-full bg-[var(--bg-surface)] border border-[var(--border-main)] text-[var(--text-main)] font-medium text-sm shadow-xs">
                  <Clock class="w-4 h-4 text-[var(--accent-brass)]" />
                  <span class="font-serif font-bold text-base text-[var(--accent-brass)]">{{ walkMinutes }} min</span>
                  <span class="text-sm text-[var(--text-muted)]">(~{{ radiusMeters >= 1000 ? (radiusMeters / 1000).toFixed(1).replace('.', ',') + ' km' : radiusMeters + ' m' }})</span>
                </div>
              </div>

              <div class="py-1">
                <input
                  id="walk-slider"
                  v-model.number="walkMinutes"
                  type="range"
                  min="3"
                  max="35"
                  step="1"
                  :disabled="isLoading"
                  class="slider-custom"
                />
              </div>

              <!-- Raccourcis cliquables sous le slider -->
              <div class="flex justify-between items-center text-sm gap-1">
                <button
                  v-for="preset in durationPresets"
                  :key="preset.minutes"
                  type="button"
                  :disabled="isLoading"
                  @click="walkMinutes = preset.minutes"
                  :class="[
                    walkMinutes === preset.minutes
                      ? 'text-white font-medium bg-[var(--accent-brass)] border border-[var(--accent-brass)] shadow-xs'
                      : 'text-[var(--text-muted)] hover:text-[var(--text-main)] hover:bg-[var(--bg-surface)]',
                    'cursor-pointer transition px-3 sm:px-3.5 py-1.5 rounded-xl flex items-center gap-1'
                  ]"
                >
                  <span class="font-serif font-bold text-sm sm:text-base">{{ preset.label }}</span>
                  <span class="text-xs opacity-80 hidden sm:inline">({{ preset.meters }})</span>
                </button>
              </div>

              <p class="text-sm text-[var(--text-muted)] pt-1 font-serif">
                Allure estimée à environ 6 km/h (100 mètres par minute).
              </p>
            </div>
          </div>

          <!-- Volet Droit : Nombre de restaurants & Validation -->
          <div class="lg:col-span-5 flex flex-col justify-between space-y-6 lg:border-l lg:border-[var(--border-subtle)] lg:pl-10">
            <div class="space-y-5">
              <div class="flex items-center gap-2 border-b border-[var(--border-subtle)] pb-2 mb-1">
                <span class="font-serif text-sm font-bold text-[var(--accent-brass)] uppercase tracking-wider">Étape 2</span>
                <span class="text-[var(--text-faint)]">•</span>
                <h2 class="font-serif text-xl sm:text-2xl font-bold text-[var(--text-main)]">
                  Options du vote
                </h2>
              </div>

              <!-- Nombre de restaurants -->
              <div class="space-y-2">
                <div class="flex items-center justify-between">
                  <label class="block font-serif text-base font-semibold text-[var(--text-main)]">
                    Nombre d'adresses à retenir
                  </label>
                  <span class="text-xs text-[var(--text-muted)] font-serif italic">
                    {{ maxRestaurants }} adresses
                  </span>
                </div>
                <div class="grid grid-cols-4 gap-2">
                  <button
                    v-for="opt in [
                      { count: 20, label: '20', desc: 'Rapide' },
                      { count: 30, label: '30', desc: 'Idéal' },
                      { count: 40, label: '40', desc: 'Élargi' },
                      { count: 50, label: '50', desc: 'Max' },
                    ]"
                    :key="opt.count"
                    type="button"
                    :disabled="isLoading"
                    @click="maxRestaurants = opt.count"
                    :class="[
                      maxRestaurants === opt.count
                        ? 'bg-[var(--accent-red)] border border-[var(--accent-red)] text-white font-medium shadow-sm'
                        : 'bg-[var(--bg-surface)] border border-[var(--border-main)] text-[var(--text-muted)] hover:border-[var(--accent-brass)] hover:text-[var(--text-main)]',
                      'cursor-pointer transition p-2.5 rounded-2xl text-center flex flex-col items-center justify-center'
                    ]"
                  >
                    <span class="font-serif text-base sm:text-lg font-bold">{{ opt.label }}</span>
                    <span 
                      :class="[
                        maxRestaurants === opt.count ? 'text-white/90 font-serif italic' : 'text-[var(--text-faint)] font-serif italic',
                        'text-xs mt-0.5'
                      ]"
                    >
                      {{ opt.desc }}
                    </span>
                  </button>
                </div>
              </div>

              <!-- Note minimale de départ (Slider 1 décimale) -->
              <div class="space-y-2.5 bg-[var(--bg-surface-inset)] p-4 rounded-2xl border border-[var(--border-subtle)]">
                <div class="flex items-center justify-between gap-2">
                  <label for="create-rating-slider" class="block font-serif text-base font-semibold text-[var(--text-main)] flex items-center gap-1.5">
                    <Star class="w-4 h-4 text-[var(--accent-brass)] fill-[var(--accent-brass)] shrink-0" />
                    <span>Note minimale de départ</span>
                  </label>
                  <div class="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-[var(--bg-surface)] border border-[var(--border-main)] text-sm shadow-xs">
                    <Star class="w-3.5 h-3.5 text-[var(--accent-brass)] fill-[var(--accent-brass)]" />
                    <span class="font-serif font-bold text-base text-[var(--accent-brass)]">
                      {{ selectedMinRating <= 3.5 ? 'Toutes (dès 3.5★)' : '≥ ' + Number(selectedMinRating).toFixed(1) + '★' }}
                    </span>
                  </div>
                </div>

                <div class="py-1">
                  <input
                    id="create-rating-slider"
                    v-model.number="selectedMinRating"
                    type="range"
                    min="3.5"
                    max="5.0"
                    step="0.1"
                    :disabled="isLoading"
                    class="slider-custom cursor-pointer"
                  />
                </div>

                <!-- Raccourcis cliquables sous le slider -->
                <div class="flex justify-between items-center text-xs font-serif text-[var(--text-muted)]">
                  <button
                    type="button"
                    :disabled="isLoading"
                    @click="selectedMinRating = 3.5"
                    :class="[selectedMinRating <= 3.5 ? 'text-[var(--accent-brass)] font-bold' : 'hover:text-[var(--text-main)]', 'cursor-pointer transition']"
                  >
                    3.5★ (Toutes)
                  </button>
                  <button
                    type="button"
                    :disabled="isLoading"
                    @click="selectedMinRating = 4.0"
                    :class="[selectedMinRating === 4.0 ? 'text-[var(--accent-brass)] font-bold' : 'hover:text-[var(--text-main)]', 'cursor-pointer transition']"
                  >
                    4.0★
                  </button>
                  <button
                    type="button"
                    :disabled="isLoading"
                    @click="selectedMinRating = 4.2"
                    :class="[selectedMinRating === 4.2 ? 'text-[var(--accent-brass)] font-bold' : 'hover:text-[var(--text-main)]', 'cursor-pointer transition']"
                  >
                    4.2★
                  </button>
                  <button
                    type="button"
                    :disabled="isLoading"
                    @click="selectedMinRating = 4.5"
                    :class="[selectedMinRating === 4.5 ? 'text-[var(--accent-brass)] font-bold' : 'hover:text-[var(--text-main)]', 'cursor-pointer transition']"
                  >
                    4.5★
                  </button>
                  <button
                    type="button"
                    :disabled="isLoading"
                    @click="selectedMinRating = 5.0"
                    :class="[selectedMinRating === 5.0 ? 'text-[var(--accent-brass)] font-bold' : 'hover:text-[var(--text-main)]', 'cursor-pointer transition']"
                  >
                    5.0★
                  </button>
                </div>

                <p class="text-xs text-[var(--text-muted)] font-serif">
                  Seuls les restaurants atteignant cette note seront sélectionnés au départ.
                </p>
              </div>

              <!-- Régimes alimentaires requis d'office -->
              <div class="space-y-2">
                <div class="flex items-center justify-between">
                  <label class="block font-serif text-base font-semibold text-[var(--text-main)]">
                    Régimes alimentaires pré-requis
                  </label>
                  <span v-if="selectedDietary.length > 0" class="text-xs text-[var(--accent-brass)] font-serif font-bold">
                    {{ selectedDietary.length }} actif{{ selectedDietary.length > 1 ? 's' : '' }}
                  </span>
                  <span v-else class="text-xs text-[var(--text-muted)] font-serif italic">
                    Optionnel
                  </span>
                </div>
                <div class="grid grid-cols-2 gap-2">
                  <button
                    v-for="diet in dietaryOptions"
                    :key="diet.id"
                    type="button"
                    :disabled="isLoading"
                    @click="toggleDietary(diet.id)"
                    :class="[
                      selectedDietary.includes(diet.id)
                        ? 'bg-[var(--accent-brass-soft)] border-2 border-[var(--accent-brass)] text-[var(--accent-brass)] font-bold shadow-xs'
                        : 'bg-[var(--bg-surface)] border border-[var(--border-main)] text-[var(--text-muted)] hover:border-[var(--accent-brass)] hover:text-[var(--text-main)]',
                      'cursor-pointer transition p-2.5 rounded-2xl text-left flex items-center justify-between gap-2'
                    ]"
                  >
                    <div class="flex items-center gap-2">
                      <span class="text-lg">{{ diet.icon }}</span>
                      <div>
                        <span class="font-serif text-sm font-bold block leading-tight">{{ diet.label }}</span>
                        <span class="text-[11px] text-[var(--text-faint)] font-serif italic block">{{ diet.desc }}</span>
                      </div>
                    </div>
                    <div 
                      :class="[
                        selectedDietary.includes(diet.id) ? 'bg-[var(--accent-brass)] text-white' : 'border border-[var(--border-main)]',
                        'w-4 h-4 rounded-full flex items-center justify-center shrink-0 text-[10px]'
                      ]"
                    >
                      <span v-if="selectedDietary.includes(diet.id)">✓</span>
                    </div>
                  </button>
                </div>
                <p class="text-xs text-[var(--text-muted)] font-serif">
                  Les adresses retenues intégreront ces régimes. Vous pourrez toujours filtrer lors du vote.
                </p>
              </div>

              <!-- Comment fonctionne le vote -->
              <div class="p-3.5 rounded-2xl bg-[var(--bg-surface-inset)] border border-[var(--border-subtle)] text-xs sm:text-sm text-[var(--text-muted)] space-y-1">
                <div class="flex items-center gap-1.5 text-[var(--accent-brass)] font-serif font-bold uppercase tracking-wider text-xs">
                  <span>💡</span>
                  <span>Principe du vote</span>
                </div>
                <p class="leading-relaxed font-serif">
                  Chaque personne choisit <strong>3 restaurants préférés</strong> (1er : 3 pts, 2e : 2 pts, 3e : 1 pt). Résultats en direct.
                </p>
              </div>

              <!-- Message d'erreur éventuel -->
              <div v-if="errorMessage" class="rounded-2xl bg-[var(--accent-red-soft)] border border-[var(--accent-red-border)] p-4 flex items-start gap-3 text-[var(--accent-red)] text-sm sm:text-base">
                <AlertCircle class="w-5 h-5 shrink-0 mt-0.5" />
                <div class="space-y-1">
                  <p class="font-medium">{{ errorMessage }}</p>
                  <p class="text-xs sm:text-sm opacity-90">Conseil : essayez d'augmenter le temps de marche avec le curseur ou de préciser la ville.</p>
                </div>
              </div>
            </div>

            <!-- Bouton de Création -->
            <div class="pt-2">
              <div class="flex items-center justify-between text-xs sm:text-sm text-[var(--accent-brass)] mb-1.5 px-1 font-serif italic opacity-90">
                <span class="tracking-wider">~ Service express ~</span>
                <span class="tracking-wider">❧ Prêt à voter ☙</span>
              </div>
              <button
                type="submit"
                :disabled="isLoading"
                class="wax-seal-btn w-full rounded-2xl px-6 py-4 text-lg sm:text-xl font-serif font-bold tracking-wide disabled:opacity-70 cursor-pointer flex items-center justify-center gap-3 shadow-xl"
              >
                <template v-if="isLoading">
                  <Loader2 class="w-5 h-5 animate-spin" />
                  <span class="font-sans text-base">{{ loadingStep }}</span>
                </template>
                <template v-else>
                  <span>Créer la session de vote</span>
                  <ArrowRight class="w-5 h-5" />
                </template>
              </button>
            </div>
          </div>
        </div>
      </form>
    </div>

    <!-- Les 3 étapes -->
    <div class="mt-14 grid grid-cols-1 sm:grid-cols-3 gap-6 text-center">
      <div class="bistro-card-frame chalk-tilt-1 p-6 rounded-2xl shadow-xs relative">
        <div class="chalk-step-pin"></div>
        <div class="text-3xl mb-2 select-none">💬</div>
        <span class="block font-serif text-base sm:text-lg font-bold text-[var(--accent-brass)] uppercase tracking-wider mb-2">1. Invitez vos collègues</span>
        <p class="text-sm sm:text-base text-[var(--text-muted)] font-serif leading-relaxed">Partagez simplement le lien de la session avec votre équipe ou vos amis.</p>
      </div>
      <div class="bistro-card-frame chalk-tilt-2 p-6 rounded-2xl shadow-xs relative">
        <div class="chalk-step-pin"></div>
        <div class="text-3xl mb-2 select-none">✍️ <span class="font-chalk text-xl tracking-widest text-[var(--chalk-yellow)]">卌 |</span></div>
        <span class="block font-serif text-base sm:text-lg font-bold text-[var(--accent-brass)] uppercase tracking-wider mb-2">2. Votez pour vos favoris</span>
        <p class="text-sm sm:text-base text-[var(--text-muted)] font-serif leading-relaxed">Consultez les menus et attribuez vos 3 choix (3, 2 et 1 pt) à la craie.</p>
      </div>
      <div class="bistro-card-frame chalk-tilt-3 p-6 rounded-2xl shadow-xs relative">
        <div class="chalk-step-pin"></div>
        <div class="text-3xl mb-2 select-none">🛎️</div>
        <span class="block font-serif text-base sm:text-lg font-bold text-[var(--accent-brass)] uppercase tracking-wider mb-2">3. Réservez la table</span>
        <p class="text-sm sm:text-base text-[var(--text-muted)] font-serif leading-relaxed">Visualisez le restaurant gagnant et le nombre exact de convives pour réserver.</p>
      </div>
    </div>
  </div>
</template>

