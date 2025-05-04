document.addEventListener('DOMContentLoaded', async () => {
  const container = document.getElementById('bookings-list');

  try {
    const resp = await fetch(
      `/api/bookings/user/${encodeURIComponent(window.currentUser)}`
    );
    if (!resp.ok) throw new Error(`Error ${resp.status}`);
    const bookings = await resp.json();

    if (!bookings.length) {
      container.innerHTML = '<p>You have no bookings yet.</p>';
      return;
    }

    container.innerHTML = bookings
      .map(
        (b) => `
      <div class="booking-card">
        <h3>Booking ID: ${b.booking_id}</h3>
        <p><strong>Property:</strong> ${b.property_id}</p>
        <p><strong>Dates:</strong> ${b.start_date} → ${b.end_date}</p>
        <button class="cancel-btn"  data-id="${b.booking_id}">Cancel</button>
        <button class="modify-btn"  data-id="${b.booking_id}">Modify</button>
        <button class="chat-btn"    data-id="${b.booking_id}">Chat</button>
        <button class="support-btn" data-id="${b.booking_id}">Need Help?</button>
      </div>`
      )
      .join('');

    // Cancel
    document.querySelectorAll('.cancel-btn').forEach((btn) => {
      btn.addEventListener('click', async () => {
        if (!confirm('Cancel this booking?')) return;
        const id = btn.dataset.id;
        const r = await fetch(`/api/bookings/${id}`, { method: 'DELETE' });
        if (r.ok) btn.closest('.booking-card').remove();
        else alert('Cancel failed');
      });
    });

    // Modify
    document.querySelectorAll('.modify-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        const id = btn.dataset.id;
        window.location.href = `/modify-booking?booking_id=${id}`;
      });
    });

    // Chat
    document.querySelectorAll('.chat-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        window.location.href = `/chat/${btn.dataset.id}`;
      });
    });

    // Support
    document.querySelectorAll('.support-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        window.location.href = `/support?booking_id=${btn.dataset.id}`;
      });
    });
  } catch (err) {
    container.innerHTML = `<p class="error">${err.message}</p>`;
  }
});
