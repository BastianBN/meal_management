<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import CreateSession from './components/CreateSession.vue';
import VotingView from './components/VotingView.vue';
import ResultsView from './components/ResultsView.vue';
import { getSession, getLeaderboard, connectSessionWebSocket } from './api';
import { Utensils, Plus, Loader2, AlertCircle, ArrowLeft } from 'lucide-vue-next';

const currentSession = ref(null);
const leaderboard = ref(null);
const currentVoterName = ref('');
const hasVoted = ref(false);
const isLoading = ref(false);
const loadError = ref('');
const activeTab = ref('vote'); // 'vote' ou 'results'

let wsConnection = null;

// Détecte si un identifiant de session est passé dans l'URL (?session=XYZ ou #XYZ ou /session/XYZ)
function getSessionIdFromUrl() {
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.has('session')) {
    return urlParams.get('session');
  }
  const hash = window.location.hash.replace(/^#\/?(session\/)?/, '');
  if (hash && hash.length >= 6) {
    return hash;
  }
  const pathMatch = window.location.pathname.match(/\/session\/([a-zA-Z0-9_-]+)/);
  if (pathMatch) {
    return pathMatch[1];
  }
  return null;
}

function updateUrlWithSession(sessionId) {
  const newUrl = `${window.location.pathname}?session=${sessionId}`;
  window.history.pushState({ session: sessionId }, '', newUrl);
}

async function loadSession(sessionId) {
  isLoading.value = true;
  loadError.value = '';

  try {
    const sessionData = await getSession(sessionId);
    currentSession.value = sessionData;

    // Vérifier si ce navigateur a déjà voté
    const storedVoter = localStorage.getItem(`meal_voter_${sessionId}`);
    if (storedVoter) {
      currentVoterName.value = storedVoter;
      hasVoted.value = true;
      activeTab.value = 'results';
    } else {
      hasVoted.value = false;
      activeTab.value = 'vote';
    }

    // Récupérer le classement actuel
    const lb = await getLeaderboard(sessionId);
    leaderboard.value = lb;

    // Établir la connexion WebSocket pour les mises à jour en direct
    setupWebSocket(sessionId);
  } catch (err) {
    loadError.value = err.message || "Impossible de charger la session.";
  } finally {
    isLoading.value = false;
  }
}

function setupWebSocket(sessionId) {
  if (wsConnection) {
    wsConnection.close();
  }

  wsConnection = connectSessionWebSocket(
    sessionId,
    (msg) => {
      if (msg.type === 'INITIAL_STATE' || msg.type === 'NEW_VOTE') {
        if (msg.leaderboard) {
          leaderboard.value = msg.leaderboard;
        }
      }
    },
    (err) => {
      console.warn("Connexion WebSocket interrompue :", err);
    }
  );
}

function handleSessionCreated(session) {
  currentSession.value = session;
  hasVoted.value = false;
  activeTab.value = 'vote';
  updateUrlWithSession(session.id);
  setupWebSocket(session.id);
}

function handleVoteSubmitted({ leaderboard: newLeaderboard, voterName }) {
  leaderboard.value = newLeaderboard;
  currentVoterName.value = voterName;
  hasVoted.value = true;
  activeTab.value = 'results';
}

function resetToHome() {
  if (wsConnection) {
    wsConnection.close();
    wsConnection = null;
  }
  currentSession.value = null;
  leaderboard.value = null;
  hasVoted.value = false;
  const newUrl = window.location.pathname;
  window.history.pushState({}, '', newUrl);
}

onMounted(() => {
  const sessionId = getSessionIdFromUrl();
  if (sessionId) {
    loadSession(sessionId);
  }

  window.addEventListener('popstate', () => {
    const sId = getSessionIdFromUrl();
    if (sId) {
      loadSession(sId);
    } else {
      currentSession.value = null;
    }
  });
});

onUnmounted(() => {
  if (wsConnection) {
    wsConnection.close();
  }
});
</script>

