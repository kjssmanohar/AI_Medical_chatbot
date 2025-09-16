# Translation utilities for multilingual support
from googletrans import Translator
import json
import os

class MultilingualSupport:
    def __init__(self):
        self.translator = Translator()
        self.supported_languages = {
            'en': 'english',
            'hi': 'hindi',
            'te': 'telugu',
            'ta': 'tamil',
            'bn': 'bengali',
            'gu': 'gujarati',
            'mr': 'marathi',
            'kn': 'kannada',
            'ml': 'malayalam',
            'or': 'oriya',
            'pa': 'punjabi',
            'ur': 'urdu'
        }
        
        # Pre-translated common medical terms
        self.medical_terms = {
            'en': {
                'fever': 'fever',
                'headache': 'headache',
                'cough': 'cough',
                'pain': 'pain',
                'doctor': 'doctor',
                'medicine': 'medicine',
                'hospital': 'hospital',
                'emergency': 'emergency'
            },
            'hi': {
                'fever': 'बुखार',
                'headache': 'सिरदर्द',
                'cough': 'खांसी',
                'pain': 'दर्द',
                'doctor': 'डॉक्टर',
                'medicine': 'दवा',
                'hospital': 'अस्पताल',
                'emergency': 'आपातकाल'
            },
            'te': {
                'fever': 'జ్వరం',
                'headache': 'తలనొప్పి',
                'cough': 'దగ్గు',
                'pain': 'నొప్పి',
                'doctor': 'వైద్యుడు',
                'medicine': 'మందు',
                'hospital': 'ఆసుపత్రి',
                'emergency': 'అత్యవసరం'
            },
            'ta': {
                'fever': 'காய்ச்சல்',
                'headache': 'தலைவலி',
                'cough': 'இருமல்',
                'pain': 'வலி',
                'doctor': 'மருத்துவர்',
                'medicine': 'மருந்து',
                'hospital': 'மருத்துவமனை',
                'emergency': 'அவசரநிலை'
            },
            'bn': {
                'fever': 'জ্বর',
                'headache': 'মাথাব্যথা',
                'cough': 'কাশি',
                'pain': 'ব্যথা',
                'doctor': 'ডাক্তার',
                'medicine': 'ওষুধ',
                'hospital': 'হাসপাতাল',
                'emergency': 'জরুরি'
            }
        }
        
        # Pre-translated common responses
        self.common_responses = {
            'en': {
                'greeting': 'Hello! How can I help you with your health concerns today?',
                'emergency_warning': 'This seems like a medical emergency. Please seek immediate medical attention.',
                'disclaimer': 'This is for informational purposes only. Please consult a healthcare professional.',
                'no_match': 'I couldn\'t find specific information. Please provide more details.'
            },
            'hi': {
                'greeting': 'नमस्ते! आज मैं आपकी स्वास्थ्य समस्याओं में कैसे मदद कर सकता हूं?',
                'emergency_warning': 'यह एक मेडिकल इमरजेंसी लगती है। कृपया तुरंत चिकित्सा सहायता लें।',
                'disclaimer': 'यह केवल जानकारी के लिए है। कृपया किसी स्वास्थ्य पेशेवर से सलाह लें।',
                'no_match': 'मुझे विशिष्ट जानकारी नहीं मिली। कृपया अधिक विवरण दें।'
            },
            'te': {
                'greeting': 'నమస్కారం! ఈ రోజు మీ ఆరోగ్య సమస్యలతో నేను ఎలా సహాయం చేయగలను?',
                'emergency_warning': 'ఇది వైద్య అత్యవసర పరిస్థితిలా కనిపిస్తోంది। దయచేసి వెంటనే వైద్య సహాయం తీసుకోండి।',
                'disclaimer': 'ఇది కేవలం సమాచార ప్రయోజనాల కోసం మాత్రమే. దయచేసి ఆరోగ్య నిపుణుడిని సంప్రదించండి।',
                'no_match': 'నాకు నిర్దిష్ట సమాచారం కనుగొనలేకపోయింది. దయచేసి మరిన్ని వివరాలు ఇవ్వండి।'
            }
        }
    
    def translate_text(self, text, target_language, source_language='en'):
        """Translate text to target language"""
        if target_language == source_language:
            return text
            
        try:
            # Check if we have a pre-translated version
            if source_language == 'en' and target_language in self.common_responses:
                for key, value in self.common_responses['en'].items():
                    if text.lower() in value.lower():
                        return self.common_responses[target_language].get(key, text)
            
            # Use Google Translate for other text
            result = self.translator.translate(text, dest=target_language, src=source_language)
            return result.text
        except Exception as e:
            print(f"Translation error: {e}")
            return text
    
    def detect_language(self, text):
        """Detect the language of input text"""
        try:
            result = self.translator.detect(text)
            return result.lang
        except:
            return 'en'  # Default to English
    
    def get_medical_term(self, term, language):
        """Get translated medical term"""
        if language in self.medical_terms and term.lower() in self.medical_terms[language]:
            return self.medical_terms[language][term.lower()]
        return term
    
    def translate_disease_info(self, disease_info, target_language):
        """Translate disease information to target language"""
        if target_language == 'en':
            return disease_info
        
        translated_info = {}
        for key, value in disease_info.items():
            if isinstance(value, str):
                translated_info[key] = self.translate_text(value, target_language)
            elif isinstance(value, list):
                translated_info[key] = [self.translate_text(item, target_language) for item in value]
            else:
                translated_info[key] = value
        
        return translated_info
    
    def get_language_name(self, language_code):
        """Get language name from code"""
        return self.supported_languages.get(language_code, 'English')

