const API_BASE_URL = import.meta.env.VITE_API_BASE_URL 
  ? import.meta.env.VITE_API_BASE_URL.replace(/\/$/, '') 
  : '';

export async function createSession(departureAddress, radiusMeters = 800) {
  const res = await fetch(`${API_BASE_URL}/api/sessions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      departure_address: departureAddress,
      radius_meters: Number(radiusMeters),
    }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Impossible de créer la session de vote.');
  }

  return res.json();
}

export async function getSession(sessionId) {
  const res = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Session introuvable.');
  }
  return res.json();
}

export async function submitVote(sessionId, voteData) {
  const res = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}/votes`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      voter_name: voteData.voterName,
      first_choice_id: voteData.firstChoiceId,
      second_choice_id: voteData.secondChoiceId || null,
      third_choice_id: voteData.thirdChoiceId || null,
    }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Impossible d’enregistrer votre vote.');
  }

  return res.json();
}

export async function getLeaderboard(sessionId) {
  const res = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}/votes/leaderboard`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Erreur lors de la récupération du classement.');
  }
  return res.json();
}

export function connectSessionWebSocket(sessionId, onMessage, onError) {
  let wsUrl;
  if (API_BASE_URL) {
    const wsProto = API_BASE_URL.startsWith('https') ? 'wss:' : 'ws:';
    const host = API_BASE_URL.replace(/^https?:\/\//, '');
    wsUrl = `${wsProto}//${host}/api/ws/${sessionId}`;
  } else {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    wsUrl = `${protocol}//${window.location.host}/api/ws/${sessionId}`;
  }

  let ws;
  let pingInterval;

  try {
    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      // Ping keepalive toutes les 25 secondes
      pingInterval = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send('ping');
        }
      }, 25000);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (err) {
        // Ignorer pings/pongs
      }
    };

    ws.onerror = (err) => {
      if (onError) onError(err);
    };

    ws.onclose = () => {
      clearInterval(pingInterval);
    };
  } catch (err) {
    if (onError) onError(err);
  }

  return {
    close: () => {
      clearInterval(pingInterval);
      if (ws) ws.close();
    }
  };
}
