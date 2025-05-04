document.addEventListener('DOMContentLoaded', async () => {
    const container = document.getElementById('host-bookings-list');
  
    try {
      const resp = await fetch('/api/bookings/host');
      if (!resp.ok) throw new Error(`Error ${resp.status}`);
      const list = await resp.json();
  
      if (!list.length) {
        container.innerHTML = '<p>No bookings on your properties yet.</p>';
        return;
      }
  
      container.innerHTML = list.map(b => `
        <div class="booking-card">
          <h3>Booking ID: ${b.booking_id}</h3>
          <p><strong>Property ID:</strong> ${b.property_id}</p>
          <p><strong>Dates:</strong> ${b.start_date} → ${b.end_date}</p>
          <button class="chat-btn" data-id="${b.booking_id}">Chat</button>
        </div>
      `).join('');
  
      // Wire chat buttons
      document.querySelectorAll('.chat-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          window.location.href = `/chat/${btn.dataset.id}`;
        });
      });
  
    } catch (err) {
      container.innerHTML = `<p class="error">${err.message}</p>`;
    }
  });
  