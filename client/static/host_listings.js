document.addEventListener('DOMContentLoaded', () => {
  const form       = document.getElementById('new-listing-form');
  const titleEl    = document.getElementById('listing-title');
  const addrEl     = document.getElementById('listing-address');
  const priceEl    = document.getElementById('listing-price');
  const descEl     = document.getElementById('listing-description');
  const imgEl      = document.getElementById('listing-image_url');
  const idEl       = document.getElementById('listing-id');
  const submitBtn  = document.getElementById('submit-btn');
  const cancelBtn  = document.getElementById('cancel-edit-btn');
  const headerEl   = document.getElementById('form-title');
  const container  = document.getElementById('listings-container');

  let isEditMode = false;

  async function loadListings() {
    const res = await fetch('/api/listings');
    const list = res.ok ? await res.json() : [];
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
        <button class="edit-btn"   data-id="${l.id}">Edit</button>
        <button class="delete-btn" data-id="${l.id}">Delete</button>
      </div>
    `).join('');

    // Wire delete
    document.querySelectorAll('.delete-btn').forEach(btn => {
      btn.addEventListener('click', async () => {
        if (!confirm('Delete this listing?')) return;
        await fetch(`/api/listings/${btn.dataset.id}`, { method: 'DELETE' });
        loadListings();
      });
    });

    // Wire edit
    document.querySelectorAll('.edit-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const listing = list.find(x => x.id === btn.dataset.id);
        // Populate form
        idEl.value       = listing.id;
        titleEl.value    = listing.title;
        addrEl.value     = listing.address;
        priceEl.value    = listing.price;
        descEl.value     = listing.description;
        imgEl.value      = listing.image_url;
        // Switch to edit mode
        isEditMode = true;
        headerEl.textContent    = 'Edit Listing';
        submitBtn.textContent   = 'Save Changes';
        cancelBtn.style.display = 'inline-block';
      });
    });
  }

  // Cancel edit
  cancelBtn.addEventListener('click', () => {
    form.reset();
    idEl.value = '';
    isEditMode = false;
    headerEl.textContent    = 'Add a New Listing';
    submitBtn.textContent   = 'Add Listing';
    cancelBtn.style.display = 'none';
  });

  // Form submit (create or update)
  form.addEventListener('submit', async e => {
    e.preventDefault();
    const data = {
      title:       titleEl.value,
      address:     addrEl.value,
      price:       priceEl.value,
      description: descEl.value,
      image_url:   imgEl.value
    };

    if (isEditMode && idEl.value) {
      // Update existing listing
      await fetch(`/api/listings/${idEl.value}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
    } else {
      // Create new listing
      await fetch('/api/listings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
    }

    // Reset form & reload
    cancelBtn.click();
    loadListings();
  });

  // Initial load
  loadListings();
});
