/* dashboard.js */

async function loadDashboard() {
  const [kpiRes, expiringRes] = await Promise.all([
    api.get('/api/dashboard'),
    api.get('/api/dashboard/expiring')
  ]);

  if (kpiRes && kpiRes.success) {
    const d = kpiRes.data;
    document.getElementById('totalMembers').textContent  = d.total_members;
    document.getElementById('activeMembers').textContent = d.active_members;
    document.getElementById('monthlyIncome').textContent = formatMoney(d.monthly_income);
    document.getElementById('expiringSoon').textContent  = d.expiring_soon;
  }

  const tbody = document.getElementById('expiringBody');
  if (expiringRes && expiringRes.success) {
    const list = expiringRes.data;
    if (!list.length) {
      tbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted">Ningún miembro vence en los próximos 7 días 🎉</td></tr>';
    } else {
      tbody.innerHTML = list.map(m => `
        <tr>
          <td>${escHtml(m.name)} ${escHtml(m.last_name)}</td>
          <td>${escHtml(m.phone)}</td>
          <td>${expiryBadge(m.expiry_date)}</td>
          <td>
            <button class="btn btn-sm btn-wa" onclick="openWhatsApp('${escHtml(m.whatsapp_url)}')">
              📲 WhatsApp
            </button>
          </td>
        </tr>
      `).join('');
    }
  } else {
    tbody.innerHTML = '<tr><td colspan="4" class="text-danger text-center">Error al cargar</td></tr>';
  }
}

loadDashboard();
