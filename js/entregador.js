const API_URL = window.location.origin;

let entregas = [];
let currentEntrega = null;
let deferredInstallPrompt = null;

// Service Worker Registration
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js').catch(err => {
    console.error('Service Worker registration failed:', err);
  });
}

// Capture Android install prompt
window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredInstallPrompt = e;
  showInstallButton();
});

// When app is installed, hide the button
window.addEventListener('appinstalled', () => {
  deferredInstallPrompt = null;
  hideInstallButton();
});

function showInstallButton() {
  const btn = document.getElementById('installBanner');
  if (btn) btn.style.display = 'flex';
}

function hideInstallButton() {
  const btn = document.getElementById('installBanner');
  if (btn) btn.style.display = 'none';
}

async function installApp() {
  if (!deferredInstallPrompt) return;
  deferredInstallPrompt.prompt();
  const { outcome } = await deferredInstallPrompt.userChoice;
  if (outcome === 'accepted') {
    deferredInstallPrompt = null;
    hideInstallButton();
  }
}

const VAPID_PUBLIC_KEY = 'BNiQ0yNtE5rbfIqdwZbZc-oW4_42MntZAw5T0d5MAooN4UlRB5mwmeP70P_ZNmz4yOC6GXf-pudwKTXu9Uwo3cc';

async function subscribePushNotifications() {
  if (!('serviceWorker' in navigator) || !('PushManager' in window)) return;
  try {
    const registration = await navigator.serviceWorker.ready;
    let subscription = await registration.pushManager.getSubscription();
    if (!subscription) {
      const convertedVapidKey = urlBase64ToUint8Array(VAPID_PUBLIC_KEY);
      subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: convertedVapidKey
      });
    }
    
    // Send subscription to server
    const token = localStorage.getItem('entregador_token');
    await fetch(`${API_URL}/api/entregador/push/subscribe`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ subscription })
    });
    
    // Hide banner on success
    const banner = document.getElementById('notificationBanner');
    if(banner) banner.style.display = 'none';
    
    alert("Notificações ativadas com sucesso!");
    
  } catch (err) {
    console.error('Push subscription failed:', err);
    alert("Falha ao ativar notificações. Verifique se seu navegador suporta Push.");
  }
}

function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);
  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

function checkNotificationStatus() {
  const banner = document.getElementById('notificationBanner');
  if (!banner) return;
  
  if (!('Notification' in window)) {
    banner.style.display = 'none';
    return;
  }
  
  if (Notification.permission === 'default' || Notification.permission === 'prompt') {
    banner.style.display = 'block';
  } else {
    banner.style.display = 'none';
    // Se já tiver permissão (granted), tentar renovar/garantir a inscrição de forma silenciosa
    if (Notification.permission === 'granted') {
      subscribePushNotificationsSilently();
    }
  }
}

async function subscribePushNotificationsSilently() {
  if (!('serviceWorker' in navigator) || !('PushManager' in window)) return;
  try {
    const registration = await navigator.serviceWorker.ready;
    let subscription = await registration.pushManager.getSubscription();
    if (!subscription) {
      const convertedVapidKey = urlBase64ToUint8Array(VAPID_PUBLIC_KEY);
      subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: convertedVapidKey
      });
    }
    const token = localStorage.getItem('entregador_token');
    if (token) {
      await fetch(`${API_URL}/api/entregador/push/subscribe`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ subscription })
      });
    }
  } catch (e) {
    console.error('Silent sub failed', e);
  }
}

// Initialization
document.addEventListener('DOMContentLoaded', () => {
  const token = localStorage.getItem('entregador_token');
  if (token) {
    showScreen('dashboardScreen');
    loadEntregas();
    checkNotificationStatus();
    startLocationTracking();
  } else {
    showScreen('loginScreen');
  }

  // iOS detection - show tip since Safari doesn't support beforeinstallprompt
  const isIos = /iphone|ipad|ipod/i.test(navigator.userAgent);
  const isInStandaloneMode = window.matchMedia('(display-mode: standalone)').matches;
  const iosTip = document.getElementById('iosTip');
  if (isIos && !isInStandaloneMode && iosTip) {
    iosTip.style.display = 'flex';
  }
});

function showScreen(id) {
  document.querySelectorAll('.screen').forEach(s => s.style.display = 'none');
  document.getElementById(id).style.display = 'flex';
}

