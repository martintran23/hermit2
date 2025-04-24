const apiKey = 'bfb6821e53msh848033d27b1e2d1p186d09jsnb3bc129f7ecb';
const searchInput = document.getElementById("location-search");

searchInput.addEventListener('keyup', (event) => {
    const key = event.key;
    if (key === "Enter") {
        const location = searchInput.value;
        if (location) {
            searchProperties(location);
        }
    }
});

async function searchProperties(location) {
    const url = `https://us-real-estate-listings.p.rapidapi.com/for-rent?location=${encodeURIComponent(location)}&limit=5&offset=0`;
    
    const options = {
        method: 'GET',
        headers: {
            'X-RapidAPI-Key': apiKey,
            'X-RapidAPI-Host': 'us-real-estate-listings.p.rapidapi.com'
        }
    };

    try {
        const response = await fetch(url, options);
        const data = await response.json();
        console.log("Search Results:", data);

        if (data.listings && data.listings.length > 0) {
            displayResults(data.listings);
        } else {
            alert("No rentals found for this location.");
        }

    } catch (error) {
        console.error("Error fetching properties:", error);
    }
}

function displayResults(listings) {
    const resultsContainer = document.getElementById("results");
    resultsContainer.innerHTML = "";

    listings.forEach(listing => {
        const address = listing.location?.address || {};
        const card = document.createElement("div");
        card.className = "listing-card";
        card.innerHTML = `
            <h3>${address.line}, ${address.city}, ${address.state_code} ${address.postal_code}</h3>
            <p>Price: ${listing.list_price ? `$${listing.list_price}` : "Not listed"}</p>
            <a href="${listing.href}" target="_blank">View Details</a>
        `;
        resultsContainer.appendChild(card);
    });
}