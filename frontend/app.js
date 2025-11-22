// AgriAssist AI - Frontend JavaScript

const API_BASE = 'http://localhost:5000/api';
let currentLanguage = 'en';
let sessionId = generateSessionId();

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeTabs();
    initializeImageUpload();
    initializeChat();
    initializeTips();
    initializeLanguageToggle();
});

// Tab Management
function initializeTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.dataset.tab;

            // Remove active class from all
            tabBtns.forEach(b => b.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));

            // Add active to clicked
            btn.classList.add('active');
            document.getElementById(targetTab).classList.add('active');
        });
    });
}

// Image Upload
function initializeImageUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const imageInput = document.getElementById('imageInput');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const removeBtn = document.getElementById('removeImage');

    uploadArea.addEventListener('click', () => imageInput.click());

    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.background = '#d5f4e6';
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.style.background = '#ecf0f1';
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith('image/')) {
            handleImageSelect(file);
        }
    });

    imageInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            handleImageSelect(file);
        }
    });

    removeBtn.addEventListener('click', () => {
        imageInput.value = '';
        document.getElementById('imagePreview').style.display = 'none';
        document.getElementById('uploadArea').style.display = 'block';
        analyzeBtn.disabled = true;
    });

    analyzeBtn.addEventListener('click', analyzeCrop);
}

function handleImageSelect(file) {
    const preview = document.getElementById('imagePreview');
    const previewImg = document.getElementById('previewImg');
    const uploadArea = document.getElementById('uploadArea');
    const analyzeBtn = document.getElementById('analyzeBtn');

    const reader = new FileReader();
    reader.onload = (e) => {
        previewImg.src = e.target.result;
        uploadArea.style.display = 'none';
        preview.style.display = 'block';
        analyzeBtn.disabled = false;
    };
    reader.readAsDataURL(file);
}

async function analyzeCrop() {
    const imageInput = document.getElementById('imageInput');
    const location = document.getElementById('location').value || 'Kenya';
    const resultsSection = document.getElementById('analysisResults');
    const resultsContent = document.getElementById('resultsContent');

    if (!imageInput.files[0]) {
        alert('Please select an image first');
        return;
    }

    showLoading(true);

    try {
        const formData = new FormData();
        formData.append('image', imageInput.files[0]);
        formData.append('location', location);
        formData.append('language', currentLanguage);

        const response = await fetch(`${API_BASE}/analyze-crop`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            resultsContent.innerHTML = formatAnalysis(data.analysis);
            resultsSection.style.display = 'block';
            resultsSection.scrollIntoView({ behavior: 'smooth' });
        } else {
            alert('Analysis failed: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to analyze image. Please try again.');
    } finally {
        showLoading(false);
    }
}

function formatAnalysis(analysisData) {
    const analysis = analysisData.analysis || analysisData;
    
    // Convert markdown-style formatting to HTML
    let formatted = analysis
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>');
    
    return `<div class="analysis-text"><p>${formatted}</p></div>`;
}

// Chat Functionality
function initializeChat() {
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');

    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
}

async function sendMessage() {
    const chatInput = document.getElementById('chatInput');
    const message = chatInput.value.trim();

    if (!message) return;

    // Add user message to chat
    addMessageToChat(message, 'user');
    chatInput.value = '';

    showLoading(true);

    try {
        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                session_id: sessionId,
                language: currentLanguage
            })
        });

        const data = await response.json();

        if (data.success) {
            addMessageToChat(data.response, 'bot');
        } else {
            addMessageToChat('Sorry, I encountered an error. Please try again.', 'bot');
        }
    } catch (error) {
        console.error('Error:', error);
        addMessageToChat('Connection error. Please check your internet and try again.', 'bot');
    } finally {
        showLoading(false);
    }
}

function addMessageToChat(message, sender) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;

    const icon = sender === 'bot' ? '<i class="fas fa-robot"></i>' : '<i class="fas fa-user"></i>';

    messageDiv.innerHTML = `
        ${icon}
        <div class="message-content">
            <p>${message}</p>
        </div>
    `;

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Farming Tips
function initializeTips() {
    const getTipsBtn = document.getElementById('getTipsBtn');
    getTipsBtn.addEventListener('click', getFarmingTips);
}

async function getFarmingTips() {
    const crop = document.getElementById('cropSelect').value;
    const season = document.getElementById('seasonSelect').value;
    const tipsResults = document.getElementById('tipsResults');
    const tipsContent = document.getElementById('tipsContent');

    showLoading(true);

    try {
        const response = await fetch(
            `${API_BASE}/farming-tips?crop=${crop}&season=${season}&language=${currentLanguage}`
        );
        const data = await response.json();

        if (data.success) {
            tipsContent.innerHTML = formatTips(data.tips);
            tipsResults.style.display = 'block';
        } else {
            alert('Failed to get tips: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to fetch farming tips.');
    } finally {
        showLoading(false);
    }
}

function formatTips(tips) {
    if (typeof tips === 'string') {
        return `<div class="tips-text">${tips}</div>`;
    }

    // Format structured tips
    let html = '<div class="structured-tips">';
    for (const [key, value] of Object.entries(tips)) {
        html += `
            <div class="tip-section">
                <h4>${key.replace(/_/g, ' ').toUpperCase()}</h4>
                <p>${Array.isArray(value) ? value.join('<br>') : value}</p>
            </div>
        `;
    }
    html += '</div>';
    return html;
}

// Language Toggle
function initializeLanguageToggle() {
    const langToggle = document.getElementById('langToggle');
    
    langToggle.addEventListener('click', () => {
        currentLanguage = currentLanguage === 'en' ? 'sw' : 'en';
        langToggle.innerHTML = `<i class="fas fa-globe"></i> ${currentLanguage === 'en' ? 'English' : 'Kiswahili'}`;
    });
}

// Utility Functions
function showLoading(show) {
    const overlay = document.getElementById('loadingOverlay');
    overlay.style.display = show ? 'flex' : 'none';
}

function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

// Service Worker for PWA (optional enhancement)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .catch(err => console.log('ServiceWorker registration failed:', err));
    });
      }
