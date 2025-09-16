# AI Medical Chatbot Setup Guide - SIH 2025

## Quick Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Web browser (Chrome, Firefox, Safari)

### Installation Steps

1. **Clone/Download the project**
   ```bash
   cd AI_Medical_chatbot
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download required NLTK data** (optional - handled automatically)
   ```python
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
   ```

4. **Start the backend server**
   ```bash
   cd backend
   python app.py
   ```
   The server will start on `http://localhost:5000`

5. **Open the frontend**
   - Open `frontend/index.html` in your web browser
   - Or serve it using a simple HTTP server:
     ```bash
     cd frontend
     python -m http.server 8080
     ```
   - Then visit `http://localhost:8080`

### Environment Configuration (Optional)

Create a `.env` file in the project root for production use:

```env
FLASK_DEBUG=False
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-key
GOOGLE_TRANSLATE_API_KEY=your-google-translate-key
```

### Testing the Application

1. **Chat Feature**: Type messages like "I have fever and headache"
2. **Symptom Checker**: Go to "Symptom Checker" tab and describe symptoms
3. **Disease Info**: Browse diseases in the "Disease Info" tab
4. **Emergency**: Check emergency contacts in the "Emergency" tab
5. **Language**: Change language using the dropdown in the header

### API Endpoints

- `GET /` - API information
- `POST /chat` - Chat with the bot
- `GET /diseases` - List all diseases
- `GET /disease/<name>` - Get disease details
- `POST /symptoms-check` - Check symptoms
- `GET /emergency` - Emergency contacts
- `GET /health-tips` - Health tips

### Troubleshooting

**Port already in use**: Change the port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

**Translation errors**: The app works without translation if Google Translate fails

**CORS issues**: Make sure Flask-CORS is installed and enabled

### Deployment

For production deployment:
1. Set `FLASK_DEBUG=False` in environment
2. Use a production WSGI server like Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

## Features for SIH 2025 Demo

### Core Features
- ✅ AI-powered medical chatbot
- ✅ Disease awareness and information
- ✅ Symptom checker with analysis
- ✅ Multi-language support (12+ Indian languages)
- ✅ Emergency contact integration
- ✅ Responsive web interface
- ✅ Comprehensive disease database

### Advanced Features
- 🔄 Real-time translation
- 🔄 Regional health information
- 🔄 Healthcare facility locator
- 🔄 Voice input support (browser-dependent)
- 🔄 Offline mode capability

### Government Integration Ready
- State-wise health department contacts
- National health helpline integration
- Regional disease prevalence data
- Multi-lingual accessibility
- Emergency services integration

## Architecture Overview

```
Frontend (HTML/CSS/JS)
    ↓
Flask REST API
    ↓
AI/ML Models (Transformers, NLTK)
    ↓
Disease Knowledge Base (JSON)
    ↓
Translation Services (Google Translate)
```

This application is ready for SIH 2025 presentation and can be extended with additional features based on specific requirements.