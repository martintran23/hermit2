// client/static/script.js

document.addEventListener('DOMContentLoaded', () => {
    const searchForm       = document.getElementById('search-form');
    const locationInput    = document.getElementById('location-search');
    const checkInInput     = document.getElementById('check-in');
    const checkOutInput    = document.getElementById('check-out');
    const resultsContainer = document.getElementById('results');
  
    // Search form submission
    searchForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const query = locationInput.value.trim();
      if (!query) return;
      await fetchRentals(query);
    });
  
    // Fetch rental listings from backend
    async function fetchRentals(query) {
      const url = `/api/properties?location=${encodeURIComponent(query)}`;
      try {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`Error ${response.status}`);
        const listings = await response.json();
        if (!Array.isArray(listings) || listings.length === 0) {
          resultsContainer.innerHTML = `<p>No rentals found for "${query}".</p>`;
        } else {
          displayResults(listings);
        }
      } catch (error) {
        console.error('Fetch error:', error);
        resultsContainer.innerHTML = `<p>${error.message}</p>`;
      }
    }
  
    // Render listings and attach booking handlers
    function displayResults(listings) {
      resultsContainer.innerHTML = '';
      listings.forEach(listing => {
        const address = listing.location?.address || {};
        const image   = listing.primary_photo?.href || 'https://via.placeholder.com/300x200';
  
        const card = document.createElement('div');
        card.className = 'listing-card';
        card.innerHTML = `
          <img src="${image}" alt="Property Image">
          <h3>${address.line || 'Unknown address'}, ${address.city || ''}, ${address.state_code || ''}</h3>
          <p>Price: ${listing.list_price ? '$' + listing.list_price : 'Not listed'}</p>
          <button class="book-btn" data-id="${listing.property_id}">Book</button>
        `;
        resultsContainer.appendChild(card);
      });
  
      // Attach click handlers to all book buttons
      document.querySelectorAll('.book-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
          const propertyId = btn.getAttribute('data-id');
          const startDate  = checkInInput.value;
          const endDate    = checkOutInput.value;
          if (!startDate || !endDate) {
            alert('Please select check-in and check-out dates before booking.');
            return;
          }
  
          // Example user email; replace or prompt user as needed
          const userEmail = 'test@example.com';
  
          try {
            const resp = await fetch('/api/bookings', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                property_id: propertyId,
                user_email:  userEmail,
                start_date:  startDate,
                end_date:    endDate
              })
            });
            const data = await resp.json();
            if (resp.ok) {
              // Redirect to payment page for this booking
              window.location.href = `/payments/${data.booking.booking_id}`;
            } else {
              alert('Booking failed: ' + (data.error || resp.status));
            }
          } catch (err) {
            console.error('Booking error:', err);
            alert('Booking error: ' + err.message);
          }
        });
      });
    }
  });
  