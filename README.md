# 🍽️ Meal Manager • Choix & Vote de Restaurant pour le Midi

Application web collaborative conçue pour les équipes et groupes d'amis souhaitant décider rapidement et équitablement d'un restaurant pour la pause déjeuner.

---

## 🌟 Fonctionnalités Clés

1. **Recherche de proximité (OpenStreetMap)** :
   - Indiquez votre adresse de départ (bureau, gare, place...).
   - Géocodage précis avec Nominatim et découverte des restaurants accessibles à pied via l'Overpass API.
   - Calcul de la distance réelle de marche et du temps de trajet estimé (à ~4.8 km/h).
2. **Découverte et scraping intelligent des menus** :
   - Détection automatique du site officiel du restaurant (tags OSM ou recherche de secours DuckDuckGo).
   - Analyse de la page carte/menu pour extraire les **formules du midi**, **plats du jour** et **tarifs en euros**.
   - Liens directs vers la carte officielle.
3. **Système de vote préférentiel par classement (Ranked Choice)** :
   - Chaque participant indique son nom et classe ses 3 établissements favoris :
     - 🥇 **1er choix** : **3 points**
     - 🥈 **2e choix** : **2 points**
     - 🥉 **3e choix** : **1 point**
   - **Règle d'or** : Le vote est **définitif** dès sa validation afin d'éviter les hésitations sans fin.
4. **Classement en direct via WebSockets** :
   - Dès qu'un collègue vote, les scores sont recalculés et diffusés instantanément à tous les participants connectés sans recharger la page.
5. **CI/CD & Déploiement automatisé** :
   - Versionnement automatique avec **Semantic Release** et Conventional Commits (`feat:`, `fix:`).
   - Déploiement continu du frontend Vue 3 sur **GitHub Pages**.
   - `Dockerfile` multi-stage pour héberger la stack complète.

---

## 🛠️ Stack Technique

- **Environnement** : Python 3.13 géré par [`mise`](https://mise.jdx.dev/) et [`uv`](https://docs.astral.sh/uv/).
- **Backend** : FastAPI, SQLAlchemy asynchrone, SQLite (aiosqlite), HTTPX, BeautifulSoup4, WebSockets.
- **Frontend** : Vue 3 (Composition API `<script setup>`), Vite, Tailwind CSS v4, Lucide Icons.
- **Interface** : 100% en français, sobre, responsive et moderne.

---

## 🚀 Démarrage Rapide

### Prérequis

- **Python 3.13** (installable avec `mise use python@3.13` ou `uv python install 3.13`)
- **Node.js 20+** et npm

### Installation des dépendances

```bash
# 1. Backend (avec uv)
uv venv --python 3.13
uv pip install -e ".[dev]"

# 2. Frontend
cd frontend
npm install
cd ..
```

### Lancement

#### Mode Simple (Production locale sur http://127.0.0.1:8000)
```bash
uv run python run.py
```

#### Mode Développement (Hot-reload complet)
```bash
uv run python run.py --dev
```
- Backend API : [http://127.0.0.1:8000](http://127.0.0.1:8000) (Documentation interactive sur `/docs`)
- Frontend Vite : [http://127.0.0.1:5173](http://127.0.0.1:5173)

---

## 🧪 Tests Unitaires

Exécutez la suite de tests automatisés couvrant le calcul des points préférentiels, les règles de vote et l'extraction de formules de menu :

```bash
uv run pytest
```

---

## 📦 CI/CD & Déploiement

### Déploiement GitHub Pages (Frontend)
Le workflow [`.github/workflows/deploy-pages.yml`](.github/workflows/deploy-pages.yml) compile et publie automatiquement le frontend Vue.js sur GitHub Pages à chaque push sur la branche `main`.

Pour relier le frontend GitHub Pages à un backend déployé en ligne (ex: Render, Fly.io, VPS), définissez la variable `BACKEND_API_URL` dans les variables GitHub de votre dépôt (`Settings > Secrets and variables > Actions > Variables`).

### Semantic Release
À chaque commit conventionnel fusionné sur `main` :
- `feat: ...` -> Incrémentation mineure (v1.1.0)
- `fix: ...` -> Incrémentation de correctif (v1.0.1)
- `feat!: ...` -> Incrémentation majeure (v2.0.0)

Le workflow [`.github/workflows/release.yml`](.github/workflows/release.yml) met à jour automatiquement le `CHANGELOG.md` et crée une nouvelle release GitHub avec tag.

### Déploiement Docker (Stack complète)
```bash
docker build -t meal-manager .
docker run -p 8000:8000 meal-manager
```
L'application est alors accessible sur `http://localhost:8000`.
