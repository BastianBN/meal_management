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
  let bgColor = '#2C2019';
  let badgeText = `${restaurant.walking_time_min}m`;
  let ringColor = 'rgba(44, 32, 25, 0.15)';
  let scale = '1';

  if (rank === 1) {
    bgColor = '#C2542D';
    badgeText = '1er';
    ringColor = 'rgba(194, 84, 45, 0.35)';
    scale = '1.15';
  } else if (rank === 2) {
    bgColor = '#586F54';
    badgeText = '2e';
    ringColor = 'rgba(88, 111, 84, 0.35)';
    scale = '1.1';
  } else if (rank === 3) {
    bgColor = '#7E6C5C';
    badgeText = '3e';
    ringColor = 'rgba(126, 108, 92, 0.35)';
    scale = '1.05';
  }

  return L.divIcon({
    className: 'custom-restaurant-pin',
    html: `
      <div style="transform: scale(${scale}); transform-origin: bottom center; transition: all 0.2s ease;">
        <div style="background: ${bgColor}; color: white; padding: 4px 8px; border-radius: 9999px; font-size: 11px; font-weight: 500; border: 2px solid #FFFCF7; box-shadow: 0 2px 6px ${ringColor}; display: flex; align-items: center; gap: 3px; white-space: nowrap; cursor: pointer;">
          <span>🍽️</span>
          <span>${badgeText}</span>
        </div>
        <div style="width: 0; height: 0; border-left: 5px solid transparent; border-right: 5px solid transparent; border-top: 6px solid ${bgColor}; margin: 0 auto; margin-top: -1px;"></div>
      </div>
    `,
    iconSize: [44, 32],
    iconAnchor: [22, 32],
    popupAnchor: [0, -32],
  });
}

function buildPopupHtml(r) {
  const currentRank = getRank(r.id);
  const siteBtn = r.website_url 
    ? `<a href="${r.website_url}" target="_blank" rel="noopener" style="display: inline-block; font-size: 11px; color: #C2542D; font-weight: 500; text-decoration: underline; margin-right: 8px;">Site officiel</a>`
    : '';
  const gmapsBtn = r.google_maps_url
    ? `<a href="${r.google_maps_url}" target="_blank" rel="noopener" style="display: inline-block; font-size: 11px; color: #857263; font-weight: 500; text-decoration: underline;">Fiche Google & Avis</a>`
    : '';

  return `
    <div style="padding: 14px; min-width: 230px; max-width: 290px; font-family: inherit; background: #FFFCF7; border-radius: 12px;">
      <div style="font-size: 10px; font-weight: 600; color: #C2542D; text-transform: uppercase; margin-bottom: 2px; letter-spacing: 0.5px;">
        ${r.cuisine || 'Restaurant'} • ${r.distance_meters} m (~${r.walking_time_min} min)
      </div>
      <div style="font-size: 16px; font-family: 'Shippori Mincho', serif; font-weight: 600; color: #2C2019; margin-bottom: 6px; line-height: 1.2;">
        ${r.name}
      </div>
      ${r.menu_summary ? `<div style="font-size: 11px; color: #5D4B3E; margin-bottom: 8px; line-height: 1.3;">${r.menu_summary}</div>` : ''}
      <div style="margin-bottom: 10px;">
        ${siteBtn}
        ${gmapsBtn}
      </div>
      <div style="border-top: 1px solid #E5D6C5; padding-top: 8px; display: flex; gap: 4px;">
        <button onclick="window.__vote_restaurant(${r.id}, 1)" style="flex: 1; padding: 5px 6px; font-size: 10px; font-weight: 500; border-radius: 8px; border: 1px solid #ECCDBE; background: ${currentRank === 1 ? '#C2542D' : '#FAF0E8'}; color: ${currentRank === 1 ? '#ffffff' : '#7C2D12'}; cursor: pointer;">
          1er (3 pts)
        </button>
        <button onclick="window.__vote_restaurant(${r.id}, 2)" style="flex: 1; padding: 5px 6px; font-size: 10px; font-weight: 500; border-radius: 8px; border: 1px solid #C8D7C4; background: ${currentRank === 2 ? '#586F54' : '#F0F5EE'}; color: ${currentRank === 2 ? '#ffffff' : '#2F3D2C'}; cursor: pointer;">
          2e (2 pts)
        </button>
        <button onclick="window.__vote_restaurant(${r.id}, 3)" style="flex: 1; padding: 5px 6px; font-size: 10px; font-weight: 500; border-radius: 8px; border: 1px solid #DBCFBF; background: ${currentRank === 3 ? '#7E6C5C' : '#F4EDE5'}; color: ${currentRank === 3 ? '#ffffff' : '#4A433A'}; cursor: pointer;">
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
      color: '#ea580c',
      weight: 1.5,
      opacity: 0.6,
      fillColor: '#ea580c',
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
});

onUnmounted(() => {
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
  <div class="rounded-2xl border border-slate-200 overflow-hidden shadow-xs bg-white">
    <div class="p-3 bg-slate-50 border-b border-slate-200/80 flex items-center justify-between text-xs text-slate-600">
      <div class="flex items-center gap-3">
        <span class="flex items-center gap-1.5 font-semibold text-slate-900">
          <span>🗺️</span> Carte des restaurants
        </span>
        <span class="text-slate-400">•</span>
        <span>Rayon de marche : {{ departure.radius_meters }} m</span>
      </div>
      <div class="flex items-center gap-2">
        <span class="inline-flex items-center gap-1 font-medium text-amber-700 bg-amber-50 px-2 py-0.5 rounded-md border border-amber-200/60">
          <span class="w-2 h-2 rounded-full bg-amber-500"></span> 1er choix
        </span>
        <span class="hidden sm:inline text-slate-400">Cliquez sur un marqueur pour voter</span>
      </div>
    </div>
    <div ref="mapContainer" class="w-full h-80 sm:h-96 z-10"></div>
  </div>
</template>
