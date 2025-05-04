document.addEventListener('DOMContentLoaded', () => {
    const bookingId = window.location.pathname.split('/').pop();
    const msgsEl    = document.getElementById('messages');
    const form      = document.getElementById('chat-form');
    const input     = document.getElementById('chat-input');
  
    async function loadMessages() {
      const res = await fetch(`/api/chat/${bookingId}`);
      if (!res.ok) return;
      const msgs = await res.json();
      msgsEl.innerHTML = msgs.map(m => `
        <div class="ticket-item">
          <div class="ticket-header">
            <span>${m.user_email}</span>
            <span class="ticket-time">${new Date(m.timestamp).toLocaleString()}</span>
          </div>
          <p class="ticket-message">${m.message}</p>
        </div>
      `).join('');
      msgsEl.scrollTop = msgsEl.scrollHeight;
    }
  
    form.addEventListener('submit', async e => {
      e.preventDefault();
      const text = input.value.trim();
      if (!text) return;
      await fetch(`/api/chat/${bookingId}`, {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ message: text })
      });
      input.value = '';
      loadMessages();
    });
  
    // poll every 5s
    loadMessages();
    setInterval(loadMessages, 5000);
  });
  