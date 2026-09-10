<script setup>
import { ref } from 'vue';
import { createSession } from '../api';
import { MapPin, Navigation, Utensils, ArrowRight, Loader2, AlertCircle } from 'lucide-vue-next';

const emit = defineEmits(['sessionCreated']);

const departureAddress = ref('');
const radiusMeters = ref(800);
const isLoading = ref(false);
const loadingStep = ref('');
const errorMessage = ref('');

const radiusOptions = [
  { value: 500, label: '500 m', desc: '~6 min à pied' },
  { value: 800, label: '800 m', desc: '~10 min à pied' },
  { value: 1200, label: '1 200 m', desc: '~15 min à pied' },
];

async function handleCreateSession() {
  const address = departureAddress.value.trim();
  if (!address) {
    errorMessage.value = "Veuillez renseigner une adresse ou un lieu de départ.";
    return;
  }

  isLoading.value = true;
  errorMessage.value = '';
  loadingStep.value = "Recherche des restaurants et extraction des formules du midi...";

  try {
    const session = await createSession(address, radiusMeters.value);
    emit('sessionCreated', session);
  } catch (err) {
    errorMessage.value = err.message || "Une erreur est survenue lors de la création de la session.";
  } finally {
    isLoading.value = false;
  }
}
</script>

<template>
  <div class="max-w-2xl mx-auto px-4 py-8 sm:py-16">
    <div class="text-center mb-10">
      <div class="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-brand-50 text-brand-600 mb-5 ring-1 ring-brand-200/50">
        <Utensils class="w-7 h-7" />
      </div>
      <h1 class="text-3xl sm:text-4xl font-extrabold tracking-tight text-slate-900 mb-3">
        Où mangeons-nous ce midi ?
      </h1>
      <p class="text-base sm:text-lg text-slate-600 max-w-lg mx-auto leading-relaxed">
        Rassemblez vos collègues, découvrez les cartes et formules du jour autour du bureau, et votez en quelques secondes.
      </p>
    </div>

    <!-- Carte formulaire -->
    <div class="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 sm:p-8">
      <form @submit.prevent="handleCreateSession" class="space-y-6">
        <!-- Champ Adresse -->
        <div>
          <label for="address-input" class="block text-sm font-semibold text-slate-900 mb-2">
            Adresse de départ
          </label>
          <div class="relative rounded-xl shadow-xs">
            <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5 text-slate-400">
              <MapPin class="h-5 w-5" />
            </div>
            <input
              id="address-input"
              v-model="departureAddress"
              type="text"
              required
              :disabled="isLoading"
              placeholder="ex : 12 rue de la Paix, Paris ou Gare Part-Dieu, Lyon"
              class="block w-full rounded-xl border border-slate-300 pl-11 pr-4 py-3 text-slate-900 placeholder:text-slate-400 focus:border-brand-600 focus:ring-2 focus:ring-brand-500/20 focus:outline-none text-base transition sm:text-sm"
            />
          </div>
          <p class="mt-1.5 text-xs text-slate-500">
            Nous localisons les établissements accessibles à pied depuis ce point.
          </p>
        </div>

        <!-- Rayon de marche -->
        <div>
          <label class="block text-sm font-semibold text-slate-900 mb-2.5">
            Distance de marche maximale
          </label>
          <div class="grid grid-cols-3 gap-3">
            <button
              v-for="opt in radiusOptions"
              :key="opt.value"
              type="button"
              :disabled="isLoading"
              @click="radiusMeters = opt.value"
              :class="[
                radiusMeters === opt.value
                  ? 'border-brand-600 bg-brand-50/50 text-brand-900 ring-2 ring-brand-600/30 font-semibold'
                  : 'border-slate-200 hover:border-slate-300 bg-white text-slate-700',
                'p-3.5 text-center rounded-xl border transition btn-interaction flex flex-col items-center justify-center'
              ]"
            >
              <span class="text-sm font-bold">{{ opt.label }}</span>
              <span class="text-xs text-slate-500 mt-0.5">{{ opt.desc }}</span>
            </button>
          </div>
        </div>

        <!-- Message d'erreur éventuel -->
        <div v-if="errorMessage" class="rounded-xl bg-red-50 border border-red-200 p-4 flex items-start gap-3 text-red-800 text-sm">
          <AlertCircle class="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
          <span>{{ errorMessage }}</span>
        </div>

        <!-- Bouton d'action -->
        <button
          type="submit"
          :disabled="isLoading"
          class="w-full inline-flex items-center justify-center gap-2 rounded-xl bg-brand-600 px-6 py-3.5 text-base font-semibold text-white shadow-sm hover:bg-brand-700 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-600 disabled:opacity-75 transition btn-interaction cursor-pointer"
        >
          <template v-if="isLoading">
            <Loader2 class="w-5 h-5 animate-spin" />
            <span>{{ loadingStep }}</span>
          </template>
          <template v-else>
            <span>Créer la session de vote</span>
            <ArrowRight class="w-5 h-5" />
          </template>
        </button>
      </form>
    </div>

    <!-- Récapitulatif du fonctionnement -->
    <div class="mt-8 grid grid-cols-1 sm:grid-cols-3 gap-4 text-center">
      <div class="p-4 rounded-xl bg-slate-100/70 border border-slate-200/60">
        <span class="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">1. Partagez</span>
        <p class="text-xs text-slate-700">Envoyez le lien unique à votre équipe ou vos amis.</p>
      </div>
      <div class="p-4 rounded-xl bg-slate-100/70 border border-slate-200/60">
        <span class="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">2. Votez</span>
        <p class="text-xs text-slate-700">Classez vos 3 restaurants préférés (3, 2 et 1 point).</p>
      </div>
      <div class="p-4 rounded-xl bg-slate-100/70 border border-slate-200/60">
        <span class="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">3. Résultats</span>
        <p class="text-xs text-slate-700">Découvrez le gagnant en direct dès que vous avez voté.</p>
      </div>
    </div>
  </div>
</template>
