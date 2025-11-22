"""
AgriAssist AI - Flask Backend
Main application file
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
from dotenv import load_dotenv
import logging

from gemini_service import GeminiService
from image_analyzer import ImageAnalyzer
from weather_service import WeatherService

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, 
            static_folder='../frontend',
            template_folder='../frontend')
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
gemini_service = GeminiService(api_key=os.getenv('GEMINI_API_KEY'))
image_analyzer = ImageAnalyzer(gemini_service)
weather_service = WeatherService(api_key=os.getenv('WEATHER_API_KEY'))

# Store conversation history (in production, use Redis/DB)
conversations = {}

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'AgriAssist AI',
        'version': '1.0.0'
    })

@app.route('/api/analyze-crop', methods=['POST'])
def analyze_crop():
    """
    Analyze crop image for diseases
    Expects: multipart/form-data with 'image' file and optional 'location'
    """
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        image_file = request.files['image']
        location = request.form.get('location', 'Kenya')
        language = request.form.get('language', 'en')
        
        # Get weather context (optional)
        weather_context = None
        if location:
            weather_context = weather_service.get_weather(location)
        
        # Analyze image with Gemini
        analysis = image_analyzer.analyze_crop_disease(
            image_file, 
            location=location,
            weather_context=weather_context,
            language=language
        )
        
        logger.info(f"Crop analysis completed for location: {location}")
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'weather': weather_context
        })
        
    except Exception as e:
        logger.error(f"Error in crop analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Chat endpoint for conversational queries
    Expects: JSON with 'message', 'session_id', optional 'language'
    """
    try:
        data = request.get_json()
        message = data.get('message')
        session_id = data.get('session_id', 'default')
        language = data.get('language', 'en')
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Get or create conversation history
        if session_id not in conversations:
            conversations[session_id] = []
        
        # Get response from Gemini
        response = gemini_service.chat(
            message=message,
            history=conversations[session_id],
            language=language
        )
        
        # Update conversation history
        conversations[session_id].append({
            'role': 'user',
            'parts': [message]
        })
        conversations[session_id].append({
            'role': 'model',
            'parts': [response]
        })
        
        logger.info(f"Chat response generated for session: {session_id}")
        
        return jsonify({
            'success': True,
            'response': response,
            'session_id': session_id
        })
        
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/farming-tips', methods=['GET'])
def farming_tips():
    """
    Get general farming tips based on season and crop
    Query params: crop, season, language
    """
    try:
        crop = request.args.get('crop', 'maize')
        season = request.args.get('season', 'current')
        language = request.args.get('language', 'en')
        
        tips = gemini_service.get_farming_tips(
            crop=crop,
            season=season,
            language=language
        )
        
        return jsonify({
            'success': True,
            'tips': tips,
            'crop': crop,
            'season': season
        })
        
    except Exception as e:
        logger.error(f"Error getting farming tips: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/market-prices', methods=['GET'])
def market_prices():
    """
    Get current market prices (mock data for MVP)
    In production, integrate with real market data API
    """
    # Mock data for MVP
    mock_prices = {
        'maize': {'price': 3500, 'unit': 'KES/90kg bag', 'trend': 'stable'},
        'beans': {'price': 12000, 'unit': 'KES/90kg bag', 'trend': 'rising'},
        'tomatoes': {'price': 80, 'unit': 'KES/kg', 'trend': 'falling'},
        'potatoes': {'price': 60, 'unit': 'KES/kg', 'trend': 'stable'}
    }
    
    return jsonify({
        'success': True,
        'prices': mock_prices,
        'last_updated': '2025-11-22'
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.getenv('FLASK_ENV') == 'development'
    )
