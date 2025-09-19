// API Configuration
let API_BASE_URL = '/api'; // Use relative paths when served from same server

// If we're on a different port (development), use absolute URLs
if (window.location.port === '8080') {
    // Auto-detect GitHub Codespace environment and adjust the backend URL
    if (window.location.hostname.includes('app.github.dev')) {
        const currentURL = window.location.href;
        API_BASE_URL = currentURL.replace('-8080.app.github.dev', '-5000.app.github.dev').replace(/\/[^\/]*$/, '') + '/api';
    } else {
        // Local development
        API_BASE_URL = 'http://localhost:5000/api';
    }
} else if (window.location.port === '5000') {
    // Running on integrated server
    if (window.location.hostname.includes('app.github.dev')) {
        // GitHub Codespace - use full URL to ensure proper routing
        API_BASE_URL = window.location.origin + '/api';
    } else {
        // Local development
        API_BASE_URL = '/api';
    }
}

console.log('Frontend URL:', window.location.href);
console.log('Backend API URL:', API_BASE_URL);

// Global variables
let currentLanguage = 'en';
let isLoading = false;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    setupEventListeners();
    testAPIConnection(); // Add API connection test
    loadDiseases();
    loadEmergencyContacts();
}

// Test API connection on startup
async function testAPIConnection() {
    try {
        console.log('Testing API connection to:', API_BASE_URL);
        const response = await fetch(`${API_BASE_URL}`);
        const data = await response.json();
        console.log('✅ API Connection successful:', data);
        
        // Show connection status in the chat
        const connectionStatus = document.createElement('div');
        connectionStatus.innerHTML = `
            <div style="background: #d4edda; border: 1px solid #c3e6cb; color: #155724; padding: 1rem; border-radius: 8px; margin: 1rem;">
                <i class="fas fa-check-circle"></i> Connected to AI Medical Assistant API
                <br><small>Backend: ${API_BASE_URL}</small>
            </div>
        `;
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.appendChild(connectionStatus);
        
    } catch (error) {
        console.error('❌ API Connection failed:', error);
        
        // Show connection error in the chat
        const connectionError = document.createElement('div');
        connectionError.innerHTML = `
            <div style="background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; padding: 1rem; border-radius: 8px; margin: 1rem;">
                <i class="fas fa-exclamation-triangle"></i> Unable to connect to backend API
                <br><small>Trying: ${API_BASE_URL}</small>
                <br><small>Error: ${error.message}</small>
            </div>
        `;
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.appendChild(connectionError);
    }
}

function setupEventListeners() {
    // Tab navigation
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });

    // Chat functionality
    const sendButton = document.getElementById('sendButton');
    const messageInput = document.getElementById('messageInput');
    
    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    // Symptom checker
    const checkSymptomsBtn = document.getElementById('checkSymptomsBtn');
    checkSymptomsBtn.addEventListener('click', checkSymptoms);

    // Disease search
    const searchDiseaseBtn = document.getElementById('searchDiseaseBtn');
    const diseaseSearch = document.getElementById('diseaseSearch');
    
    searchDiseaseBtn.addEventListener('click', searchDiseases);
    diseaseSearch.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') searchDiseases();
    });

    // Language selection
    const languageSelect = document.getElementById('languageSelect');
    languageSelect.addEventListener('change', (e) => {
        currentLanguage = e.target.value;
    });
}

function switchTab(tabName) {
    // Hide all tabs
    const tabs = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => tab.classList.remove('active'));

    // Remove active class from all buttons
    const buttons = document.querySelectorAll('.tab-btn');
    buttons.forEach(btn => btn.classList.remove('active'));

    // Show selected tab
    document.getElementById(tabName).classList.add('active');
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
}

// Chat functionality
function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim();
    
    if (!message || isLoading) return;
    
    addMessageToChat(message, 'user');
    messageInput.value = '';
    
    // Send to backend
    sendToBot(message);
}

function sendQuickMessage(message) {
    addMessageToChat(message, 'user');
    sendToBot(message);
}

function addMessageToChat(message, sender) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    
    if (typeof message === 'string') {
        content.innerHTML = `<p>${message}</p>`;
    } else {
        content.appendChild(message);
    }
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function sendToBot(message) {
    showLoading();
    
    try {
        console.log('Sending request to:', `${API_BASE_URL}/chat`);
        console.log('Message:', message);
        
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                language: currentLanguage
            })
        });
        
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Response data:', data);
        displayBotResponse(data.response);
        
    } catch (error) {
        console.error('Error details:', error);
        displayErrorMessage(`Connection error: ${error.message}. Please check if the backend server is running.`);
    }
    
    hideLoading();
}

