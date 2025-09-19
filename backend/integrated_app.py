from flask import Flask, request, jsonify, render_template_string, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime
import logging
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class MedicalChatbot:
    def __init__(self):
        self.disease_data = self.load_disease_data()
        self.conversation_history = []
        self.setup_gemini()
        
    def setup_gemini(self):
        """Initialize Gemini AI model"""
        try:
            # Configure Gemini API
            api_key = os.getenv('GEMINI_API_KEY')
            if api_key and api_key != 'your_gemini_api_key_here':
                genai.configure(api_key=api_key)
                self.gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
                self.gemini_enabled = True
                logger.info("Gemini 2.0 Flash model initialized successfully")
            else:
                self.gemini_enabled = False
                logger.warning("Gemini API key not found, using rule-based system only")
        except Exception as e:
            self.gemini_enabled = False
            logger.error(f"Failed to initialize Gemini: {e}")
    
    def get_medical_prompt(self, user_message):
        """Create specialized medical prompt for Gemini"""
        
        # Check if it's a greeting or general chat
        greetings = ['hi', 'hello', 'hey', 'good morning', 'good evening', 'how are you']
        if user_message.lower().strip() in greetings:
            return f"""You are a medical assistant. The user said "{user_message}". 

Respond with a brief, friendly greeting and ask how you can help with their health concerns.

Keep it under 50 words and be professional."""
        
        # Check if it's a non-medical query (math, general questions, etc.)
        non_medical_patterns = ['+', '-', '*', '/', '=', 'calculate', 'what is', 'how much', 'math', 'number']
        if any(pattern in user_message.lower() for pattern in non_medical_patterns):
            return f"""The user asked: "{user_message}"

This appears to be a non-medical question. Politely redirect them to health topics.

Respond: "I'm a medical assistant focused on health-related questions. For math or general queries, please use appropriate tools. How can I help with your health concerns instead?" 

Keep it under 50 words."""
        
        # For medical queries
        prompt = f"""You are an AI medical assistant. Provide VERY SHORT, focused medical information.

STRICT RULES:
- Maximum 150 words total
- Use bullet points with HTML colored headings
- 2-3 conditions max
- Brief advice only
- Always end with "Consult a doctor"

USER: {user_message}

Format (use these exact HTML colors):
<span style="color: #3498db; font-weight: bold;">🔍 Possible causes:</span>
• Condition 1
• Condition 2

<span style="color: #e74c3c; font-weight: bold;">⚡ Quick advice:</span>
• Action 1
• Action 2

<span style="color: #f39c12; font-weight: bold;">👨‍⚕️ When to see doctor:</span> [brief]

Consult a doctor for proper diagnosis.

**When to see doctor:** [brief]

Consult a doctor for proper diagnosis."""
        
        return prompt
        
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
                "description": "A temporary increase in body temperature, often due to illness",
                "symptoms": ["high temperature", "chills", "sweating", "headache", "muscle aches"],
                "causes": ["viral infection", "bacterial infection", "heat exhaustion", "medication side effects"],
                "prevention": ["stay hydrated", "rest", "maintain hygiene", "avoid crowded places"],
                "treatment": ["rest", "fluids", "fever reducers", "consult doctor if persistent"],
                "emergency_signs": ["temperature over 103°F", "difficulty breathing", "chest pain", "confusion"]
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
        """Generate chatbot response using Gemini AI with rule-based fallback"""
        
        # Try Gemini AI first if available
        if self.gemini_enabled:
            try:
                gemini_response = self.get_gemini_response(user_input)
                if gemini_response:
                    return gemini_response
            except Exception as e:
                logger.warning(f"Gemini API failed, falling back to rule-based system: {e}")
        
        # Fallback to rule-based system
        return self.get_rule_based_response(user_input, language)
    
    def get_gemini_response(self, user_input):
        """Get response from Gemini AI"""
        try:
            prompt = self.get_medical_prompt(user_input)
            response = self.gemini_model.generate_content(prompt)
            
            # Analyze for emergency keywords to ensure safety
            emergency_keywords = ['emergency', 'urgent', 'chest pain', 'difficulty breathing', 
                                'unconscious', 'severe pain', 'heart attack', 'stroke', 
                                'suicide', 'self harm', 'blood in vomit', 'severe bleeding',
                                'cannot breathe', 'choking', 'severe allergic reaction']
            
            is_emergency = any(keyword in user_input.lower() for keyword in emergency_keywords)
            
            if is_emergency:
                return {
                    'type': 'emergency',
                    'message': '⚠️ MEDICAL EMERGENCY DETECTED ⚠️\n\nThis seems like a medical emergency. Please call emergency services immediately!',
                    'ai_response': response.text,
                    'emergency_contacts': {
                        'ambulance': '108',
                        'police': '100',
                        'fire': '101',
                        'national_helpline': '1800-180-1104',
                        'mental_health': '08046110007'
                    },
                    'immediate_advice': 'If this is a life-threatening emergency, call 108 immediately. Do not delay seeking professional medical help.',
                    'powered_by': 'Gemini 2.0 Flash + Emergency Detection'
                }
            else:
                return {
                    'type': 'ai_analysis',
                    'message': response.text,
                    'disclaimer': '⚠️ This AI-generated response is for informational purposes only. Always consult healthcare professionals for medical advice.',
                    'powered_by': 'Google Gemini 2.0 Flash',
                    'confidence': 'AI-powered analysis'
                }
                
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return None
    
    def get_rule_based_response(self, user_input, language='en'):
        """Original rule-based response system"""
        user_input = user_input.lower()
        
        # Enhanced health emergency keywords
        emergency_keywords = ['emergency', 'urgent', 'chest pain', 'difficulty breathing', 
                            'unconscious', 'severe pain', 'heart attack', 'stroke', 
                            'suicide', 'self harm', 'blood in vomit', 'severe bleeding',
                            'cannot breathe', 'choking', 'severe allergic reaction']
        
        # Mental health keywords
        mental_health_keywords = ['depression', 'anxiety', 'panic', 'stress', 'mental health',
                                'feeling sad', 'worried', 'anxious', 'panic attack']
        
        # General symptom keywords
        symptom_keywords = ['symptom', 'feel', 'pain', 'fever', 'headache', 'cough', 'ache',
                          'hurt', 'sick', 'unwell', 'tired', 'fatigue', 'nausea', 'vomit',
                          'dizzy', 'swelling', 'rash', 'itching', 'burning']
        
        if any(keyword in user_input for keyword in emergency_keywords):
            response = {
                'type': 'emergency',
                'message': 'This seems like a medical emergency. Please call emergency services immediately or visit the nearest hospital.',
                'emergency_contacts': {
                    'ambulance': '108',
                    'police': '100',
                    'fire': '101',
                    'national_helpline': '1800-180-1104',
                    'mental_health': '08046110007'
                },
                'immediate_advice': 'If this is a life-threatening emergency, call 108 immediately. Do not delay seeking professional medical help.',
                'powered_by': 'Rule-based Emergency Detection'
            }
        elif any(keyword in user_input for keyword in mental_health_keywords):
            response = {
                'type': 'mental_health',
                'message': 'Mental health is just as important as physical health. Here are some resources that might help:',
                'advice': [
                    'Talk to a trusted friend, family member, or counselor',
                    'Practice relaxation techniques like deep breathing',
                    'Maintain a regular sleep schedule',
                    'Engage in physical activity',
                    'Consider professional counseling or therapy'
                ],
                'helplines': {
                    'mental_health_helpline': '08046110007',
                    'national_helpline': '1800-180-1104',
                    'youth_helpline': '1800-233-3330'
                },
                'disclaimer': 'If you are having thoughts of self-harm, please seek immediate professional help or call emergency services.',
                'powered_by': 'Rule-based Mental Health Support'
            }
        elif any(keyword in user_input for keyword in symptom_keywords):
            # Enhanced symptom analysis
            possible_diseases = self.analyze_symptoms(user_input)
            if possible_diseases:
                response = {
                    'type': 'symptom_analysis',
                    'message': 'Based on your symptoms, here are some possible conditions:',
                    'possible_diseases': possible_diseases,
                    'disclaimer': 'This is not a medical diagnosis. Please consult a healthcare professional for proper diagnosis and treatment.',
                    'powered_by': 'Rule-based Symptom Analysis'
                }
            else:
                response = {
                    'type': 'general',
                    'message': 'I couldn\'t identify specific conditions based on your symptoms. Please provide more details or consult a healthcare professional.',
                    'powered_by': 'Rule-based System'
                }
        elif any(disease in user_input for disease in self.disease_data.keys()):
            # Disease information request
            for disease_key in self.disease_data.keys():
                if disease_key in user_input:
                    disease_info = self.disease_data[disease_key]
                    response = {
                        'type': 'disease_info',
                        'disease': disease_info,
                        'message': f'Here\'s information about {disease_info["name"]}:',
                        'powered_by': 'Medical Knowledge Database'
                    }
                    break
        else:
            # General health query
            response = {
                'type': 'general',
                'message': 'I\'m here to help with health information. You can ask me about symptoms, diseases, or general health advice. How can I assist you today?',
                'powered_by': 'Rule-based System'
            }
        
        return response

