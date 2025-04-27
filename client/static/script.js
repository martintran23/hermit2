document.getElementById('search-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const location = document.getElementById('location-search').value;
  
    try {
      const response = await fetch(`/api/properties?location=${encodeURIComponent(location)}`);
      const data = await response.json();
      console.log("Search Results:", data);
  
      if (response.ok && data.length > 0) {
        displayResults(data);
      } else {
        document.getElementById('results').innerHTML = `<p>No rentals found for "${location}".</p>`;
      }
    } catch (error) {
      console.error("Search error:", error);
      document.getElementById('results').innerHTML = `<p>Error fetching results.</p>`;
    }
  });
  
  function displayResults(listings) {
    const resultsContainer = document.getElementById('results');
    resultsContainer.innerHTML = "";
  
    listings.forEach(listing => {
      const address = listing.location?.address || {};
      const image = listing.primary_photo?.href || "https://via.placeholder.com/300x200";
  
      const card = document.createElement('div');
      card.className = "listing-card";
      card.innerHTML = `
        <img src="${image}" alt="Property Image" width="300">
        <h3>${address.line}, ${address.city}, ${address.state_code}</h3>
      `;
      resultsContainer.appendChild(card);
    });
  }