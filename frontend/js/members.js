/* members.js */

let allPlans = [];
let currentPage = 1;
let totalPages = 1;
let searchTimeout = null;

async function loadPlansForSelect() {
  const res = await api.get('/api/plans');
  if (res && res.success) {
    allPlans = res.data;
    const sel = document.getElementById('memberPlan');
    sel.innerHTML = '<option value="">Seleccionar plan…</option>' +
      allPlans.map(p => `<option value="${p.id}">${escHtml(p.name)} – ${formatMoney(p.price)}</option>`).join('');
  }
}

async function loadMembers(page = 1) {
  const search = document.getElementById('searchInput').value.trim();
  const params = new URLSearchParams({ page, per_page: 20 });
  if (search) params.set('search', search);
  const res = await api.get(`/api/members?${params}`);
  if (!res || !res.success) return;

  currentPage = res.pagination.page;
  totalPages  = res.pagination.pages;
  renderMembers(res.data);
  renderPagination();
}

function renderMembers(members) {
  const tbody = document.getElementById('membersBody');
  if (!members.length) {
    tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">Sin miembros encontrados</td></tr>';
    return;
  }
  tbody.innerHTML = members.map(m => {
    const photoSrc = m.photo_path
      ? `${window.API_URL}${m.photo_path}`
      : 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 36 36"%3E%3Ccircle cx="18" cy="18" r="18" fill="%23dee2e6"/%3E%3Ctext x="18" y="24" text-anchor="middle" font-size="18" fill="%236c757d"%3E👤%3C/text%3E%3C/svg%3E';
    return `
      <tr>
        <td><img src="${photoSrc}" class="member-photo" alt="" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'36\' height=\'36\'%3E%3Ccircle cx=\'18\' cy=\'18\' r=\'18\' fill=\'%23dee2e6\'/%3E%3C/svg%3E'"></td>
        <td>${escHtml(m.name)} ${escHtml(m.last_name)}</td>
        <td>${escHtml(m.id_number)}</td>
        <td>${escHtml(m.phone)}</td>
        <td>${escHtml(m.plan_name || '–')}</td>
        <td>${expiryBadge(m.expiry_date)}</td>
        <td class="actions">
          <button class="btn btn-sm btn-primary"  onclick="viewMember(${m.id})">👁 Ver</button>
          <button class="btn btn-sm btn-secondary" onclick="editMember(${m.id})">✏ Editar</button>
          <button class="btn btn-sm btn-wa"        onclick="openWhatsAppForMember(${m.id})">📲</button>
          <button class="btn btn-sm btn-danger"    onclick="deleteMember(${m.id}, '${escHtml(m.name)}')">🗑</button>
        </td>
      </tr>
    `;
  }).join('');
}

function renderPagination() {
  const el = document.getElementById('pagination');
  if (totalPages <= 1) { el.innerHTML = ''; return; }
  let html = '';
  for (let i = 1; i <= totalPages; i++) {
    html += `<button class="${i === currentPage ? 'active' : ''}" onclick="loadMembers(${i})">${i}</button>`;
  }
  el.innerHTML = html;
}

async function viewMember(id) {
  const res = await api.get(`/api/members/${id}`);
  if (!res || !res.success) { showToast('Error al cargar miembro', 'error'); return; }
  const m = res.data;
  const photoSrc = m.photo_path ? `${window.API_URL}${m.photo_path}` : '';
  const payments = (m.payments || []).map(p => `
    <tr>
      <td>${p.date}</td>
      <td>${p.months} mes(es)</td>
      <td>${formatMoney(p.amount)}</td>
      <td>${escHtml(p.description)}</td>
    </tr>
  `).join('') || '<tr><td colspan="4" class="text-muted text-center">Sin pagos registrados</td></tr>';

  document.getElementById('detailTitle').textContent = `${m.name} ${m.last_name}`;
  document.getElementById('detailBody').innerHTML = `
    <div style="display:flex;gap:1.5rem;flex-wrap:wrap;margin-bottom:1rem;">
      ${photoSrc ? `<img src="${photoSrc}" style="width:80px;height:80px;border-radius:50%;object-fit:cover;" alt="">` : ''}
      <div>
        <p><strong>Cédula:</strong> ${escHtml(m.id_number)}</p>
        <p><strong>Teléfono:</strong> ${escHtml(m.phone)}</p>
        <p><strong>Email:</strong> ${escHtml(m.email || '–')}</p>
        <p><strong>Plan:</strong> ${escHtml(m.plan_name || '–')} – ${formatMoney(m.plan_price)}</p>
        <p><strong>Registro:</strong> ${m.registration_date || '–'}</p>
        <p><strong>Vencimiento:</strong> ${expiryBadge(m.expiry_date)}</p>
      </div>
    </div>
    <div style="display:flex;gap:0.5rem;margin-bottom:1rem;flex-wrap:wrap;">
      <button class="btn btn-wa" onclick="openWhatsAppForMember(${m.id})">📲 WhatsApp</button>
      <button class="btn btn-secondary" onclick="openPhotoModal(${m.id})">📷 Cambiar foto</button>
    </div>
    <h4 style="margin-bottom:0.5rem;">Historial de pagos</h4>
    <div class="table-responsive">
      <table class="table">
        <thead><tr><th>Fecha</th><th>Meses</th><th>Monto</th><th>Descripción</th></tr></thead>
        <tbody>${payments}</tbody>
      </table>
    </div>
  `;
  document.getElementById('detailModal').classList.add('active');
}

