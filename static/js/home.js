const CSV_FILE_PATH = '/static/Exoplanets%20names.csv'; 

let exoplanets = [];
let dataLoaded = false;

const searchInput = document.getElementById('searchInput');
const exoplanetList = document.getElementById('exoplanetList');
const errorDiv = document.getElementById('error');

// Loading Indicator
const loadingIndicator = document.createElement('div');
loadingIndicator.textContent = 'Loading exoplanet data...';
loadingIndicator.style.textAlign = 'center';
document.querySelector('.search').insertBefore(loadingIndicator, exoplanetList);

// Fetch and Parse Exoplanet Data
function fetchExoplanetData() {
    fetch(CSV_FILE_PATH)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.text();
        })
        .then(data => {
            console.log('CSV file successfully fetched');
            parseCSVData(data);
        })
        .catch(error => {
            console.error('Error fetching the CSV file:', error);
            loadingIndicator.textContent = `Error loading exoplanet data: ${error.message}. Please check the console and file path.`;
        });
}

// Parse CSV Data
function parseCSVData(data) {
    // Remove comment lines and parse CSV data
    const cleanedData = data.split('\n').filter(line => !line.startsWith('#')).join('\n');

    Papa.parse(cleanedData, {
        header: false,
        dynamicTyping: true,
        complete: (results) => {
            handleParseResults(results);
        },
        error: (error) => {
            console.error('Papa Parse error:', error);
            loadingIndicator.textContent = 'Error parsing exoplanet data. Please check the console.';
        }
    });
}

// Handle Parsed Results
function handleParseResults(results) {
    console.log('Papa Parse results:', results);
    if (results.errors.length > 0) {
        console.warn('Papa Parse errors:', results.errors);
    }

    // Process the data
    exoplanets = results.data
        .flat()
        .filter(name => name && typeof name === 'string' && name.trim() !== '')
        .map(name => ({ name: name.trim() }));

    dataLoaded = true;
    loadingIndicator.style.display = 'none';
    console.log(`Exoplanet data loaded. Total exoplanets: ${exoplanets.length}`);

    // Enable search input
    searchInput.disabled = false;
    searchInput.placeholder = "Search for an exoplanet...";

    // Initial state: Hide the list
    exoplanetList.style.display = 'none'; // Ensure the list is hidden initially
}

// Filter Exoplanets Based on Search Query
function filterExoplanets() {
    const searchQuery = searchInput.value.toLowerCase();
    exoplanetList.innerHTML = ''; // Clear the list

    const filteredExoplanets = exoplanets.filter(exoplanet =>
        exoplanet.name.toLowerCase().includes(searchQuery)
    );

    if (filteredExoplanets.length === 0) {
        errorDiv.textContent = 'No exoplanets found';
        errorDiv.style.display = 'block';
        exoplanetList.style.display = 'none';
    } else {
        errorDiv.style.display = 'none';
        exoplanetList.style.display = 'block';
        filteredExoplanets.forEach((exoplanet) => {
            const li = document.createElement('li');
            li.textContent = exoplanet.name;
            li.addEventListener('click', () => handleSelect(exoplanet));
            exoplanetList.appendChild(li);
        });
    }
}

// Handle Exoplanet Selection
function handleSelect(exoplanet) {
    console.log('Selected exoplanet:', exoplanet);
    alert(`You selected ${exoplanet.name}`);
    exoplanetList.style.display = 'none';
}

// Event Listeners
searchInput.addEventListener('input', filterExoplanets);
searchInput.addEventListener('focus', filterExoplanets);
searchInput.addEventListener('blur', () => {
    setTimeout(() => {
        exoplanetList.style.display = 'none'; // Hide the list after a short delay
    }, 100); // Delay allows for click events to be registered
});

// Fetch exoplanet data when the script loads
fetchExoplanetData();
