from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
import logging
# from googletrans import Translator
import nltk
# from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import pandas as pd
import numpy as np

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    passFlask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
import logging
from googletrans import Translator
import nltk
# Removed heavy transformers import for lighter demo
import pandas as pd
import numpy as np

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    pass

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize translator (commented out for demo)
# translator = Translator()

class MedicalChatbot:
    def __init__(self):
        self.disease_data = self.load_disease_data()
        self.conversation_history = []
        
    def load_disease_data(self):
        """Load disease information from JSON file"""
        try:
            # Try relative path first, then absolute path
            data_file = '../data/diseases.json'
            if not os.path.exists(data_file):
                data_file = '/workspaces/AI_Medical_chatbot/data/diseases.json'
            
            with open(data_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("Disease data file not found, using default data")
            return self.get_default_disease_data()
    
    def get_default_disease_data(self):
        """Default disease data for demo purposes"""
        return {
            "fever": {
                "name": "Fever",
                "symptoms": ["high temperature", "chills", "sweating", "headache", "muscle aches"],
                "causes": ["viral infection", "bacterial infection", "heat exhaustion", "medication side effects"],
                "prevention": ["stay hydrated", "rest", "maintain hygiene", "avoid crowded places"],
                "treatment": ["rest", "fluids", "fever reducers", "consult doctor if persistent"],
                "emergency_signs": ["temperature over 103°F", "difficulty breathing", "chest pain", "confusion"]
            },
            "diabetes": {
                "name": "Diabetes",
                "symptoms": ["frequent urination", "excessive thirst", "unexplained weight loss", "fatigue", "blurred vision"],
                "causes": ["genetics", "lifestyle factors", "obesity", "age"],
                "prevention": ["healthy diet", "regular exercise", "maintain healthy weight", "limit sugar intake"],
                "treatment": ["medication", "insulin therapy", "diet control", "regular monitoring"],
                "emergency_signs": ["severe dehydration", "confusion", "vomiting", "difficulty breathing"]
            },
            "hypertension": {
                "name": "High Blood Pressure",
                "symptoms": ["headaches", "shortness of breath", "nosebleeds", "chest pain"],
                "causes": ["age", "family history", "obesity", "high sodium diet", "stress"],
                "prevention": ["low sodium diet", "regular exercise", "stress management", "limit alcohol"],
                "treatment": ["lifestyle changes", "medication", "regular monitoring", "weight management"],
                "emergency_signs": ["severe headache", "chest pain", "difficulty breathing", "vision problems"]
            }
        }
    
    def analyze_symptoms(self, symptoms_text):
        """Analyze symptoms and suggest possible conditions"""
        symptoms_text = symptoms_text.lower()
        possible_diseases = []
        
        for disease, info in self.disease_data.items():
            symptom_matches = 0
            for symptom in info['symptoms']:
                if symptom.lower() in symptoms_text:
                    symptom_matches += 1
            
            if symptom_matches > 0:
                confidence = (symptom_matches / len(info['symptoms'])) * 100
                possible_diseases.append({
                    'disease': info['name'],
                    'confidence': round(confidence, 2),
                    'matched_symptoms': symptom_matches
                })
        
        # Sort by confidence
        possible_diseases.sort(key=lambda x: x['confidence'], reverse=True)
        return possible_diseases[:3]  # Return top 3 matches
    
    def get_disease_info(self, disease_name):
        """Get detailed information about a specific disease"""
        disease_name = disease_name.lower()
        for key, info in self.disease_data.items():
            if key.lower() == disease_name or info['name'].lower() == disease_name:
                return info
        return None
    
    def generate_response(self, user_input, language='en'):
        """Generate chatbot response based on user input"""
        user_input = user_input.lower()
        
        # Health emergency keywords
        emergency_keywords = ['emergency', 'urgent', 'chest pain', 'difficulty breathing', 
                            'unconscious', 'severe pain', 'heart attack', 'stroke']
        
        if any(keyword in user_input for keyword in emergency_keywords):
            response = {
                'type': 'emergency',
                'message': 'This seems like a medical emergency. Please call emergency services immediately or visit the nearest hospital.',
                'emergency_contacts': {
                    'ambulance': '108',
                    'police': '100',
                    'fire': '101'
                }
            }
        elif 'symptom' in user_input or 'feel' in user_input or 'pain' in user_input:
            # Symptom analysis
            possible_diseases = self.analyze_symptoms(user_input)
            if possible_diseases:
                response = {
                    'type': 'symptom_analysis',
                    'message': 'Based on your symptoms, here are some possible conditions:',
                    'possible_diseases': possible_diseases,
                    'disclaimer': 'This is not a medical diagnosis. Please consult a healthcare professional for proper diagnosis and treatment.'
                }
            else:
                response = {
                    'type': 'general',
                    'message': 'I couldn\'t identify specific conditions based on your symptoms. Please provide more details or consult a healthcare professional.'
                }
        elif any(disease in user_input for disease in self.disease_data.keys()):
            # Disease information request
            for disease_key in self.disease_data.keys():
                if disease_key in user_input:
                    disease_info = self.disease_data[disease_key]
                    response = {
                        'type': 'disease_info',
                        'disease': disease_info,
                        'message': f'Here\'s information about {disease_info["name"]}:'
                    }
                    break
        else:
            # General health query
            response = {
                'type': 'general',
                'message': 'I\'m here to help with health information. You can ask me about symptoms, diseases, or general health advice. How can I assist you today?'
            }
        
        # Translate response if needed
        if language != 'en':
            response['message'] = self.translate_text(response['message'], language)
        
        return response
    
    def translate_text(self, text, target_language):
        """Translate text to target language"""
        try:
            # Commented out for demo - would use Google Translate in production
            # translated = translator.translate(text, dest=target_language)
            # return translated.text
            return text  # Return original text for demo
        except:
            return text  # Return original text if translation fails

# Initialize chatbot
chatbot = MedicalChatbot()

@app.route('/')
def home():
    return jsonify({
        'message': 'AI Medical Chatbot API',
        'version': '1.0',
        'endpoints': {
            '/chat': 'POST - Chat with the bot',
            '/diseases': 'GET - List all diseases',
            '/disease/<name>': 'GET - Get disease information',
            '/emergency': 'GET - Emergency contacts'
        }
    })

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        language = data.get('language', 'en')
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Generate response
        response = chatbot.generate_response(user_message, language)
        
        # Store conversation
        chatbot.conversation_history.append({
            'user_message': user_message,
            'bot_response': response,
            'timestamp': datetime.now().isoformat(),
            'language': language
        })
        
        return jsonify({
            'success': True,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/diseases', methods=['GET'])
def list_diseases():
    """Get list of all available diseases"""
    diseases = []
    for key, info in chatbot.disease_data.items():
        diseases.append({
            'id': key,
            'name': info['name'],
            'symptoms_count': len(info['symptoms'])
        })
    
    return jsonify({
        'success': True,
        'diseases': diseases,
        'total': len(diseases)
    })

@app.route('/disease/<disease_name>', methods=['GET'])
def get_disease(disease_name):
    """Get detailed information about a specific disease"""
    disease_info = chatbot.get_disease_info(disease_name)
    
    if disease_info:
        return jsonify({
            'success': True,
            'disease': disease_info
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Disease not found'
        }), 404

@app.route('/emergency', methods=['GET'])
def emergency_contacts():
    """Get emergency contact information"""
    return jsonify({
        'success': True,
        'emergency_contacts': {
            'ambulance': '108',
            'police': '100',
            'fire_service': '101',
            'disaster_management': '108',
            'women_helpline': '1091',
            'child_helpline': '1098'
        },
        'health_helplines': {
            'national_health_helpline': '1800-180-1104',
            'covid_helpline': '1075',
            'mental_health_helpline': '08046110007'
        }
    })

@app.route('/symptoms-check', methods=['POST'])
def symptoms_check():
    """Check symptoms and provide possible conditions"""
    try:
        data = request.get_json()
        symptoms = data.get('symptoms', '')
        
        if not symptoms:
            return jsonify({'error': 'Symptoms are required'}), 400
        
        possible_diseases = chatbot.analyze_symptoms(symptoms)
        
        return jsonify({
            'success': True,
            'symptoms': symptoms,
            'possible_conditions': possible_diseases,
            'disclaimer': 'This is not a medical diagnosis. Please consult a healthcare professional.',
            'recommendation': 'If symptoms persist or worsen, please seek immediate medical attention.'
        })
        
    except Exception as e:
        logger.error(f"Error in symptoms check: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/health-tips', methods=['GET'])
def health_tips():
    """Get general health tips"""
    tips = [
        "Drink at least 8 glasses of water daily",
        "Exercise for at least 30 minutes daily",
        "Eat a balanced diet with fruits and vegetables",
        "Get 7-8 hours of sleep every night",
        "Wash your hands frequently",
        "Avoid smoking and excessive alcohol",
        "Regular health check-ups are important",
        "Manage stress through meditation or yoga",
        "Maintain a healthy weight",
        "Stay up to date with vaccinations"
    ]
    
    return jsonify({
        'success': True,
        'health_tips': tips,
        'total': len(tips)
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)