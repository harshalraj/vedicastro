document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('astroForm');
    const placeInput = document.getElementById('place');
    const suggestionsBox = document.getElementById('suggestions');
    const latInput = document.getElementById('lat');
    const lonInput = document.getElementById('lon');
    const resultsSection = document.getElementById('results');
    const d1ChartDiv = document.getElementById('d1-chart');
    const moonChartDiv = document.getElementById('moon-chart');
    const userDetailsDiv = document.getElementById('user-details');

    // Manual Entry Elements
    const coordsRow = document.getElementById('coords-row');
    const manualCheckbox = document.getElementById('manual-coords');

    if (manualCheckbox) {
        manualCheckbox.addEventListener('change', () => {
            if (manualCheckbox.checked) {
                coordsRow.classList.remove('hidden');
                placeInput.disabled = true;
                placeInput.value = ''; // Clear place name to avoid confusion
            } else {
                coordsRow.classList.add('hidden');
                placeInput.disabled = false;
            }
        });
    }

    let debounceTimer;

    // Place Autocomplete
    placeInput.addEventListener('input', () => {
        clearTimeout(debounceTimer);
        const query = placeInput.value;
        if (query.length < 1) {
            suggestionsBox.style.display = 'none';
            return;
        }

        debounceTimer = setTimeout(async () => {
            try {
                const res = await fetch(`/suggest_place?q=${query}`);
                const data = await res.json();

                suggestionsBox.innerHTML = '';
                if (data.length > 0) {
                    suggestionsBox.style.display = 'block';
                    data.forEach(place => {
                        const div = document.createElement('div');
                        div.textContent = place.display_name;
                        div.addEventListener('click', () => {
                            placeInput.value = place.display_name;
                            latInput.value = place.lat;
                            lonInput.value = place.lon;
                            suggestionsBox.style.display = 'none';
                        });
                        suggestionsBox.appendChild(div);
                    });
                } else {
                    suggestionsBox.style.display = 'none';
                }
            } catch (err) {
                console.error('Error fetching places:', err);
            }
        }, 300);
    });

    // Hide suggestions on click outside
    document.addEventListener('click', (e) => {
        if (!placeInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
            suggestionsBox.style.display = 'none';
        }
    });

    // Form Submit
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const name = document.getElementById('name').value;
        const dob = document.getElementById('dob').value;
        const tob = document.getElementById('tob').value;
        const lat = latInput.value;
        const lon = lonInput.value;
        const tz = document.getElementById('tz').value;

        if (!lat || !lon) {
            alert("Please select a valid place or enter coordinates manually.");
            return;
        }

        const payload = { name, dob, tob, lat, lon, tz };

        try {
            const res = await fetch('/get_chart', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();

            if (data.error) {
                alert('Error: ' + data.error);
                return;
            }

            renderCharts(data);
            resultsSection.scrollIntoView({ behavior: 'smooth' });

        } catch (err) {
            console.error('Error:', err);
            alert('Failed to generate chart');
        }
    });

    function renderCharts(data) {
        resultsSection.classList.remove('hidden');

        userDetailsDiv.innerHTML = `
            <p><strong>Name:</strong> ${data.details.Name}</p>
            <p><strong>Born:</strong> ${data.details.Date} at ${data.details.Time}</p>
             <p><strong>Ascendant:</strong> ${data.details.Ascendant} | <strong>Moon Sign:</strong> ${data.details['Moon Sign']}</p>
        `;

        // D1 Chart starts with Ascendant Sign
        renderSingleChart(d1ChartDiv, data.d1, data.details.Ascendant);

        // Moon Chart starts with Moon Sign (It becomes the Lagna of Moon Chart)
        renderSingleChart(moonChartDiv, data.moon, data.details['Moon Sign']);

        // Render Table
        renderTable(data.planetary_details);

        // Render Dasha
        renderDashaTable(data.vimshottari);
    }

    function renderTable(details) {
        const tbody = document.querySelector('#planet-table tbody');
        tbody.innerHTML = '';

        details.forEach(planet => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${planet.Planet}</td>
                <td>${planet.Sign}</td>
                <td>${planet.Degree}</td>
                <td>${planet.Nakshatra}</td>
            `;
            tbody.appendChild(tr);
        });
    }

    function renderDashaTable(dashas) {
        const tbody = document.querySelector('#dasha-table tbody');
        tbody.innerHTML = '';

        if (!dashas || dashas.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4">No Dasha data available</td></tr>';
            return;
        }

        dashas.forEach(dasha => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${dasha.Lord}</td>
                <td>${dasha.Start}</td>
                <td>${dasha.End}</td>
                <td>${dasha.Duration}</td>
            `;
            tbody.appendChild(tr);
        });
    }

    function renderSingleChart(container, chartData, ascSignName) {
        // Clear previous content
        const houseDivs = container.querySelectorAll('.house');
        houseDivs.forEach(div => div.innerHTML = '');

        const signsMap = {
            'Aries': 1, 'Taurus': 2, 'Gemini': 3, 'Cancer': 4,
            'Leo': 5, 'Virgo': 6, 'Libra': 7, 'Scorpio': 8,
            'Sagittarius': 9, 'Capricorn': 10, 'Aquarius': 11, 'Pisces': 12
        };

        let startSignNum = signsMap[ascSignName];
        if (!startSignNum) startSignNum = 1; // Fallback

        // Populate
        for (const [houseNum, planets] of Object.entries(chartData)) {
            const div = container.querySelector(`.house-${houseNum}`);
            if (div) {
                // Calculate Sign Number for this house
                // Formula: (StartSign + House - 2) % 12 + 1
                const currentSignNum = (startSignNum + parseInt(houseNum) - 2) % 12 + 1;

                // Add Sign Number Element
                const signSpan = document.createElement('div');
                signSpan.className = 'sign-number';
                signSpan.textContent = currentSignNum;
                div.appendChild(signSpan);

                // Add Planets
                if (planets.length > 0) {
                    planets.forEach(p => {
                        const span = document.createElement('span');
                        span.textContent = p;
                        div.appendChild(span);
                    });
                }
            }
        }
    }
});
