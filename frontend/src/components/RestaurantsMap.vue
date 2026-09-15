<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue';
import L from 'leaflet';

const props = defineProps({
  departure: {
    type: Object,
    required: true, // { address, latitude, longitude, radius_meters }
  },
  restaurants: {
    type: Array,
    required: true,
  },
  selectedRankings: {
    type: Object,
    default: () => ({ firstChoiceId: null, secondChoiceId: null, thirdChoiceId: null }),
  },
});

const emit = defineEmits(['toggleRank', 'selectRestaurant']);

const mapContainer = ref(null);
let map = null;
let markersLayer = null;
let radiusCircle = null;

function getRank(restaurantId) {
  if (props.selectedRankings.firstChoiceId === restaurantId) return 1;
  if (props.selectedRankings.secondChoiceId === restaurantId) return 2;
  if (props.selectedRankings.thirdChoiceId === restaurantId) return 3;
  return null;
}

function createDepartureIcon() {
  return L.divIcon({
    className: 'custom-departure-pin',
    html: `
      <div style="position: relative; display: flex; align-items: center; justify-content: center; width: 36px; height: 36px;">
        <span style="position: absolute; width: 36px; height: 36px; border-radius: 50%; background: #3b82f6; opacity: 0.35; animation: ping 2s cubic-bezier(0, 0, 0.2, 1) infinite;"></span>
        <div style="width: 28px; height: 28px; border-radius: 50%; background: #2563eb; border: 3px solid white; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.2); display: flex; align-items: center; justify-content: center; color: white; font-size: 14px; font-weight: bold;">
          📍
        </div>
      </div>
    `,
    iconSize: [36, 36],
    iconAnchor: [18, 18],
  });
}

function createRestaurantIcon(restaurant, rank) {
  const isCarte = typeof document !== 'undefined' && document.documentElement.classList.contains('theme-carte');
  
  let bgColor = isCarte ? '#2A1F18' : '#181C24';
  let badgeText = `${restaurant.walking_time_min}m`;
  let ringColor = isCarte ? 'rgba(70, 45, 20, 0.35)' : 'rgba(0, 0, 0, 0.7)';
  let borderColor = isCarte ? '#C5A880' : '#475569';
  let scale = '1';

  if (rank === 1) {
    bgColor = isCarte ? '#8B1515' : '#DC2626';
    badgeText = '1er';
    ringColor = isCarte ? 'rgba(139, 21, 21, 0.5)' : 'rgba(220, 38, 38, 0.6)';
    borderColor = '#FFFFFF';
    scale = '1.15';
  } else if (rank === 2) {
    bgColor = isCarte ? '#B45309' : '#D97706';
    badgeText = '2e';
    ringColor = isCarte ? 'rgba(180, 83, 9, 0.5)' : 'rgba(217, 119, 6, 0.6)';
    borderColor = '#FFFFFF';
    scale = '1.1';
  } else if (rank === 3) {
    bgColor = isCarte ? '#475569' : '#64748B';
    badgeText = '3e';
    ringColor = isCarte ? 'rgba(71, 85, 105, 0.5)' : 'rgba(100, 116, 139, 0.6)';
    borderColor = '#FFFFFF';
    scale = '1.05';
  }

  return L.divIcon({
    className: 'custom-restaurant-pin',
    html: `
      <div style="transform: scale(${scale}); transform-origin: bottom center; transition: all 0.2s ease;">
        <div style="background: ${bgColor}; color: white; padding: 4px 9px; border-radius: 9999px; font-size: 11px; font-weight: 700; border: 2px solid ${borderColor}; box-shadow: 0 4px 12px ${ringColor}; display: flex; align-items: center; gap: 4px; white-space: nowrap; cursor: pointer; font-family: inherit;">
          <span>🍽️</span>
          <span>${badgeText}</span>
        </div>
        <div style="width: 0; height: 0; border-left: 5px solid transparent; border-right: 5px solid transparent; border-top: 6px solid ${bgColor}; margin: 0 auto; margin-top: -1px;"></div>
      </div>
    `,
    iconSize: [46, 34],
    iconAnchor: [23, 34],
    popupAnchor: [0, -34],
  });
}

