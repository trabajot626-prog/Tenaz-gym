/* ============================================================
   main.js – Global utilities, API client, shared init
   ============================================================ */

// Set API_URL from build-time env injection or fallback
window.API_URL = window.API_URL || 'http://localhost:5000';

/* ── API Client ──────────────────────────────────────────── */
const api = {
  async request(method, path, data = null, formData = null) {
    const opts = {
      method,
      credentials: 'include',
      headers: {}
    };
    if (formData) {
      opts.body = formData;
    } else if (data) {
      opts.headers['Content-Type'] = 'application/json';
      opts.body = JSON.stringify(data);
    }
    try {
      const res = await fetch(window.API_URL + path, opts);
      if (res.status === 401) {
        window.location.href = '/login.html';
        return null;
      }
      return await res.json();
    } catch (err) {
      console.error('API error:', err);
      return { success: false, error: 'Error de conexión con el servidor' };
    }
  },
  get:    (path)        => api.request('GET',    path),
  post:   (path, data)  => api.request('POST',   path, data),
  put:    (path, data)  => api.request('PUT',    path, data),
  delete: (path)        => api.request('DELETE', path),
  upload: (path, fd)    => api.request('POST',   path, null, fd),
};

/* ── Toast Notifications ─────────────────────────────────── */
function showToast(message, type = 'info', duration = 3500) {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transition = 'opacity 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

/* ── Utility helpers ─────────────────────────────────────── */
function escHtml(str) {
  if (str == null) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function formatMoney(amount) {
  if (amount == null) return '–';
  return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(amount);
}

function today() {
  return new Date().toISOString().split('T')[0];
}

function expiryBadge(dateStr) {
  if (!dateStr) return '<span class="badge badge-warning">Sin fecha</span>';
  const exp = new Date(dateStr + 'T00:00:00');
  const now = new Date(); now.setHours(0,0,0,0);
  const diff = Math.ceil((exp - now) / 86400000);
  if (diff < 0) return `<span class="badge badge-danger">Vencido (${dateStr})</span>`;
  if (diff <= 7) return `<span class="badge badge-warning">Vence ${dateStr}</span>`;
  return `<span class="badge badge-success">${dateStr}</span>`;
}

/* ── Sidebar / Hamburger ─────────────────────────────────── */
(function initSidebar() {
  const sidebar  = document.getElementById('sidebar');
  const hamburger = document.getElementById('hamburger');
  const overlay  = document.getElementById('overlay');
  const closeBtn = document.getElementById('sidebarClose');

  function openSidebar() {
    sidebar && sidebar.classList.add('open');
    overlay && overlay.classList.add('active');
  }
  function closeSidebar() {
    sidebar && sidebar.classList.remove('open');
    overlay && overlay.classList.remove('active');
  }

  hamburger && hamburger.addEventListener('click', openSidebar);
  closeBtn  && closeBtn.addEventListener('click', closeSidebar);
  overlay   && overlay.addEventListener('click', closeSidebar);
})();

/* ── Logout ──────────────────────────────────────────────── */
(function initLogout() {
  const btn = document.getElementById('logoutBtn');
  if (!btn) return;
  btn.addEventListener('click', async () => {
    await api.post('/api/auth/logout');
    window.location.href = '/login.html';
  });
})();

/* ── Auth guard (skip on login page) ────────────────────── */
(function authGuard() {
  if (window.location.pathname.includes('login')) return;
  api.get('/api/auth/status').then(res => {
    if (!res || !res.success || !res.data.logged_in) {
      window.location.href = '/login.html';
    }
  });
})();