function displayBotResponse(response) {
    const content = document.createElement('div');
    
    // Display main message with HTML rendering for colored headings
    const messageP = document.createElement('p');
    messageP.innerHTML = response.message;
    content.appendChild(messageP);
    
    // Handle different response types
    if (response.type === 'emergency') {
        const emergencyDiv = document.createElement('div');
        emergencyDiv.className = 'emergency-response';
        emergencyDiv.innerHTML = `
            <div style="background: #dc3545; color: white; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
                <h4><i class="fas fa-exclamation-triangle"></i> Emergency Contacts</h4>
                <p><strong>Ambulance:</strong> ${response.emergency_contacts.ambulance}</p>
                <p><strong>Police:</strong> ${response.emergency_contacts.police}</p>
                <p><strong>Fire:</strong> ${response.emergency_contacts.fire}</p>
            </div>
        `;
        content.appendChild(emergencyDiv);
    }
    
    if (response.type === 'symptom_analysis' && response.possible_diseases) {
        const symptomsDiv = document.createElement('div');
        symptomsDiv.innerHTML = '<h4>Possible Conditions:</h4>';
        
        response.possible_diseases.forEach(disease => {
            const diseaseDiv = document.createElement('div');
            diseaseDiv.style.cssText = 'background: #f8f9fa; padding: 1rem; margin: 0.5rem 0; border-radius: 8px; border-left: 4px solid #2c5aa0;';
            diseaseDiv.innerHTML = `
                <strong>${disease.disease}</strong>
                <span style="float: right; background: #28a745; color: white; padding: 0.2rem 0.5rem; border-radius: 10px; font-size: 0.8rem;">
                    ${disease.confidence}% match
                </span>
            `;
            symptomsDiv.appendChild(diseaseDiv);
        });
        
        const disclaimerP = document.createElement('p');
        disclaimerP.innerHTML = `<small><i class="fas fa-exclamation-triangle"></i> ${response.disclaimer}</small>`;
        disclaimerP.style.cssText = 'background: rgba(255, 193, 7, 0.1); border: 1px solid rgba(255, 193, 7, 0.3); padding: 0.8rem; border-radius: 8px; margin-top: 1rem;';
        symptomsDiv.appendChild(disclaimerP);
        
        content.appendChild(symptomsDiv);
    }
    
    if (response.type === 'disease_info' && response.disease) {
        const diseaseInfo = response.disease;
        const diseaseDiv = document.createElement('div');
        diseaseDiv.innerHTML = `
            <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 12px; margin: 1rem 0;">
                <h4 style="color: #2c5aa0; margin-bottom: 1rem;">${diseaseInfo.name}</h4>
                <p><strong>Description:</strong> ${diseaseInfo.description || 'Information about this condition.'}</p>
                
                <div style="margin: 1rem 0;">
                    <h5><i class="fas fa-list"></i> Common Symptoms:</h5>
                    <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
                        ${diseaseInfo.symptoms.slice(0, 5).map(symptom => `<li>${symptom}</li>`).join('')}
                    </ul>
                </div>
                
                <div style="margin: 1rem 0;">
                    <h5><i class="fas fa-shield-alt"></i> Prevention:</h5>
                    <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
                        ${diseaseInfo.prevention.slice(0, 3).map(tip => `<li>${tip}</li>`).join('')}
                    </ul>
                </div>
            </div>
        `;
        content.appendChild(diseaseDiv);
    }
    
    addMessageToChat(content, 'bot');
}

function displayErrorMessage(message) {
    const errorContent = document.createElement('div');
    errorContent.innerHTML = `
        <p style="color: #dc3545;"><i class="fas fa-exclamation-circle"></i> ${message}</p>
    `;
    addMessageToChat(errorContent, 'bot');
}