# Initialize chatbot
chatbot = MedicalChatbot()

# Serve frontend files
@app.route('/')
def index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('../frontend', filename)

# API routes
@app.route('/api')
def api_info():
    return jsonify({
        'message': 'AI Medical Chatbot API - Enhanced Version',
        'version': '2.0',
        'endpoints': {
            '/api/chat': 'POST - Chat with the AI medical assistant',
            '/api/diseases': 'GET - List all diseases in database',
            '/api/disease/<name>': 'GET - Get detailed disease information',
            '/api/emergency': 'GET - Emergency contacts and helplines',
            '/api/symptoms-check': 'POST - Analyze symptoms for possible conditions',
            '/api/health-tips': 'GET - Daily wellness and preventive care tips',
            '/api/first-aid': 'GET - Basic first aid guidelines',
            '/api/nutrition': 'GET - Nutrition and dietary information'
        },
        'features': [
            'Symptom analysis with AI',
            'Emergency detection',
            'Mental health support',
            'Comprehensive disease database',
            'Health tips and wellness advice',
            'First aid guidance',
            'Nutrition information'
        ]
    })

@app.route('/api/chat', methods=['POST'])
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

@app.route('/api/diseases', methods=['GET'])
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

@app.route('/api/disease/<disease_name>', methods=['GET'])
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

