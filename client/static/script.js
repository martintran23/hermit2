const apiKey = 'bfb6821e53msh848033d27b1e2d1p186d09jsnb3bc129f7ecb';
let currentPage = 1;
let totalPages = 1;
let currentSearchQuery = "";
let currentHomes = [];

const homeSearch = document.getElementById("home-search");
homeSearch.addEventListener('keyup', (event) => {
    const { key } = event;
    if (key !== "Enter" && key !== "Backspace" && key !== "Shift" && key !== "Control") {
        currentPage = 1;
        currentSearchQuery += key;
        debounceSearch(currentSearchQuery, currentPage);
    }
});

// Correct URL
const baseUrl = 'https://us-real-estate-listings.p.rapidapi.com/for-rent';

async function fetchRentals(query = "", page = 1) {
    const url = `${baseUrl}?location=${query}&page=${page}`;
    const options = {
        method: 'GET',
        headers: {
            'X-RapidAPI-Key': apiKey,
            'X-RapidAPI-Host': 'us-real-estate-listings.p.rapidapi.com'
        }
    };

    try {
        const response = await fetch(url, options);
        const result = await response.json();
        console.log(result);
    } catch (error) {
        console.error("Error fetching rentals:", error);
    }
}


let debounceTimer;
function debounceSearch(query, page) {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
        fetchRentals(query, page);
    }, 500); 
}