function buildPopupHtml(r) {
  const isCarte = typeof document !== 'undefined' && document.documentElement.classList.contains('theme-carte');
  const currentRank = getRank(r.id);

  const cardBg = isCarte ? '#FFFDF9' : '#181C24';
  const textMain = isCarte ? '#1F1A15' : '#F8FAFC';
  const textMuted = isCarte ? '#6B5747' : '#CBD5E1';
  const borderCol = isCarte ? '#DBCFBE' : '#363E4D';
  const accentBrass = isCarte ? '#B45309' : '#D97706';
  const btnInactiveBg = isCarte ? '#F2ECE1' : '#202530';
  const btnInactiveText = isCarte ? '#1F1A15' : '#CBD5E1';

  const siteBtn = r.website_url 
    ? `<a href="${r.website_url}" target="_blank" rel="noopener" style="display: inline-block; font-size: 11px; color: ${accentBrass}; font-weight: 600; text-decoration: underline; margin-right: 8px;">Site officiel</a>`
    : '';
  const gmapsBtn = r.google_maps_url
    ? `<a href="${r.google_maps_url}" target="_blank" rel="noopener" style="display: inline-block; font-size: 11px; color: ${textMuted}; font-weight: 500; text-decoration: underline;">Fiche Google & Avis</a>`
    : '';

  return `
    <div style="padding: 14px; min-width: 250px; max-width: 320px; font-family: inherit; background: ${cardBg}; color: ${textMain}; border-radius: 14px; border: 1px solid ${borderCol}; box-shadow: 0 10px 30px rgba(0,0,0,0.35);">
      <div style="font-size: 10px; font-weight: 700; color: ${accentBrass}; text-transform: uppercase; margin-bottom: 3px; letter-spacing: 0.5px;">
        ${r.cuisine || 'Restaurant'} • ${r.distance_meters} m (~${r.walking_time_min} min)
      </div>
      <div style="font-size: 18px; font-family: 'Cormorant Garamond', Georgia, serif; font-weight: 700; color: ${textMain}; margin-bottom: 6px; line-height: 1.2;">
        ${r.name}
      </div>
      ${r.menu_summary ? `<div style="font-size: 11px; color: ${textMuted}; margin-bottom: 8px; line-height: 1.35;">${r.menu_summary}</div>` : ''}
      <div style="margin-bottom: 10px;">
        ${siteBtn}
        ${gmapsBtn}
      </div>
      <div style="border-top: 1px solid ${borderCol}; padding-top: 10px; display: flex; gap: 4px;">
        <button onclick="window.__vote_restaurant(${r.id}, 1)" style="flex: 1; padding: 7px 4px; font-size: 11px; font-weight: 700; font-family: inherit; border-radius: 8px; border: 1px solid ${currentRank === 1 ? '#8B1515' : borderCol}; background: ${currentRank === 1 ? '#8B1515' : btnInactiveBg}; color: ${currentRank === 1 ? '#ffffff' : btnInactiveText}; cursor: pointer; transition: all 0.15s;">
          1er (3 pts)
        </button>
        <button onclick="window.__vote_restaurant(${r.id}, 2)" style="flex: 1; padding: 7px 4px; font-size: 11px; font-weight: 700; font-family: inherit; border-radius: 8px; border: 1px solid ${currentRank === 2 ? '#B45309' : borderCol}; background: ${currentRank === 2 ? '#B45309' : btnInactiveBg}; color: ${currentRank === 2 ? '#ffffff' : btnInactiveText}; cursor: pointer; transition: all 0.15s;">
          2e (2 pts)
        </button>
        <button onclick="window.__vote_restaurant(${r.id}, 3)" style="flex: 1; padding: 7px 4px; font-size: 11px; font-weight: 700; font-family: inherit; border-radius: 8px; border: 1px solid ${currentRank === 3 ? '#475569' : borderCol}; background: ${currentRank === 3 ? '#475569' : btnInactiveBg}; color: ${currentRank === 3 ? '#ffffff' : btnInactiveText}; cursor: pointer; transition: all 0.15s;">
          3e (1 pt)
        </button>
      </div>
    </div>
  `;
}

