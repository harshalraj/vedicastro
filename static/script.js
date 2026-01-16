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

    // Analysis Elements
    const btnAnalyze = document.getElementById('btn-analyze');
    const analysisSection = document.getElementById('analysis-section');
    let lastFormData = null; // Store form data for analysis request

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

            // Show Analysis Button and Store Data
            if (btnAnalyze) {
                btnAnalyze.classList.remove('hidden');
                if (analysisSection) analysisSection.classList.add('hidden');
                lastFormData = payload;
            }

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

        // Show Chat Button
        const chatToggleBtn = document.getElementById('chat-toggle-btn');
        if (chatToggleBtn) {
            chatToggleBtn.classList.remove('hidden');
            // Give a little bounce or pulse effect via CSS if desired, or just show it
        }
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

        dashas.forEach((dasha, index) => {
            // Main Row
            const tr = document.createElement('tr');
            tr.className = 'dasha-row';
            tr.style.cursor = 'pointer';

            // Add Expand icon if clickable
            const hasAds = dasha.Antardashas && dasha.Antardashas.length > 0;
            const icon = hasAds ? '▶' : ''; // Simple arrow



            tr.innerHTML = `
                <td style="display: flex; align-items: center; justify-content: flex-start;">
                    <div style="width: 25px; text-align: center; margin-right: 5px;">${icon}</div>
                    <span>${dasha.Lord}</span>
                </td>
                <td>${dasha.Start}</td>
                <td>${dasha.End}</td>
                <td>${dasha.Duration}</td>
            `;
            tbody.appendChild(tr);

            // Antardasha Row (Hidden by default)
            if (hasAds) {
                const adRow = document.createElement('tr');
                adRow.className = 'ad-row hidden';
                adRow.innerHTML = `
                    <td colspan="4" style="background-color: #f9f9f9; padding: 0;">
                        <div style="padding: 10px 20px;">
                            <h5 style="margin: 0 0 10px 0; color: #555;">${dasha.Lord} Antardashas</h5>
                            <table style="width: 100%; font-size: 0.9em; border-collapse: collapse;">
                                <thead style="background: #eee;">
                                    <tr>
                                        <th style="padding:5px; text-align:left;">AD Lord</th>
                                        <th style="padding:5px; text-align:left;">Start</th>
                                        <th style="padding:5px; text-align:left;">End</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${dasha.Antardashas.map(ad => `
                                        <tr style="border-bottom: 1px solid #ddd;">
                                            <td style="padding:5px;">${ad.Lord}</td>
                                            <td style="padding:5px;">${ad.Start}</td>
                                            <td style="padding:5px;">${ad.End}</td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    </td>
                `;
                tbody.appendChild(adRow);

                // Click Event
                tr.addEventListener('click', () => {
                    const isHidden = adRow.classList.contains('hidden');
                    // Find the div that contains the icon
                    const iconDiv = tr.querySelector('td > div');

                    if (isHidden) {
                        adRow.classList.remove('hidden');
                        if (iconDiv) iconDiv.textContent = '▼';
                        tr.style.backgroundColor = '#f0f0f0';
                    } else {
                        adRow.classList.add('hidden');
                        if (iconDiv) iconDiv.textContent = '▶';
                        tr.style.backgroundColor = '';
                    }
                });
            }
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

    // Analysis Button Click
    if (btnAnalyze) {
        btnAnalyze.addEventListener('click', async () => {
            if (!lastFormData) return;

            const originalText = btnAnalyze.textContent;
            btnAnalyze.textContent = "Analyzing...";
            btnAnalyze.disabled = true;

            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(lastFormData)
                });

                if (!response.ok) throw new Error('Analysis failed');
                const data = await response.json();

                renderAnalysis(data);
            } catch (e) {
                alert(e.message);
            } finally {
                btnAnalyze.textContent = originalText;
                btnAnalyze.disabled = false;
            }
        });
    }

    function renderAnalysis(data) {
        if (!analysisSection) return;
        analysisSection.classList.remove('hidden');
        analysisSection.scrollIntoView({ behavior: 'smooth' });

        // Render Yogas
        const yogaList = document.getElementById('yoga-list');
        const noYogas = document.getElementById('no-yogas');
        if (yogaList) {
            yogaList.innerHTML = '';
            if (data.yogas && data.yogas.length > 0) {
                if (noYogas) noYogas.classList.add('hidden');
                data.yogas.forEach(yoga => {
                    const li = document.createElement('li');
                    li.innerHTML = `<strong>${yoga.name}</strong>: ${yoga.desc}`;
                    yogaList.appendChild(li);
                });
            } else {
                if (noYogas) noYogas.classList.remove('hidden');
            }
        }

        // Render Manglik
        const manglikBox = document.getElementById('manglik-status');
        if (manglikBox && data.manglik) {
            const isManglik = data.manglik.status;
            manglikBox.innerHTML = `
                <p style="color: ${isManglik ? '#d32f2f' : '#388e3c'}; font-weight: bold;">
                    ${isManglik ? 'MANGLIK DETECTED' : 'NO MANGLIK DOSHA'}
                </p>
                <p>${data.manglik.desc}</p>
            `;
            manglikBox.style.borderLeft = isManglik ? "4px solid #d32f2f" : "4px solid #388e3c";
            manglikBox.style.paddingLeft = "10px";
            manglikBox.style.backgroundColor = isManglik ? "#ffebee" : "#e8f5e9";
            manglikBox.style.padding = "10px";
            manglikBox.style.borderRadius = "4px";
        }

        // Render Karmic Analysis (Rahu/Ketu)
        const rahuBox = document.getElementById('rahu-purpose');
        const ketuBox = document.getElementById('ketu-karma');

        if (rahuBox && ketuBox && data.karmic_analysis) {
            const r = data.karmic_analysis.rahu;
            const k = data.karmic_analysis.ketu;

            rahuBox.innerHTML = `
                <p><strong>House ${r.house}:</strong> ${r.house_text}</p>
                <p><strong>Star (${r.nakshatra}):</strong> ${r.nakshatra_text}</p>
            `;

            ketuBox.innerHTML = `
                <p><strong>House ${k.house}:</strong> ${k.house_text}</p>
                <p><strong>Star (${k.nakshatra}):</strong> ${k.nakshatra_text}</p>
            `;
        }

        // Render Dasha Prediction
        const dashaBox = document.getElementById('dasha-prediction');
        if (dashaBox && data.dasha_prediction) {
            const dp = data.dasha_prediction;
            dashaBox.innerHTML = `
                <p><strong>Running Mahadasha:</strong> ${dp.current_lord}</p>
                <p><strong>Period:</strong> ${dp.period}</p>
                <p><em>${dp.prediction}</em></p>
            `;
        }

        // Render Nakshatra Analysis
        const nakBox = document.getElementById('nakshatra-analysis');
        if (nakBox && data.nakshatra_analysis) {
            nakBox.innerHTML = `
                <p><strong>Star:</strong> ${data.nakshatra_analysis.nakshatra}</p>
                <p>${data.nakshatra_analysis.traits}</p>
            `;
        }

        // Render House Analysis
        const houseList = document.getElementById('house-analysis-list');
        if (houseList && data.house_analysis) {
            houseList.innerHTML = '';
            data.house_analysis.forEach(item => {
                const div = document.createElement('div');
                div.className = 'analysis-item';
                div.innerHTML = `<strong>${item.planet} in House ${item.house} (${item.sign})</strong>: ${item.text}`;
                houseList.appendChild(div);
            });
        }
    }

    // ---------------------------------------------------------
    // Chat Widget Logic
    // ---------------------------------------------------------
    const chatToggleBtn = document.getElementById('chat-toggle-btn');
    const chatWidget = document.getElementById('chat-widget');
    const chatCloseBtn = document.getElementById('chat-close-btn');
    const chatInput = document.getElementById('chat-input');
    const chatSendBtn = document.getElementById('chat-send-btn');
    const chatMessages = document.getElementById('chat-messages');

    // Toggle Chat Window
    if (chatToggleBtn && chatWidget) {
        chatToggleBtn.addEventListener('click', () => {
            chatWidget.classList.remove('hidden');
            chatToggleBtn.classList.add('hidden');
            // Focus input
            setTimeout(() => {
                if (chatInput) chatInput.focus();
            }, 100);
        });
    }

    if (chatCloseBtn && chatWidget) {
        chatCloseBtn.addEventListener('click', () => {
            chatWidget.classList.add('hidden');
            if (chatToggleBtn) chatToggleBtn.classList.remove('hidden');
        });
    }

    // Send Message Logic
    if (chatSendBtn) {
        chatSendBtn.addEventListener('click', sendMessage);
    }
    if (chatInput) {
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
    }

    async function sendMessage() {
        const question = chatInput.value.trim();
        if (!question) return;

        // Display User Message
        appendMessage('user', question);
        chatInput.value = '';

        // Display Loading
        const loadingId = appendMessage('bot', 'Analyzing stars...');

        try {
            if (!lastFormData) {
                updateMessage(loadingId, "Please generate your birth chart first!");
                return;
            }

            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    question: question,
                    chart_params: lastFormData
                })
            });

            const data = await response.json();

            if (data.error) {
                updateMessage(loadingId, "Error: " + data.error);
            } else {
                // Formatting
                let formattedAnswer = data.answer || "I am speechless.";
                formattedAnswer = formattedAnswer.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
                formattedAnswer = formattedAnswer.replace(/\n\n/g, '<br><br>');
                formattedAnswer = formattedAnswer.replace(/\n/g, '<br>');

                updateMessage(loadingId, formattedAnswer);
            }
        } catch (err) {
            console.error(err);
            updateMessage(loadingId, "Sorry, the stars are silent right now. (Connection Error)");
        }
    }

    function appendMessage(sender, text) {
        if (!chatMessages) return null;
        const div = document.createElement('div');
        div.className = `message ${sender}`;
        div.innerHTML = text;
        chatMessages.appendChild(div);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return div;
    }

    function updateMessage(msgDiv, newText) {
        if (msgDiv) {
            msgDiv.innerHTML = newText;
            if (chatMessages) chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

});
