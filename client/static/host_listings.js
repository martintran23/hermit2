document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('new-listing-form');
    const container = document.getElementById('listings-container');
  
    async function loadListings() {
      const res = await fetch('/api/listings');
      const list = await res.json();
      if (!list.length) {
        container.innerHTML = '<p>No listings yet.</p>';
        return;
      }
      container.innerHTML = list.map(l => `
        <div class="booking-card">
          <h3>${l.title}</h3>
          <p>${l.address}</p>
          <p><strong>$${l.price}</strong></p>
          <img src="${l.image_url}" alt="" style="max-width:100%;border-radius:6px;">
          <p>${l.description}</p>
          <button class="edit-btn"    data-id="${l.id}">Edit</button>
          <button class="delete-btn"  data-id="${l.id}">Delete</button>
        </div>
      `).join('');
  
      document.querySelectorAll('.delete-btn').forEach(b => {
        b.addEventListener('click', async () => {
          if (!confirm('Delete this listing?')) return;
          const id = b.dataset.id;
          await fetch(`/api/listings/${id}`, { method: 'DELETE' });
          loadListings();
        });
      });
  
      document.querySelectorAll('.edit-btn').forEach(b => {
        b.addEventListener('click', id => {
          // For simplicity, prompt inline
          const listing = list.find(x => x.id === b.dataset.id);
          const newTitle = prompt('New title', listing.title);
          if (!newTitle) return;
          fetch(`/api/listings/${b.dataset.id}`, {
            method:'PUT',
            headers:{'Content-Type':'application/json'},
            body: JSON.stringify({ title: newTitle })
          }).then(loadListings);
        });
      });
    }
  
    form.addEventListener('submit', async e => {
      e.preventDefault();
      const data = Object.fromEntries(new FormData(form).entries());
      await fetch('/api/listings', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify(data)
      });
      form.reset();
      loadListings();
    });
  
    loadListings();
  });
  