// Symptom checker functionality
async function checkSymptoms() {
    const symptomsInput = document.getElementById('symptomsInput');
    const symptoms = symptomsInput.value.trim();
    
    if (!symptoms) {
        alert('Please describe your symptoms');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/symptoms-check`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ symptoms: symptoms })
        });
        
        const data = await response.json();
        displaySymptomsResults(data);
        
    } catch (error) {
        console.error('Error:', error);
        displaySymptomsError();
    }
    
    hideLoading();
}

function displaySymptomsResults(data) {
    const resultsContainer = document.getElementById('symptomsResults');
    
    if (data.possible_conditions && data.possible_conditions.length > 0) {
        let html = `
            <h3>Analysis Results</h3>
            <p><strong>Symptoms:</strong> ${data.symptoms}</p>
            <div class="conditions-list">
        `;
        
        data.possible_conditions.forEach(condition => {
            html += `
                <div class="condition-card">
                    <div class="condition-header">
                        <span class="condition-name">${condition.disease}</span>
                        <span class="confidence-badge">${condition.confidence}% match</span>
                    </div>
                    <p>Matched ${condition.matched_symptoms} symptoms</p>
                </div>
            `;
        });
        
        html += `
            </div>
            <div class="disclaimer">
                <i class="fas fa-exclamation-triangle"></i>
                <strong>Disclaimer:</strong> ${data.disclaimer}
            </div>
            <div style="margin-top: 1rem; padding: 1rem; background: #e3f2fd; border-radius: 8px;">
                <p><strong>Recommendation:</strong> ${data.recommendation}</p>
            </div>
        `;
        
        resultsContainer.innerHTML = html;
    } else {
        resultsContainer.innerHTML = `
            <div style="text-align: center; padding: 2rem;">
                <i class="fas fa-search" style="font-size: 3rem; color: #ccc; margin-bottom: 1rem;"></i>
                <p>No specific conditions identified based on the symptoms provided.</p>
                <p>Please consult a healthcare professional for proper evaluation.</p>
            </div>
        `;
    }
}

function displaySymptomsError() {
    const resultsContainer = document.getElementById('symptomsResults');
    resultsContainer.innerHTML = `
        <div style="text-align: center; padding: 2rem; color: #dc3545;">
            <i class="fas fa-exclamation-circle" style="font-size: 3rem; margin-bottom: 1rem;"></i>
            <p>Sorry, there was an error processing your symptoms.</p>
            <p>Please try again or consult a healthcare professional.</p>
        </div>
    `;
}

// Disease information functionality
async function loadDiseases() {
    try {
        const response = await fetch(`${API_BASE_URL}/diseases`);
        const data = await response.json();
        displayDiseases(data.diseases);
    } catch (error) {
        console.error('Error loading diseases:', error);
    }
}

function displayDiseases(diseases) {
    const diseasesList = document.getElementById('diseasesList');
    
    const html = diseases.map(disease => `
        <div class="disease-card" onclick="loadDiseaseDetails('${disease.id}')">
            <h3>${disease.name}</h3>
            <p>Click to learn more about symptoms, prevention, and treatment.</p>
            <span class="symptoms-count">${disease.symptoms_count} symptoms</span>
        </div>
    `).join('');
    
    diseasesList.innerHTML = html;
}

async function loadDiseaseDetails(diseaseId) {
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/disease/${diseaseId}`);
        const data = await response.json();
        
        if (data.success) {
            displayDiseaseDetails(data.disease);
        }
    } catch (error) {
        console.error('Error loading disease details:', error);
    }
    
    hideLoading();
}

function displayDiseaseDetails(disease) {
    const detailsContainer = document.getElementById('diseaseDetails');
    
    const html = `
        <h2>${disease.name}</h2>
        <p style="font-size: 1.1rem; color: #666; margin-bottom: 2rem;">${disease.description}</p>
        
        <div class="detail-section">
            <h3><i class="fas fa-list"></i> Symptoms</h3>
            <ul>
                ${disease.symptoms.map(symptom => `<li>${symptom}</li>`).join('')}
            </ul>
        </div>
        
        <div class="detail-section">
            <h3><i class="fas fa-search"></i> Causes</h3>
            <ul>
                ${disease.causes.map(cause => `<li>${cause}</li>`).join('')}
            </ul>
        </div>
        
        <div class="detail-section">
            <h3><i class="fas fa-shield-alt"></i> Prevention</h3>
            <ul>
                ${disease.prevention.map(tip => `<li>${tip}</li>`).join('')}
            </ul>
        </div>
        
        <div class="detail-section">
            <h3><i class="fas fa-medkit"></i> Treatment</h3>
            <ul>
                ${disease.treatment.map(treatment => `<li>${treatment}</li>`).join('')}
            </ul>
        </div>
        
        <div class="detail-section">
            <h3><i class="fas fa-exclamation-triangle" style="color: #dc3545;"></i> Emergency Signs</h3>
            <ul>
                ${disease.emergency_signs.map(sign => `<li style="border-left-color: #dc3545;">${sign}</li>`).join('')}
            </ul>
            <div style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                <strong>⚠️ If you experience any of these emergency signs, seek immediate medical attention!</strong>
            </div>
        </div>
    `;
    
    detailsContainer.innerHTML = html;
    detailsContainer.scrollIntoView({ behavior: 'smooth' });
}

