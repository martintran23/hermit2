document.getElementById('search-form').addEventListener('submit', async (e) => {
  e.preventDefault(); // Stop form from reloading page

  const location = document.getElementById('location-search').value;
  const checkInDate = document.getElementById('check-in').value;
  const checkOutDate = document.getElementById('check-out').value;

  if (checkInDate && checkOutDate && new Date(checkOutDate) <= new Date(checkInDate)) {
    alert("Check-out date must be after check-in date!");
    return; // Stop if invalid
  }

  try {
    const response = await fetch(`/api/properties?location=${encodeURIComponent(location)}`);
    const listings = await response.json();

    if (response.ok && listings.length > 0) {
      displayResults(listings);
    } else {
      document.getElementById('results').innerHTML = `<p>No rentals found for "${location}".</p>`;
    }
  } catch (error) {
    console.error("Error fetching properties:", error);
    document.getElementById('results').innerHTML = `<p>Error fetching results.</p>`;
  }
});

function displayResults(listings) {
  const resultsContainer = document.getElementById('results');
  resultsContainer.innerHTML = ""; // Clear old results

  listings.forEach(listing => {
    const address = listing.location?.address || {};
    const image = listing.primary_photo?.href || "https://via.placeholder.com/300x200";

    const card = document.createElement('div');
    card.className = "listing-card";
    card.innerHTML = `
      <img src="${image}" alt="Property Image" width="300">
      <h3>${address.line}, ${address.city}, ${address.state_code}</h3>
      <p>Price: ${listing.list_price ? `$${listing.list_price}` : "Not listed"}</p>
    `;
    resultsContainer.appendChild(card);
  });
}