@app.route('/api/emergency', methods=['GET'])
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

@app.route('/api/symptoms-check', methods=['POST'])
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

@app.route('/api/health-tips', methods=['GET'])
def health_tips():
    """Get general health and wellness tips"""
    tips = {
        'daily_wellness': [
            'Drink at least 8 glasses of water daily',
            'Get 7-9 hours of sleep each night',
            'Exercise for at least 30 minutes daily',
            'Eat 5 servings of fruits and vegetables',
            'Practice stress management techniques',
            'Maintain good hygiene habits',
            'Limit processed foods and sugar',
            'Take breaks from screen time'
        ],
        'preventive_care': [
            'Schedule regular health check-ups',
            'Keep vaccinations up to date',
            'Monitor blood pressure regularly',
            'Check cholesterol levels annually',
            'Practice good oral hygiene',
            'Protect skin from UV radiation',
            'Maintain healthy weight',
            'Don\'t smoke or use tobacco'
        ],
        'mental_wellness': [
            'Practice mindfulness and meditation',
            'Stay connected with family and friends',
            'Engage in hobbies you enjoy',
            'Learn new skills or knowledge',
            'Express gratitude daily',
            'Seek help when feeling overwhelmed',
            'Maintain work-life balance',
            'Practice deep breathing exercises'
        ]
    }
    
    return jsonify({
        'success': True,
        'health_tips': tips,
        'message': 'Remember: These are general wellness tips. Always consult healthcare professionals for personalized advice.'
    })