async function login() {
  const email = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value.trim();
  const errorDiv = document.getElementById('loginError');
  errorDiv.innerText = '';

  if (!email || !password) {
    errorDiv.innerText = 'Preencha e-mail e senha.';
    return;
  }

  try {
    const res = await fetch(`${API_URL}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    
    const data = await res.json();
    
    if (res.ok && data.token) {
      if (data.user.role !== 'entregador' && data.user.role !== 'admin') {
        errorDiv.innerText = 'Acesso negado. Apenas entregadores.';
        return;
      }
      localStorage.setItem('entregador_token', data.token);
      showScreen('dashboardScreen');
      loadEntregas();
      checkNotificationStatus();
      startLocationTracking();
    } else {
      errorDiv.innerText = data.error || 'Falha no login.';
    }
  } catch (err) {
    console.error(err);
    errorDiv.innerText = 'Erro ao conectar com o servidor.';
  }
}

function logout() {
  localStorage.removeItem('entregador_token');
  showScreen('loginScreen');
}

async function loadEntregas() {
  const token = localStorage.getItem('entregador_token');
  const container = document.getElementById('listaEntregas');
  
  try {
    const res = await fetch(`${API_URL}/api/entregador/entregas/disponiveis`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    if (res.ok) {
      entregas = await res.json();
      renderEntregas();
    } else if (res.status === 401 || res.status === 403) {
      logout();
    }
  } catch (err) {
    console.error(err);
    container.innerHTML = '<div style="text-align:center; padding: 20px; color: var(--danger);">Erro ao carregar entregas.</div>';
  }
}

function renderEntregas() {
  const container = document.getElementById('listaEntregas');
  container.innerHTML = '';

  if (entregas.length === 0) {
    container.innerHTML = '<div style="text-align:center; padding: 20px; color: var(--text-muted);">Nenhuma entrega pronta para coleta.</div>';
    return;
  }

  entregas.forEach(e => {
    const dataObj = e.criado_em ? new Date(e.criado_em) : null;
    const hora = dataObj ? `${dataObj.getHours().toString().padStart(2,'0')}:${dataObj.getMinutes().toString().padStart(2,'0')}` : '';
    
    const tag = e.pago 
      ? '<span class="tag tag-green">Pago</span>' 
      : `<span class="tag tag-orange">Pagar: R$ ${e.valor || '0.00'}</span>`;

    const card = document.createElement('div');
    card.className = 'card';
    card.onclick = () => openDetails(e.id);
    card.innerHTML = `
      <div class="card-header">
        <span class="card-id">#${e.id}</span>
        <span class="card-time">${hora}</span>
      </div>
      <div class="card-title">${escapeHtml(e.nome_cliente)}</div>
      <div class="card-info">
        <span>📍 ${escapeHtml(e.localizacao).split(',')[0]}</span>
        <span>📦 ${escapeHtml(e.nome_peca)}</span>
        <div style="margin-top: 4px;">${tag}</div>
      </div>
    `;
    container.appendChild(card);
  });
}

function openDetails(id) {
  currentEntrega = entregas.find(e => e.id === id);
  if (!currentEntrega) return;
  
  const e = currentEntrega;
  const container = document.getElementById('detailsContent');
  
  let mapsBtn = '';
  if (e.latitude && e.longitude) {
    mapsBtn = `<a href="https://maps.google.com/?q=${e.latitude},${e.longitude}" target="_blank" class="btn-maps">📍 Abrir Navegação (Google Maps)</a>`;
  }

  container.innerHTML = `
    <div class="detail-row">
      <span class="detail-label">Cliente</span>
      <span class="detail-value" style="font-size:18px; font-weight:600;">${escapeHtml(e.nome_cliente)}</span>
    </div>
    <div class="detail-row">
      <span class="detail-label">Telefone</span>
      <span class="detail-value">${escapeHtml(e.telefone_cliente || '-')}</span>
    </div>
    <div class="detail-row">
      <span class="detail-label">Endereço de Entrega</span>
      <span class="detail-value">${escapeHtml(e.localizacao)}</span>
      ${mapsBtn}
    </div>
    <div style="height:1px; background:var(--border); margin: 8px 0;"></div>
    <div class="detail-row">
      <span class="detail-label">Produto</span>
      <span class="detail-value"><strong>${escapeHtml(e.nome_peca)}</strong> (Tam: ${escapeHtml(e.tamanho_peca || '-')})</span>
    </div>
    <div class="detail-row" style="margin-top: 8px;">
      <span class="detail-label">Pagamento</span>
      <span class="detail-value">
        ${e.pago ? '<span style="color:#00a884;font-weight:600;">Já Pago</span>' : `<span style="color:#f59e0b;font-weight:600;">Cobrar: R$ ${e.valor || '0.00'}</span> (${e.forma_pagamento || '-'})`}
      </span>
    </div>
  `;
  
  showScreen('detailsScreen');
}

function voltarParaDashboard() {
  currentEntrega = null;
  showScreen('dashboardScreen');
  loadEntregas();
}

async function aceitarEntrega() {
  if (!currentEntrega) return;
  
  // Se já está aceita por esse entregador, vira "Concluir Entrega"
  // Para fins do plano, vamos tratar apenas o aceite primeiro
  const codigo = prompt("Digite o código de verificação para travar essa entrega em seu nome:");
  if (!codigo) return; // Usuário cancelou ou deixou vazio
  
  const token = localStorage.getItem('entregador_token');
  try {
    const res = await fetch(`${API_URL}/api/entregador/aceitar_entrega`, {
      method: 'POST',
      headers: { 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        entrega_id: currentEntrega.id,
        codigo_verificacao: codigo
      })
    });
    const data = await res.json();
    if (data.success) {
      alert('Entrega travada em seu nome com sucesso!');
      voltarParaDashboard();
    } else {
      alert(`Erro: ${data.error || 'Código incorreto ou entrega indisponível.'}`);
    }
  } catch (err) {
    console.error(err);
    alert('Erro ao se conectar ao servidor.');
  }
}

function escapeHtml(text) {
  if (!text) return '';
  const div = document.createElement('div');
  div.innerText = text;
  return div.innerHTML;
}

// === LOCATION TRACKING ===
let locationInterval = null;

function startLocationTracking() {
  // Clear any existing interval
  if (locationInterval) clearInterval(locationInterval);
  
  // Track immediately
  trackLocation();
  
  // Then track every 5 seconds
  locationInterval = setInterval(trackLocation, 5000);
}

function trackLocation() {
  if (!navigator.geolocation) return;
  
  navigator.geolocation.getCurrentPosition(
    (position) => {
      sendLocationToBackend(position.coords.latitude, position.coords.longitude);
    },
    (err) => {
      console.warn('Erro ao obter GPS (pode estar negado ou desativado):', err.message);
    },
    { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
  );
}

async function sendLocationToBackend(lat, lng) {
  const token = localStorage.getItem('entregador_token');
  if (!token) return;
  
  try {
    await fetch(`${API_URL}/api/entregador/location`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ lat, lng })
    });
  } catch (err) {
    console.error('Falha ao enviar localização', err);
  }
}

