const apiKey = 'bfb6821e53msh848033d27b1e2d1p186d09jsnb3bc129f7ecb';
let currentPage = 1;
let totalPages = 1;
let currentSearchQuery = "";
let currentHomes = [];

const homeSearch = document.getElementById("movie-search");
movieSearch.addEventListener('keyup', (event) => {
        const { key } = event;
        if (key !== "Enter" && key !== "Backspace" && key !== "Shift" && key !== "Control") {
            currentPage = 1;
            currentSearchQuery += key;
            debounceSearch(currentSearchQuery, currentPage);
        } 
    });

const url = 'https://us-real-estate-listings.p.rapidapi.com/v2/property';
const options = {
	method: 'GET',
	headers: {
		'x-rapidapi-host': 'us-real-estate-listings.p.rapidapi.com'
	}
};

try {
	const response = await fetch(url, options);
	const result = await response.text();
	console.log(result);
} catch (error) {
	console.error(error);
}