@app.route('/api/first-aid', methods=['GET'])
def first_aid():
    """Get basic first aid information"""
    first_aid_info = {
        'common_situations': {
            'cuts_and_scrapes': [
                'Clean your hands',
                'Stop the bleeding by applying pressure',
                'Clean the wound with water',
                'Apply antibiotic ointment',
                'Cover with sterile bandage',
                'Change bandage daily'
            ],
            'burns': [
                'Cool the burn with cold water',
                'Remove jewelry near the burn',
                'Don\'t break blisters',
                'Apply aloe vera or moisturizer',
                'Cover with loose bandage',
                'Seek medical help for severe burns'
            ],
            'sprains': [
                'Rest the injured area',
                'Apply ice for 15-20 minutes',
                'Compress with elastic bandage',
                'Elevate the injured limb',
                'Take over-the-counter pain relievers',
                'Seek medical attention if severe'
            ],
            'nosebleeds': [
                'Sit upright and lean forward',
                'Pinch nostrils firmly for 10 minutes',
                'Breathe through your mouth',
                'Apply ice to nose bridge',
                'Avoid lying down',
                'Seek help if bleeding persists'
            ]
        },
        'emergency_disclaimer': 'These are basic first aid guidelines. For serious injuries or emergencies, call 108 immediately.'
    }
    
    return jsonify({
        'success': True,
        'first_aid': first_aid_info
    })

@app.route('/api/nutrition', methods=['GET'])
def nutrition():
    """Get nutrition and dietary information"""
    nutrition_info = {
        'balanced_diet': {
            'proteins': [
                'Lean meats, fish, eggs',
                'Legumes, beans, lentils',
                'Nuts and seeds',
                'Dairy products',
                'Quinoa and tofu'
            ],
            'carbohydrates': [
                'Whole grains (brown rice, oats)',
                'Fruits and vegetables',
                'Sweet potatoes',
                'Whole wheat products',
                'Legumes'
            ],
            'healthy_fats': [
                'Avocados and olive oil',
                'Nuts and seeds',
                'Fatty fish (salmon, mackerel)',
                'Coconut oil (in moderation)',
                'Dark chocolate'
            ],
            'vitamins_minerals': [
                'Leafy green vegetables',
                'Colorful fruits and vegetables',
                'Dairy or fortified alternatives',
                'Seafood and lean meats',
                'Whole grains and nuts'
            ]
        },
        'hydration': [
            'Drink water regularly throughout the day',
            'Monitor urine color (should be light yellow)',
            'Increase intake during exercise or hot weather',
            'Limit sugary and caffeinated drinks',
            'Include water-rich foods like fruits'
        ],
        'special_diets': {
            'diabetes': 'Focus on complex carbs, lean proteins, and healthy fats. Monitor blood sugar levels.',
            'heart_health': 'Reduce sodium, saturated fats. Increase omega-3 fatty acids and fiber.',
            'weight_management': 'Create caloric balance, focus on nutrient-dense foods, practice portion control.',
            'digestive_health': 'Include probiotics, fiber-rich foods, stay hydrated, avoid trigger foods.'
        }
    }
    
    return jsonify({
        'success': True,
        'nutrition': nutrition_info,
        'message': 'Consult a registered dietitian for personalized nutrition advice.'
    })

if __name__ == '__main__':
    print("🏥 AI Medical Chatbot Server Starting...")
    print("🌐 Frontend and API available at: http://localhost:5000")
    print("📱 In codespace, check the 'Ports' tab for the public URL")
    print("🔧 API endpoints available at: /api/*")
    app.run(debug=True, host='0.0.0.0', port=5000)