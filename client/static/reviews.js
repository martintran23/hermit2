document.addEventListener('DOMContentLoaded', () => {
    const propertyId = window.location.pathname.split('/').pop();
    const listEl     = document.getElementById('reviews-list');
    const ratingEl   = document.getElementById('rating');
    const commentEl  = document.getElementById('comment');
    const submitBtn  = document.getElementById('submit-review');
  
    async function loadReviews() {
      const res = await fetch(`/api/reviews/${propertyId}`);
      if (!res.ok) {
        listEl.innerHTML = '<p>Failed to load reviews.</p>';
        return;
      }
      const revs = await res.json();
      if (!revs.length) {
        listEl.innerHTML = '<p>No reviews yet.</p>';
        return;
      }
      listEl.innerHTML = revs.map(r => `
        <div class="ticket-item">
          <div class="ticket-header">
            <span>${r.user_email}</span>
            <span class="ticket-time">${new Date(r.timestamp).toLocaleString()}</span>
          </div>
          <p class="ticket-message">Rating: ${'★'.repeat(r.rating)}${'☆'.repeat(5-r.rating)}</p>
          <p class="ticket-message">${r.comment}</p>
        </div>
      `).join('');
    }
  
    if (submitBtn) {
      submitBtn.addEventListener('click', async () => {
        const rating  = ratingEl.value;
        const comment = commentEl.value.trim();
        const res = await fetch(`/api/reviews/${propertyId}`, {
          method: 'POST',
          headers: {'Content-Type':'application/json'},
          body: JSON.stringify({ rating, comment })
        });
        if (!res.ok) {
          alert('Failed to submit review');
          return;
        }
        commentEl.value = '';
        ratingEl.value  = '5';
        loadReviews();
      });
    }
  
    loadReviews();
  });
  