# Regional health information for different states in India
class RegionalHealthInfo:
    def __init__(self):
        self.state_health_departments = {
            'odisha': {
                'health_department': 'Department of Health & Family Welfare, Odisha',
                'helpline': '104',
                'website': 'https://health.odisha.gov.in/',
                'covid_helpline': '9439994859',
                'ambulance': '108'
            },
            'andhra_pradesh': {
                'health_department': 'Department of Health, Medical & Family Welfare, AP',
                'helpline': '104',
                'website': 'https://hmfw.ap.gov.in/',
                'covid_helpline': '0866-2410978',
                'ambulance': '108'
            },
            'telangana': {
                'health_department': 'Department of Health, Medical & Family Welfare, Telangana',
                'helpline': '104',
                'website': 'https://health.telangana.gov.in/',
                'covid_helpline': '040-23814500',
                'ambulance': '108'
            },
            'tamil_nadu': {
                'health_department': 'Directorate of Public Health, Tamil Nadu',
                'helpline': '104',
                'website': 'https://www.tn.gov.in/department/10',
                'covid_helpline': '044-29510400',
                'ambulance': '108'
            },
            'west_bengal': {
                'health_department': 'Department of Health & Family Welfare, West Bengal',
                'helpline': '104',
                'website': 'https://www.wbhealth.gov.in/',
                'covid_helpline': '033-23576001',
                'ambulance': '108'
            }
        }
        
        # Common diseases in different regions
        self.regional_diseases = {
            'coastal': ['dengue', 'malaria', 'chikungunya', 'typhoid'],
            'urban': ['diabetes', 'hypertension', 'respiratory_diseases', 'stress'],
            'rural': ['malaria', 'tuberculosis', 'anemia', 'diarrhea'],
            'tribal': ['malaria', 'sickle_cell', 'malnutrition', 'tuberculosis']
        }
    
    def get_state_info(self, state):
        """Get health department information for a state"""
        return self.state_health_departments.get(state.lower(), {})
    
    def get_regional_diseases(self, region_type):
        """Get common diseases for a region type"""
        return self.regional_diseases.get(region_type.lower(), [])

# Healthcare facility locator (mock data for demo)
class HealthcareFacilities:
    def __init__(self):
        self.facilities = {
            'bhubaneswar': [
                {
                    'name': 'AIIMS Bhubaneswar',
                    'type': 'Government Hospital',
                    'address': 'Sijua, Patrapada, Bhubaneswar',
                    'phone': '0674-2476751',
                    'emergency': '108',
                    'specialties': ['Emergency', 'Cardiology', 'Neurology', 'Oncology']
                },
                {
                    'name': 'Capital Hospital',
                    'type': 'Government Hospital',
                    'address': 'Unit 6, Bhubaneswar',
                    'phone': '0674-2390123',
                    'emergency': '108',
                    'specialties': ['Emergency', 'General Medicine', 'Surgery']
                }
            ],
            'hyderabad': [
                {
                    'name': 'NIMS Hospital',
                    'type': 'Government Hospital',
                    'address': 'Punjagutta, Hyderabad',
                    'phone': '040-23489999',
                    'emergency': '108',
                    'specialties': ['Emergency', 'Neurology', 'Cardiology']
                }
            ]
        }
    
    def find_nearby_hospitals(self, city):
        """Find hospitals in a city"""
        return self.facilities.get(city.lower(), [])
    
    def get_emergency_contacts(self, city):
        """Get emergency contacts for a city"""
        facilities = self.find_nearby_hospitals(city)
        return [facility['emergency'] for facility in facilities if 'emergency' in facility]