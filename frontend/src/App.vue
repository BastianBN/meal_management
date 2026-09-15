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

const currentTheme = ref('carte');

function applyTheme(theme) {
  currentTheme.value = theme;
  try {
    localStorage.setItem('bistro_theme', theme);
  } catch (e) {
    // Ignore if localStorage unavailable
  }
  if (typeof document !== 'undefined') {
    document.documentElement.classList.remove('theme-carte', 'theme-ardoise');
    document.documentElement.classList.add(`theme-${theme}`);
  }
}

onMounted(() => {
  const savedTheme = localStorage.getItem('bistro_theme') || 'carte';
  applyTheme(savedTheme);

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
  <div class="min-h-screen flex flex-col font-sans transition-colors duration-300">
    <!-- Barre de navigation supérieure brasserie & Interrupteur de Service -->
    <header class="bg-[var(--header-bg)] backdrop-blur-md border-b border-[var(--border-main)] sticky top-0 z-30 transition-colors duration-300">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 h-18 flex items-center justify-between">
        <!-- Logo Brasserie -->
        <div 
          @click="resetToHome"
          class="flex items-center gap-3 cursor-pointer select-none group"
        >
          <div class="w-10 h-10 rounded-xl bg-[var(--bg-surface)] border-2 border-[var(--accent-brass)] text-[var(--accent-brass)] flex items-center justify-center transition group-hover:scale-105 shadow-sm">
            <Utensils class="w-5 h-5" />
          </div>
          <div>
            <span class="font-serif text-2xl sm:text-3xl font-normal text-[var(--text-main)] tracking-wide block leading-none">
              Meal Manager
            </span>
            <span class="text-[10px] text-[var(--text-faint)] block mt-1 font-medium tracking-widest uppercase font-sans">
              {{ currentTheme === 'carte' ? 'La Grande Carte de Brasserie' : 'L’Ardoise du Bouchon Lyonnais' }}
            </span>
          </div>
        </div>

        <!-- Actions de navigation : Interrupteur de Service & Nouvelle Ardoise -->
        <div class="flex items-center gap-3">
          <!-- Interrupteur de Thème Jour / Soir -->
          <div class="flex items-center p-1 rounded-xl bg-[var(--bg-surface-inset)] border border-[var(--border-main)] shadow-inner">
            <button
              type="button"
              @click="applyTheme('carte')"
              :title="'Service de Jour : Carte de Brasserie'"
              :class="[
                currentTheme === 'carte'
                  ? 'bg-[var(--bg-surface)] text-[var(--text-main)] shadow-xs border border-[var(--border-main)] font-semibold'
                  : 'text-[var(--text-faint)] hover:text-[var(--text-main)]',
                'px-3 py-1.5 rounded-lg text-xs flex items-center gap-1.5 transition cursor-pointer'
              ]"
            >
              <span>☀️</span>
              <span class="hidden md:inline font-serif text-base">La Carte</span>
            </button>
            <button
              type="button"
              @click="applyTheme('ardoise')"
              :title="'Service du Soir : L’Ardoise de Bistrot'"
              :class="[
                currentTheme === 'ardoise'
                  ? 'bg-[var(--bg-surface)] text-[var(--text-main)] shadow-xs border border-[var(--border-main)] font-semibold'
                  : 'text-[var(--text-faint)] hover:text-[var(--text-main)]',
                'px-3.5 py-1.5 rounded-lg text-sm flex items-center gap-1.5 transition cursor-pointer'
              ]"
            >
              <span>🌙</span>
              <span class="hidden md:inline font-serif text-base">L'Ardoise</span>
            </button>
          </div>

          <button
            v-if="currentSession"
            @click="resetToHome"
            class="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl border border-[var(--border-main)] hover:border-[var(--accent-red)] text-sm font-medium text-[var(--text-main)] bg-[var(--bg-surface)] hover:bg-[var(--bg-surface-subtle)] transition cursor-pointer shadow-xs"
          >
            <Plus class="w-4 h-4 text-[var(--accent-red)]" />
            <span class="hidden sm:inline font-serif text-base">Nouveau vote</span>
          </button>
        </div>
      </div>
    </header>

    <!-- Contenu Principal -->
    <main class="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-8 sm:py-12">
      <!-- Chargement initial -->
      <div v-if="isLoading" class="text-center py-20">
        <Loader2 class="w-8 h-8 animate-spin text-[var(--accent-red)] mx-auto mb-3" />
        <p class="text-sm tracking-wider uppercase text-[var(--text-faint)] font-serif text-base sm:text-lg">Chargement de la session...</p>
      </div>

      <!-- Erreur de chargement de la session -->
      <div v-else-if="loadError" class="max-w-md mx-auto text-center py-16">
        <div class="w-12 h-12 rounded-full bg-[var(--accent-red-soft)] text-[var(--accent-red)] mx-auto flex items-center justify-center mb-3 border border-[var(--accent-red-border)]">
          <AlertCircle class="w-5 h-5" />
        </div>
        <h3 class="font-serif text-2xl sm:text-3xl font-normal text-[var(--text-main)] mb-2">Session introuvable</h3>
        <p class="text-sm sm:text-base text-[var(--text-muted)] mb-6">{{ loadError }}</p>
        <button
          @click="resetToHome"
          class="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[var(--accent-red)] text-white text-base font-medium hover:bg-[var(--accent-red-hover)] transition cursor-pointer shadow-sm"
        >
          <ArrowLeft class="w-4 h-4" />
          <span>Créer un nouveau vote</span>
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
          <div class="inline-flex p-1.5 rounded-2xl bg-[var(--bg-surface-inset)] border border-[var(--border-main)] shadow-inner">
            <button
              type="button"
              @click="activeTab = 'vote'"
              :class="[
                activeTab === 'vote'
                  ? 'bg-[var(--bg-surface)] text-[var(--text-main)] font-semibold border border-[var(--border-main)] shadow-md'
                  : 'text-[var(--text-faint)] hover:text-[var(--text-main)]',
                'px-6 py-2.5 rounded-xl text-sm sm:text-base font-serif transition cursor-pointer tracking-wide'
              ]"
            >
              🍽️ Découvrir & Voter
            </button>
            <button
              type="button"
              @click="activeTab = 'results'"
              :class="[
                activeTab === 'results'
                  ? 'bg-[var(--bg-surface)] text-[var(--text-main)] font-semibold border border-[var(--border-main)] shadow-md'
                  : 'text-[var(--text-faint)] hover:text-[var(--text-main)]',
                'px-6 py-2.5 rounded-xl text-sm sm:text-base font-serif transition cursor-pointer tracking-wide'
              ]"
            >
              🏆 Résultats des votes
            </button>
          </div>
        </div>

        <!-- Message d'information si déjà voté -->
        <div v-if="hasVoted" class="bistro-card-frame rounded-2xl p-4 sm:p-5 text-[var(--text-main)] text-sm sm:text-base flex items-center justify-between gap-3 shadow-md">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-full bg-[var(--accent-red-soft)] text-[var(--accent-red)] flex items-center justify-center shrink-0 border border-[var(--accent-red-border)]">
              ✓
            </div>
            <span>
              Merci <strong class="text-[var(--accent-brass)]">{{ currentVoterName }}</strong> • Votre vote a été enregistré. Les résultats ci-dessous s'actualisent en direct.
            </span>
          </div>
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

    <!-- Pied de page brasserie & tradition gastronomique -->
    <footer class="mt-auto border-t border-[var(--border-main)] py-8 text-center text-sm text-[var(--text-faint)] bg-[var(--bg-surface-subtle)]/60">
      <div class="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
        <div class="flex items-center gap-2">
          <span class="font-serif text-base text-[var(--text-main)]">Meal Manager</span>
          <span>• Données cartographiques © </span>
          <a href="https://www.openstreetmap.org" target="_blank" rel="noopener" class="underline hover:text-[var(--accent-red)]">OpenStreetMap</a>
        </div>
        <div class="tracking-wider uppercase text-xs sm:text-sm font-medium text-[var(--text-muted)] flex items-center gap-2">
          <span>❧</span>
          <span>Système de vote pondéré : 1er (3 pts) • 2e (2 pts) • 3e (1 pt)</span>
          <span>☙</span>
        </div>
      </div>
    </footer>
  </div>
</template>

