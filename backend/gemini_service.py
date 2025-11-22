"""
Gemini API Service
Handles all interactions with Google Gemini API
"""

import google.generativeai as genai
from typing import List, Dict, Optional
import json

class GeminiService:
    def __init__(self, api_key: str):
        """Initialize Gemini service with API key"""
        genai.configure(api_key=api_key)
        
        # Use Gemini 1.5 Flash for speed (Pro for better quality if needed)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # System instruction for agricultural context
        self.system_instruction = """
        You are AgriAssist AI, an expert agricultural advisor specifically designed for East African farmers,
        with deep knowledge of Kenyan agriculture.
        
        Your expertise includes:
        - Common crops: Maize, beans, tea, coffee, potatoes, tomatoes, kale (sukuma wiki)
        - Local diseases and pests
        - Climate considerations for different regions (coastal, highlands, arid areas)
        - Sustainable and affordable farming practices
        - Organic solutions when possible
        
        Guidelines:
        - Use simple, clear language that farmers can understand
        - Provide actionable, practical advice
        - Consider cost-effectiveness (many farmers have limited resources)
        - Suggest both modern and traditional solutions
        - Be encouraging and supportive
        - When diagnosing diseases, provide: symptoms, causes, treatment, prevention
        - Include approximate costs in Kenyan Shillings when suggesting inputs
        """
    
    def analyze_image_with_text(self, image_data, prompt: str, language: str = 'en') -> str:
        """
        Analyze image with custom prompt using Gemini's multimodal capabilities
        
        Args:
            image_data: Image file object or bytes
            prompt: Text prompt for analysis
            language: Response language (en/sw)
            
        Returns:
            AI-generated analysis
        """
        try:
            # Add language instruction
            lang_instruction = ""
            if language == 'sw':
                lang_instruction = "Respond in Swahili (Kiswahili). "
            
            full_prompt = lang_instruction + prompt
            
            # Generate response with image
            response = self.model.generate_content([full_prompt, image_data])
            
            return response.text
            
        except Exception as e:
            raise Exception(f"Gemini image analysis failed: {str(e)}")
    
    def chat(self, message: str, history: List[Dict] = None, language: str = 'en') -> str:
        """
        Chat with Gemini with conversation history
        
        Args:
            message: User message
            history: Previous conversation history
            language: Response language
            
        Returns:
            AI response
        """
        try:
            # Create chat session
            chat = self.model.start_chat(history=history or [])
            
            # Add language instruction
            if language == 'sw':
                message = f"[Respond in Swahili] {message}"
            
            # Send message
            response = chat.send_message(message)
            
            return response.text
            
        except Exception as e:
            raise Exception(f"Gemini chat failed: {str(e)}")
    
    def get_farming_tips(self, crop: str, season: str, language: str = 'en') -> Dict:
        """
        Get farming tips for specific crop and season
        
        Args:
            crop: Crop name
            season: Season (rainy/dry/current)
            language: Response language
            
        Returns:
            Structured farming tips
        """
        try:
            prompt = f"""
            Provide comprehensive farming tips for {crop} during the {season} season in Kenya.
            
            Include:
            1. Best planting practices
            2. Watering schedule
            3. Common challenges this season
            4. Fertilizer recommendations (with costs)
            5. Expected harvest timeline
            
            Format as JSON with keys: planting, watering, challenges, fertilizer, harvest
            """
            
            if language == 'sw':
                prompt += "\nProvide all text in Swahili."
            
            response = self.model.generate_content(prompt)
            
            # Try to parse as JSON, fallback to text
            try:
                return json.loads(response.text)
            except:
                return {'tips': response.text}
                
        except Exception as e:
            raise Exception(f"Failed to get farming tips: {str(e)}")
    
    def diagnose_disease_structured(self, symptoms: str, crop: str) -> Dict:
        """
        Diagnose crop disease with structured output
        
        Args:
            symptoms: Description of symptoms
            crop: Crop type
            
        Returns:
            Structured diagnosis
        """
        try:
            prompt = f"""
            Diagnose the disease affecting {crop} with these symptoms: {symptoms}
            
            Provide a structured response in JSON format:
            {{
                "disease_name": "string",
                "confidence": "high/medium/low",
                "symptoms": ["list", "of", "symptoms"],
                "causes": ["list", "of", "causes"],
                "treatment": {{
                    "immediate": "string",
                    "organic": "string",
                    "chemical": "string (with product names and costs in KES)"
                }},
                "prevention": ["list", "of", "preventive", "measures"],
                "severity": "mild/moderate/severe"
            }}
            """
            
            response = self.model.generate_content(prompt)
            
            try:
                return json.loads(response.text)
            except:
                # Fallback if JSON parsing fails
                return {
                    'disease_name': 'Unknown',
                    'diagnosis': response.text
                }
                
        except Exception as e:
            raise Exception(f"Disease diagnosis failed: {str(e)}")