async function searchDiseases() {
    const searchTerm = document.getElementById('diseaseSearch').value.trim().toLowerCase();
    
    if (!searchTerm) {
        loadDiseases();
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/diseases`);
        const data = await response.json();
        
        const filteredDiseases = data.diseases.filter(disease => 
            disease.name.toLowerCase().includes(searchTerm) ||
            disease.id.toLowerCase().includes(searchTerm)
        );
        
        displayDiseases(filteredDiseases);
        
        if (filteredDiseases.length === 0) {
            document.getElementById('diseasesList').innerHTML = `
                <div style="text-align: center; padding: 2rem; grid-column: 1 / -1;">
                    <i class="fas fa-search" style="font-size: 3rem; color: #ccc; margin-bottom: 1rem;"></i>
                    <p>No diseases found matching "${searchTerm}"</p>
                    <button onclick="loadDiseases()" style="margin-top: 1rem; padding: 0.5rem 1rem; background: #2c5aa0; color: white; border: none; border-radius: 8px; cursor: pointer;">
                        Show All Diseases
                    </button>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error searching diseases:', error);
    }
}

// Emergency contacts functionality
async function loadEmergencyContacts() {
    try {
        const response = await fetch(`${API_BASE_URL}/emergency`);
        const data = await response.json();
        // Emergency contacts are already in the HTML, but we could update them dynamically here
    } catch (error) {
        console.error('Error loading emergency contacts:', error);
    }
}

function callNumber(number) {
    if (confirm(`Do you want to call ${number}?`)) {
        window.location.href = `tel:${number}`;
    }
}

// Utility functions
function showLoading() {
    isLoading = true;
    document.getElementById('loadingSpinner').classList.add('show');
}

function hideLoading() {
    isLoading = false;
    document.getElementById('loadingSpinner').classList.remove('show');
}

// Health tips functionality (bonus feature)
async function loadHealthTips() {
    try {
        const response = await fetch(`${API_BASE_URL}/health-tips`);
        const data = await response.json();
        return data.health_tips;
    } catch (error) {
        console.error('Error loading health tips:', error);
        return [];
    }
}

// Voice input functionality (future enhancement)
function startVoiceInput() {
    if ('webkitSpeechRecognition' in window) {
        const recognition = new webkitSpeechRecognition();
        recognition.language = currentLanguage;
        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            document.getElementById('messageInput').value = transcript;
        };
        recognition.start();
    } else {
        alert('Voice input is not supported in your browser');
    }
}

// Nearby Hospitals Functionality
let userLocation = null;

function getUserLocation() {
    if (navigator.geolocation) {
        document.getElementById('loadingHospitals').style.display = 'block';
        navigator.geolocation.getCurrentPosition(
            function(position) {
                userLocation = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };
                
                // Update location input with coordinates
                document.getElementById('locationInput').value = `Current Location (${userLocation.lat.toFixed(4)}, ${userLocation.lng.toFixed(4)})`;
                
                // Search for nearby hospitals
                searchNearbyHospitals(userLocation);
                
                document.getElementById('loadingHospitals').style.display = 'none';
            },
            function(error) {
                document.getElementById('loadingHospitals').style.display = 'none';
                alert('Unable to get your location. Please enter your address manually.');
                console.error('Geolocation error:', error);
            }
        );
    } else {
        alert('Geolocation is not supported by this browser.');
    }
}

function searchHospitals() {
    const location = document.getElementById('locationInput').value;
    if (!location.trim()) {
        alert('Please enter a location or use "Use My Location"');
        return;
    }
    
    document.getElementById('loadingHospitals').style.display = 'block';
    
    // Simulate location-based search
    setTimeout(() => {
        generateLocationBasedHospitals(location);
        document.getElementById('loadingHospitals').style.display = 'none';
    }, 1500);
}

