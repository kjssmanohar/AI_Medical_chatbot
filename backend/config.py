# Environment Configuration
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-for-sih-2025'
    DEBUG = os.environ.get('FLASK_DEBUG') or True
    
    # API Keys (for production use)
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    GOOGLE_TRANSLATE_API_KEY = os.environ.get('GOOGLE_TRANSLATE_API_KEY')
    
    # Database Configuration
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///medical_chatbot.db'
    
    # Supported Languages for SIH 2025
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'hi': 'हिंदी (Hindi)',
        'te': 'తెలుగు (Telugu)',
        'ta': 'தமிழ் (Tamil)',
        'bn': 'বাংলা (Bengali)',
        'gu': 'ગુજરાતી (Gujarati)',
        'mr': 'मराठी (Marathi)',
        'kn': 'ಕನ್ನಡ (Kannada)',
        'ml': 'മലയാളം (Malayalam)',
        'or': 'ଓଡ଼ିଆ (Odia)',
        'pa': 'ਪੰਜਾਬੀ (Punjabi)',
        'ur': 'اردو (Urdu)'
    }
    
    # Medical Emergency Numbers (India)
    EMERGENCY_CONTACTS = {
        'ambulance': '108',
        'police': '100',
        'fire': '101',
        'disaster_management': '108',
        'women_helpline': '1091',
        'child_helpline': '1098',
        'national_health_helpline': '1800-180-1104',
        'covid_helpline': '1075',
        'mental_health_helpline': '08046110007'
    }
    
    # AI Model Configuration
    AI_MODEL_NAME = 'microsoft/DialoGPT-medium'
    MAX_RESPONSE_LENGTH = 512
    CONFIDENCE_THRESHOLD = 0.3