function updateMarkers() {
  if (!map || !markersLayer) return;

  markersLayer.clearLayers();

  // 1. Point de départ
  if (props.departure?.latitude && props.departure?.longitude) {
    const depMarker = L.marker([props.departure.latitude, props.departure.longitude], {
      icon: createDepartureIcon(),
      title: "Lieu de départ : " + props.departure.address,
    });
    depMarker.bindPopup(`
      <div style="padding: 12px; font-family: inherit;">
        <div style="font-size: 10px; font-weight: 700; color: #2563eb; text-transform: uppercase;">Lieu de départ</div>
        <div style="font-size: 13px; font-weight: 700; color: #0f172a; margin-top: 2px;">${props.departure.address}</div>
        <div style="font-size: 11px; color: #64748b; margin-top: 4px;">Rayon de marche : ${props.departure.radius_meters} m</div>
      </div>
    `);
    markersLayer.addLayer(depMarker);

    // Cercle du rayon de marche
    if (radiusCircle) {
      map.removeLayer(radiusCircle);
    }
    radiusCircle = L.circle([props.departure.latitude, props.departure.longitude], {
      radius: props.departure.radius_meters,
      color: '#B45309',
      weight: 1.5,
      opacity: 0.6,
      fillColor: '#B45309',
      fillOpacity: 0.05,
      dashArray: '6, 6',
    }).addTo(map);
  }

  // 2. Restaurants
  const latLngs = [];
  if (props.departure?.latitude && props.departure?.longitude) {
    latLngs.push([props.departure.latitude, props.departure.longitude]);
  }

  props.restaurants.forEach(r => {
    if (r.latitude && r.longitude) {
      const rank = getRank(r.id);
      const marker = L.marker([r.latitude, r.longitude], {
        icon: createRestaurantIcon(r, rank),
        title: r.name,
      });

      marker.bindPopup(buildPopupHtml(r));
      markersLayer.addLayer(marker);
      latLngs.push([r.latitude, r.longitude]);
    }
  });

  // Ajuster le zoom pour tout afficher
  if (latLngs.length > 1) {
    map.fitBounds(L.latLngBounds(latLngs), { padding: [40, 40], maxZoom: 16 });
  }
}

let themeObserver = null;

onMounted(() => {
  // Exposer la méthode globale pour les boutons du popup Leaflet
  window.__vote_restaurant = (restaurantId, rank) => {
    emit('toggleRank', { restaurantId, rank });
  };

  const centerLat = props.departure?.latitude || 48.8566;
  const centerLon = props.departure?.longitude || 2.3522;

  map = L.map(mapContainer.value, {
    zoomControl: true,
    attributionControl: true,
  }).setView([centerLat, centerLon], 15);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  }).addTo(map);

  markersLayer = L.featureGroup().addTo(map);

  updateMarkers();

  // Observer les changements de thème (classe html)
  themeObserver = new MutationObserver(() => {
    updateMarkers();
  });
  themeObserver.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
});

onUnmounted(() => {
  if (themeObserver) {
    themeObserver.disconnect();
    themeObserver = null;
  }
  if (window.__vote_restaurant) {
    delete window.__vote_restaurant;
  }
  if (map) {
    map.remove();
    map = null;
  }
});

watch(
  () => [props.selectedRankings, props.restaurants],
  () => {
    updateMarkers();
  },
  { deep: true }
);
</script>

<template>
  <div class="rounded-3xl border border-[var(--border-main)] overflow-hidden shadow-xl bg-[var(--bg-surface)]">
    <div class="p-4 sm:p-5 bg-[var(--bg-surface-subtle)] border-b border-[var(--border-main)] flex items-center justify-between text-sm text-[var(--text-muted)]">
      <div class="flex items-center gap-3">
        <span class="flex items-center gap-1.5 font-serif text-lg font-bold text-[var(--text-main)]">
          <span>🗺️</span> Carte des restaurants
        </span>
        <span class="text-[var(--text-faint)]">•</span>
        <span class="font-serif text-sm sm:text-base">Rayon : {{ departure.radius_meters }} m</span>
      </div>
      <div class="flex items-center gap-2">
        <span class="inline-flex items-center gap-1.5 font-medium text-white bg-[var(--accent-red)] px-3 py-1 rounded-full shadow-2xs font-serif text-xs sm:text-sm">
          <span class="w-1.5 h-1.5 rounded-full bg-white"></span> 1er choix
        </span>
        <span class="hidden sm:inline text-[var(--text-faint)] font-serif text-sm italic">Cliquez sur une épingle pour voter</span>
      </div>
    </div>
    <div ref="mapContainer" class="w-full h-80 sm:h-96 z-10"></div>
  </div>
</template>
