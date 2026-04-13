/* whatsapp.js – WhatsApp URL helper (client-side) */

function openWhatsApp(url) {
  window.open(url, '_blank', 'noopener,noreferrer');
}

async function openWhatsAppForMember(memberId) {
  const res = await api.get(`/api/members/${memberId}/whatsapp`);
  if (res && res.success) {
    openWhatsApp(res.data.url);
  } else {
    showToast('No se pudo generar el enlace de WhatsApp', 'error');
  }
}
