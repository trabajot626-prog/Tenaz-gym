/* payments.js */

let membersList = [];
let plansList   = [];

async function loadInitialData() {
  const [mRes, pRes] = await Promise.all([
    api.get('/api/members?per_page=1000'),
    api.get('/api/plans')
  ]);
  if (mRes && mRes.success) {
    membersList = mRes.data;
    const sel = document.getElementById('paymentMember');
    sel.innerHTML = '<option value="">Seleccionar miembro…</option>' +
      membersList.map(m =>
        `<option value="${m.id}" data-plan="${m.plan_id}">${escHtml(m.name)} ${escHtml(m.last_name)} – ${escHtml(m.id_number)}</option>`
      ).join('');
  }
  if (pRes && pRes.success) {
    plansList = pRes.data;
  }
}

async function loadPayments() {
  const res = await api.get('/api/payments');
  if (!res || !res.success) return;
  const tbody = document.getElementById('paymentsBody');
  if (!res.data.length) {
    tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">Sin pagos registrados</td></tr>';
    return;
  }
  tbody.innerHTML = res.data.map(p => `
    <tr>
      <td>${p.id}</td>
      <td>${escHtml(p.member_name)}</td>
      <td>${p.date}</td>
      <td>${p.months}</td>
      <td>${formatMoney(p.amount)}</td>
      <td>${escHtml(p.description)}</td>
      <td>
        <button class="btn btn-sm btn-danger" onclick="deletePayment(${p.id})">🗑 Eliminar</button>
      </td>
    </tr>
  `).join('');
}

async function deletePayment(id) {
  if (!confirm('¿Eliminar este pago?')) return;
  const res = await api.delete(`/api/payments/${id}`);
  if (res && res.success) {
    showToast('Pago eliminado', 'success');
    loadPayments();
  } else {
    showToast((res && res.error) || 'Error al eliminar', 'error');
  }
}

function getPlanForMember(planId) {
  return plansList.find(p => p.id === planId) || null;
}

function updateAmount() {
  const months    = parseInt(document.getElementById('paymentMonths').value) || 1;
  const unitPrice = parseFloat(document.getElementById('planUnitPrice').value) || 0;
  document.getElementById('paymentAmount').value = (unitPrice * months).toFixed(2);
}

// Member selector change: fetch aligned date and pre-fill
document.getElementById('paymentMember').addEventListener('change', async function() {
  const memberId = this.value;
  const infoEl   = document.getElementById('memberExpiryInfo');
  const expiryEl = document.getElementById('memberCurrentExpiry');
  const unitEl   = document.getElementById('planUnitPrice');

  if (!memberId) {
    infoEl.style.display = 'none';
    unitEl.value = '';
    updateAmount();
    return;
  }

  // Get aligned date (current expiry) for pre-fill
  const res = await api.get(`/api/payments/member/${memberId}/aligned-date`);
  if (res && res.success) {
    document.getElementById('paymentDate').value = res.data.aligned_date;
    expiryEl.textContent = `Vencimiento actual: ${res.data.aligned_date}`;
    infoEl.style.display = 'block';
  }

  // Set plan unit price
  const selectedOption = this.options[this.selectedIndex];
  const planId = parseInt(selectedOption.dataset.plan);
  const plan   = getPlanForMember(planId);
  if (plan) {
    unitEl.value = plan.price;
  } else {
    unitEl.value = '';
  }
  updateAmount();
});

document.getElementById('paymentMonths').addEventListener('change', updateAmount);

document.getElementById('addPaymentBtn').addEventListener('click', () => {
  document.getElementById('paymentForm').reset();
  document.getElementById('paymentDate').value = today();
  document.getElementById('memberExpiryInfo').style.display = 'none';
  document.getElementById('paymentFormError').style.display = 'none';
  document.getElementById('planUnitPrice').value = '';
  document.getElementById('paymentModal').classList.add('active');
});

document.getElementById('cancelPaymentBtn').addEventListener('click', () => {
  document.getElementById('paymentModal').classList.remove('active');
});
document.getElementById('paymentModalClose').addEventListener('click', () => {
  document.getElementById('paymentModal').classList.remove('active');
});

document.getElementById('paymentForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const body = {
    member_id:   document.getElementById('paymentMember').value,
    date:        document.getElementById('paymentDate').value,
    months:      parseInt(document.getElementById('paymentMonths').value),
    amount:      parseFloat(document.getElementById('paymentAmount').value),
    description: document.getElementById('paymentDescription').value.trim()
  };
  const res = await api.post('/api/payments', body);
  if (res && res.success) {
    document.getElementById('paymentModal').classList.remove('active');
    showToast('Pago registrado exitosamente', 'success');
    loadPayments();
  } else {
    const errEl = document.getElementById('paymentFormError');
    errEl.textContent = (res && res.error) || 'Error al registrar pago';
    errEl.style.display = 'block';
  }
});

// Init
loadInitialData();
loadPayments();
