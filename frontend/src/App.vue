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
  <div class="min-h-screen flex flex-col font-sans selection:bg-[#DC2626] selection:text-white">
    <!-- Barre de navigation supérieure brasserie -->
    <header class="bg-[#F4EFEB]/95 backdrop-blur-md border-b border-[#E2D9CF] sticky top-0 z-30">
      <div class="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
        <!-- Logo -->
        <div 
          @click="resetToHome"
          class="flex items-center gap-2.5 cursor-pointer select-none group"
        >
          <div class="w-9 h-9 rounded-xl bg-[#191C22] border border-[#383F4C] text-[#D97706] flex items-center justify-center transition group-hover:border-[#D97706]/70 shadow-sm">
            <Utensils class="w-4 h-4" />
          </div>
          <div>
            <span class="font-serif text-2xl font-normal text-[#191C22] tracking-wide block leading-none">Meal Manager</span>
            <span class="text-[10px] text-[#64748B] block mt-0.5 font-medium tracking-widest uppercase font-sans">Bistrot & Ardoise du midi</span>
          </div>
        </div>

        <!-- Actions de navigation -->
        <div class="flex items-center gap-3">
          <button
            v-if="currentSession"
            @click="resetToHome"
            class="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl border border-[#E2D9CF] hover:border-[#191C22] text-xs font-medium text-[#191C22] bg-[#FFFFFF] hover:bg-[#F8F5F2] transition cursor-pointer shadow-xs"
          >
            <Plus class="w-3.5 h-3.5 text-[#DC2626]" />
            <span class="hidden sm:inline">Nouvelle ardoise</span>
          </button>
        </div>
      </div>
    </header>

    <!-- Contenu Principal -->
    <main class="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 py-8 sm:py-12">
      <!-- Chargement initial -->
      <div v-if="isLoading" class="text-center py-20">
        <Loader2 class="w-7 h-7 animate-spin text-[#DC2626] mx-auto mb-3" />
        <p class="text-xs tracking-wider uppercase text-[#64748B]">Mise en place de l'ardoise...</p>
      </div>

      <!-- Erreur de chargement de la session -->
      <div v-else-if="loadError" class="max-w-md mx-auto text-center py-16">
        <div class="w-12 h-12 rounded-full bg-[#FEF2F2] text-[#DC2626] mx-auto flex items-center justify-center mb-3 border border-[#FECACA]">
          <AlertCircle class="w-5 h-5" />
        </div>
        <h3 class="font-serif text-2xl font-normal text-[#191C22] mb-2">Ardoise introuvable</h3>
        <p class="text-sm text-[#64748B] mb-6">{{ loadError }}</p>
        <button
          @click="resetToHome"
          class="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-[#DC2626] text-white text-sm font-medium hover:bg-[#B91C1C] transition cursor-pointer shadow-sm"
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
          <div class="inline-flex p-1 rounded-xl bg-[#E7DED4] border border-[#D5CBC0] shadow-inner">
            <button
              type="button"
              @click="activeTab = 'vote'"
              :class="[
                activeTab === 'vote' ? 'bg-[#191C22] text-[#F8FAFC] font-medium border border-[#383F4C] shadow-sm' : 'text-[#64748B] hover:text-[#191C22]',
                'px-5 py-2 rounded-lg text-xs sm:text-sm transition cursor-pointer'
              ]"
            >
              Faire mon choix
            </button>
            <button
              type="button"
              @click="activeTab = 'results'"
              :class="[
                activeTab === 'results' ? 'bg-[#191C22] text-[#F8FAFC] font-medium border border-[#383F4C] shadow-sm' : 'text-[#64748B] hover:text-[#191C22]',
                'px-5 py-2 rounded-lg text-xs sm:text-sm transition cursor-pointer'
              ]"
            >
              Voir l'ardoise en direct
            </button>
          </div>
        </div>

        <!-- Message d'information si déjà voté (palette zinc/ardoise soignée) -->
        <div v-if="hasVoted" class="rounded-xl bg-[#191C22] border border-[#383F4C] p-4 text-[#F8FAFC] text-xs sm:text-sm flex items-center justify-between gap-3 shadow-sm">
          <span>
            Merci <strong>{{ currentVoterName }}</strong> • Votre commande a été transmise. L'ardoise ci-dessous s'actualise en temps réel.
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

    <!-- Pied de page bistrot épuré -->
    <footer class="mt-auto border-t border-[#E2D9CF] py-8 text-center text-xs text-[#64748B]">
      <div class="max-w-6xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
        <div>
          <span>Meal Manager • Données cartographiques © </span>
          <a href="https://www.openstreetmap.org" target="_blank" rel="noopener" class="underline hover:text-[#191C22]">OpenStreetMap</a>
        </div>
        <div class="tracking-wider uppercase text-[11px] font-medium">
          <span>Tradition de bistrot & vote pondéré (3, 2, 1 pts)</span>
        </div>
      </div>
    </footer>
  </div>
</template>