async function editMember(id) {
  const res = await api.get(`/api/members/${id}`);
  if (!res || !res.success) { showToast('Error al cargar miembro', 'error'); return; }
  const m = res.data;
  document.getElementById('memberId').value        = m.id;
  document.getElementById('memberName').value      = m.name;
  document.getElementById('memberLastName').value  = m.last_name;
  document.getElementById('memberIdNumber').value  = m.id_number;
  document.getElementById('memberPhone').value     = m.phone;
  document.getElementById('memberEmail').value     = m.email || '';
  document.getElementById('memberPlan').value      = m.plan_id;
  document.getElementById('memberRegDate').value   = m.registration_date || '';
  document.getElementById('memberExpiry').value    = m.expiry_date || '';
  document.getElementById('modalTitle').textContent = 'Editar Miembro';
  document.getElementById('memberFormError').style.display = 'none';
  document.getElementById('memberModal').classList.add('active');
}

async function deleteMember(id, name) {
  if (!confirm(`¿Eliminar a "${name}"? También se eliminarán sus pagos.`)) return;
  const res = await api.delete(`/api/members/${id}`);
  if (res && res.success) {
    showToast('Miembro eliminado', 'success');
    loadMembers(currentPage);
  } else {
    showToast((res && res.error) || 'Error al eliminar', 'error');
  }
}

function openPhotoModal(memberId) {
  document.getElementById('photoMemberId').value = memberId;
  document.getElementById('photoFile').value = '';
  document.getElementById('photoError').style.display = 'none';
  document.getElementById('photoModal').classList.add('active');
  document.getElementById('detailModal').classList.remove('active');
}

// Event listeners
document.getElementById('addMemberBtn').addEventListener('click', () => {
  document.getElementById('memberId').value = '';
  document.getElementById('memberForm').reset();
  document.getElementById('memberRegDate').value = today();
  document.getElementById('modalTitle').textContent = 'Agregar Miembro';
  document.getElementById('memberFormError').style.display = 'none';
  document.getElementById('memberModal').classList.add('active');
});

document.getElementById('cancelMemberBtn').addEventListener('click', () => {
  document.getElementById('memberModal').classList.remove('active');
});
document.getElementById('memberModalClose').addEventListener('click', () => {
  document.getElementById('memberModal').classList.remove('active');
});
document.getElementById('detailModalClose').addEventListener('click', () => {
  document.getElementById('detailModal').classList.remove('active');
});
document.getElementById('cancelPhotoBtn').addEventListener('click', () => {
  document.getElementById('photoModal').classList.remove('active');
});
document.getElementById('photoModalClose').addEventListener('click', () => {
  document.getElementById('photoModal').classList.remove('active');
});

document.getElementById('searchInput').addEventListener('input', () => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => loadMembers(1), 350);
});

document.getElementById('exportCsvBtn').addEventListener('click', () => {
  window.location.href = window.API_URL + '/api/members/export/csv';
});

document.getElementById('memberForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const id = document.getElementById('memberId').value;
  const body = {
    name:              document.getElementById('memberName').value.trim(),
    last_name:         document.getElementById('memberLastName').value.trim(),
    id_number:         document.getElementById('memberIdNumber').value.trim(),
    phone:             document.getElementById('memberPhone').value.trim(),
    email:             document.getElementById('memberEmail').value.trim(),
    plan_id:           document.getElementById('memberPlan').value,
    registration_date: document.getElementById('memberRegDate').value,
    expiry_date:       document.getElementById('memberExpiry').value || null
  };
  const res = id
    ? await api.put(`/api/members/${id}`, body)
    : await api.post('/api/members', body);
  if (res && res.success) {
    document.getElementById('memberModal').classList.remove('active');
    showToast(id ? 'Miembro actualizado' : 'Miembro creado', 'success');
    loadMembers(currentPage);
  } else {
    const errEl = document.getElementById('memberFormError');
    errEl.textContent = (res && res.error) || 'Error al guardar';
    errEl.style.display = 'block';
  }
});

document.getElementById('uploadPhotoBtn').addEventListener('click', async () => {
  const memberId = document.getElementById('photoMemberId').value;
  const file = document.getElementById('photoFile').files[0];
  const errEl = document.getElementById('photoError');
  errEl.style.display = 'none';
  if (!file) { errEl.textContent = 'Selecciona un archivo'; errEl.style.display = 'block'; return; }
  const fd = new FormData();
  fd.append('photo', file);
  const res = await api.upload(`/api/members/${memberId}/photo`, fd);
  if (res && res.success) {
    document.getElementById('photoModal').classList.remove('active');
    showToast('Foto actualizada', 'success');
    loadMembers(currentPage);
  } else {
    errEl.textContent = (res && res.error) || 'Error al subir';
    errEl.style.display = 'block';
  }
});

// Init
loadPlansForSelect();
loadMembers(1);