<template>
  <div class="min-h-full flex flex-col font-sans selection:bg-[#B85B43] selection:text-white">
    <!-- Barre de navigation supérieure -->
    <header class="bg-[#F7F4EE]/90 backdrop-blur-md border-b border-[#E8E3DA] sticky top-0 z-30">
      <div class="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
        <!-- Logo -->
        <div 
          @click="resetToHome"
          class="flex items-center gap-2.5 cursor-pointer select-none group"
        >
          <div class="w-9 h-9 rounded-xl bg-[#FFFDF9] border border-[#E8E3DA] text-[#B85B43] flex items-center justify-center transition group-hover:border-[#B85B43]/50">
            <Utensils class="w-4 h-4" />
          </div>
          <div>
            <span class="font-serif text-lg font-semibold text-[#292524] tracking-wide block leading-tight">Meal Manager</span>
            <span class="text-[11px] text-[#78716C] block -mt-0.5 font-normal tracking-wider uppercase">Déjeuner & Vote zen</span>
          </div>
        </div>

        <!-- Actions de navigation -->
        <div class="flex items-center gap-3">
          <button
            v-if="currentSession"
            @click="resetToHome"
            class="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl border border-[#E8E3DA] hover:border-[#292524] text-xs font-medium text-[#292524] bg-[#FFFDF9] hover:bg-[#F3EFEA] transition cursor-pointer"
          >
            <Plus class="w-3.5 h-3.5 text-[#B85B43]" />
            <span class="hidden sm:inline">Nouvelle session</span>
          </button>
        </div>
      </div>
    </header>

    <!-- Contenu Principal -->
    <main class="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 py-8 sm:py-12">
      <!-- Chargement initial -->
      <div v-if="isLoading" class="text-center py-20">
        <Loader2 class="w-7 h-7 animate-spin text-[#B85B43] mx-auto mb-3" />
        <p class="text-xs tracking-wider uppercase text-[#78716C]">Chargement de la session...</p>
      </div>

      <!-- Erreur de chargement de la session -->
      <div v-else-if="loadError" class="max-w-md mx-auto text-center py-16">
        <div class="w-12 h-12 rounded-full bg-[#FBF4F1] text-[#B85B43] mx-auto flex items-center justify-center mb-3 border border-[#E8C7BE]">
          <AlertCircle class="w-5 h-5" />
        </div>
        <h3 class="font-serif text-xl font-semibold text-[#292524] mb-2">Session introuvable</h3>
        <p class="text-sm text-[#78716C] mb-6">{{ loadError }}</p>
        <button
          @click="resetToHome"
          class="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-[#B85B43] text-white text-sm font-medium hover:bg-[#9E4C36] transition cursor-pointer"
        >
          <ArrowLeft class="w-4 h-4" />
          <span>Créer une nouvelle session</span>
        </button>
      </div>

      <!-- Écran 1 : Formulaire de création de session -->
      <CreateSession
        v-else-if="!currentSession"
        @session-created="handleSessionCreated"
      />

      <!-- Écran 2 : Session active (Vote & Résultats) -->
      <div v-else class="space-y-8">
        <!-- Onglets Vote / Résultats si l'utilisateur n'a pas encore voté -->
        <div v-if="!hasVoted" class="flex items-center justify-center">
          <div class="inline-flex p-1 rounded-xl bg-[#EFEBE3] border border-[#E8E3DA]">
            <button
              type="button"
              @click="activeTab = 'vote'"
              :class="[
                activeTab === 'vote' ? 'bg-[#FFFDF9] text-[#292524] font-medium border border-[#E8E3DA]' : 'text-[#78716C] hover:text-[#292524]',
                'px-5 py-2 rounded-lg text-xs sm:text-sm transition cursor-pointer'
              ]"
            >
              Voter pour mon midi
            </button>
            <button
              type="button"
              @click="activeTab = 'results'"
              :class="[
                activeTab === 'results' ? 'bg-[#FFFDF9] text-[#292524] font-medium border border-[#E8E3DA]' : 'text-[#78716C] hover:text-[#292524]',
                'px-5 py-2 rounded-lg text-xs sm:text-sm transition cursor-pointer'
              ]"
            >
              Voir le classement en direct
            </button>
          </div>
        </div>

        <!-- Message d'information si déjà voté (palette matcha zen) -->
        <div v-if="hasVoted" class="rounded-xl bg-[#F3F6F2] border border-[#CBD8C8] p-4 text-[#3E503B] text-xs sm:text-sm flex items-center justify-between gap-3">
          <span>
            Merci <strong>{{ currentVoterName }}</strong> • Votre vote a été enregistré. Le classement ci-dessous s'actualise en temps réel.
          </span>
        </div>

        <!-- Vue de Vote (active si non voté et onglet vote) -->
        <VotingView
          v-if="!hasVoted && activeTab === 'vote'"
          :session="currentSession"
          @vote-submitted="handleVoteSubmitted"
        />

        <!-- Vue des Résultats en direct -->
        <ResultsView
          v-else-if="leaderboard"
          :leaderboard="leaderboard"
          :session="currentSession"
          :current-voter-name="currentVoterName"
        />
      </div>
    </main>

    <!-- Pied de page discret et soigné -->
    <footer class="mt-auto border-t border-[#E8E3DA] py-8 text-center text-xs text-[#78716C]">
      <div class="max-w-6xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
        <div>
          <span>Meal Manager • Données cartographiques © </span>
          <a href="https://www.openstreetmap.org" target="_blank" rel="noopener" class="underline hover:text-[#292524]">OpenStreetMap</a>
        </div>
        <div class="tracking-wider uppercase text-[11px]">
          <span>Vote préférentiel harmonieux (3, 2, 1 pts)</span>
        </div>
      </div>
    </footer>
  </div>
</template>