function searchNearbyHospitals(location) {
    // Simulate finding hospitals near the location
    const sampleHospitals = [
        {
            name: "Apollo Hospitals",
            address: "Plot No 251, Sainik School Road, Unit 15",
            phone: "+91 9876543210",
            distance: 1.2,
            type: "Emergency",
            services: ["Emergency", "ICU", "Surgery", "Cardiology", "OPD"],
            rating: 4.5,
            reviews: 342
        },
        {
            name: "AIIMS Medical Center",
            address: "Ansari Nagar, Near AIIMS Metro Station",
            phone: "+91 9876543211",
            distance: 2.1,
            type: "Government",
            services: ["Emergency", "OPD", "Surgery", "Pediatrics"],
            rating: 4.3,
            reviews: 567
        },
        {
            name: "Max Super Speciality Hospital",
            address: "1, Press Enclave Road, Saket",
            phone: "+91 9876543212",
            distance: 3.5,
            type: "Multi-Specialty",
            services: ["Emergency", "Oncology", "Neurology", "Orthopedics"],
            rating: 4.6,
            reviews: 289
        },
        {
            name: "Fortis Healthcare",
            address: "Sector 62, Near Metro Station",
            phone: "+91 9876543213",
            distance: 4.2,
            type: "Emergency",
            services: ["Emergency", "ICU", "Trauma", "Surgery"],
            rating: 4.4,
            reviews: 198
        }
    ];
    
    displayHospitals(sampleHospitals);
}

function generateLocationBasedHospitals(locationText) {
    // Generate contextual hospital names based on location
    const locationName = locationText.split(',')[0].split(' ')[0];
    const hospitals = [
        {
            name: `${locationName} Medical Center`,
            address: `Near ${locationText}`,
            phone: "+91 9876543210",
            distance: 0.8,
            type: "Emergency",
            services: ["Emergency", "ICU", "Surgery"],
            rating: 4.3,
            reviews: 156
        },
        {
            name: `${locationName} General Hospital`,
            address: `${locationText} Area`,
            phone: "+91 9876543211",
            distance: 1.5,
            type: "General",
            services: ["OPD", "Diagnostic", "Pharmacy"],
            rating: 4.1,
            reviews: 89
        },
        {
            name: `City Hospital ${locationName}`,
            address: `Main Road, ${locationText}`,
            phone: "+91 9876543212",
            distance: 2.3,
            type: "Multi-Specialty",
            services: ["Emergency", "Cardiology", "Neurology"],
            rating: 4.5,
            reviews: 234
        }
    ];
    
    displayHospitals(hospitals);
}

function displayHospitals(hospitals) {
    const hospitalsList = document.getElementById('hospitalsList');
    
    // Clear existing results except sample card
    const existingCards = hospitalsList.querySelectorAll('.hospital-card:not(.sample)');
    existingCards.forEach(card => card.remove());
    
    hospitals.forEach(hospital => {
        const hospitalCard = document.createElement('div');
        hospitalCard.className = 'hospital-card';
        const isEmergency = hospital.type === 'Emergency';
        const estimatedTime = Math.ceil(hospital.distance * 2); // 2 min per km
        
        hospitalCard.innerHTML = `
            <div class="hospital-header">
                <h3><i class="fas fa-hospital"></i> ${hospital.name}</h3>
                <span class="hospital-type ${isEmergency ? 'emergency' : ''}">${hospital.type}</span>
            </div>
            <div class="hospital-info">
                <p><i class="fas fa-map-marker-alt"></i> ${hospital.address}</p>
                <p><i class="fas fa-phone"></i> ${hospital.phone}</p>
                <p><i class="fas fa-route"></i> ${hospital.distance} km • ~${estimatedTime} min drive</p>
                <p><i class="fas fa-star"></i> ⭐ ${hospital.rating} (${hospital.reviews} reviews)</p>
                <div class="hospital-services">
                    ${hospital.services.map(service => `<span class="service-tag ${service === 'Emergency' ? 'emergency' : ''}">${service}</span>`).join('')}
                </div>
            </div>
            <div class="hospital-actions">
                <button onclick="getDirections('${hospital.name}', '${hospital.address}')" class="directions-btn">
                    <i class="fas fa-directions"></i> Get Directions
                </button>
                <button onclick="callHospital('${hospital.phone}')" class="call-btn">
                    <i class="fas fa-phone"></i> Call Hospital
                </button>
            </div>
        `;
        
        hospitalsList.appendChild(hospitalCard);
    });
}

function getDirections(name, address) {
    // Open Google Maps with directions
    const query = encodeURIComponent(`${name} ${address}`);
    const url = `https://www.google.com/maps/search/${query}`;
    window.open(url, '_blank');
}

function callHospital(phoneNumber) {
    if (confirm(`Do you want to call ${phoneNumber}?`)) {
        window.location.href = `tel:${phoneNumber}`;
    }
}