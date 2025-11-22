"""
Image Analysis Service
Specialized service for crop disease detection from images
"""

from PIL import Image
import io
from typing import Dict, Optional

class ImageAnalyzer:
    def __init__(self, gemini_service):
        """Initialize with Gemini service"""
        self.gemini = gemini_service
    
    def analyze_crop_disease(
        self, 
        image_file, 
        location: str = 'Kenya',
        weather_context: Optional[Dict] = None,
        language: str = 'en'
    ) -> Dict:
        """
        Analyze crop image for diseases and health issues
        
        Args:
            image_file: Uploaded image file
            location: Farmer's location
            weather_context: Current weather data
            language: Response language
            
        Returns:
            Comprehensive disease analysis
        """
        try:
            # Load and validate image
            image = Image.open(image_file)
            
            # Prepare context
            weather_info = ""
            if weather_context:
                weather_info = f"""
                Current weather in {location}:
                - Temperature: {weather_context.get('temperature', 'N/A')}°C
                - Conditions: {weather_context.get('description', 'N/A')}
                - Humidity: {weather_context.get('humidity', 'N/A')}%
                """
            
            # Construct detailed prompt
            prompt = f"""
            Analyze this crop image for diseases, pests, and health issues.
            
            Context:
            - Location: {location}
            {weather_info}
            
            Please provide:
            
            1. **Crop Identification**: What crop is this?
            
            2. **Health Assessment**: Overall health status (Healthy/Mild Issues/Severe Issues)
            
            3. **Disease/Pest Detection**: 
               - Name of disease or pest (if any)
               - Confidence level (High/Medium/Low)
               - Visible symptoms
            
            4. **Detailed Diagnosis**:
               - What's causing the problem?
               - How serious is it?
               - Will it spread?
            
            5. **Treatment Recommendations**:
               - Immediate actions to take
               - Organic/natural solutions
               - Chemical treatments (with specific product names available in Kenya and approximate costs)
               - Application methods
            
            6. **Prevention**:
               - How to prevent this in the future
               - Best practices for this crop
            
            7. **Timeline**: Expected recovery time with treatment
            
            Use simple language suitable for farmers. Be specific and actionable.
            If you're uncertain, say so and suggest consulting a local agricultural officer.
            """
            
            # Get analysis from Gemini
            analysis_text = self.gemini.analyze_image_with_text(
                image_data=image,
                prompt=prompt,
                language=language
            )
            
            # Structure the response
            return {
                'analysis': analysis_text,
                'location': location,
                'weather_context': weather_context,
                'timestamp': self._get_timestamp()
            }
            
        except Exception as e:
            raise Exception(f"Image analysis failed: {str(e)}")
    
    def compare_crop_stages(self, image_file1, image_file2) -> str:
        """
        Compare two crop images (e.g., before/after treatment)
        """
        try:
            image1 = Image.open(image_file1)
            image2 = Image.open(image_file2)
            
            prompt = """
            Compare these two crop images and identify:
            1. Changes in crop health
            2. Disease progression or recovery
            3. Growth differences
            4. Recommendations based on the changes observed
            """
            
            response = self.gemini.model.generate_content([prompt, image1, image2])
            return response.text
            
        except Exception as e:
            raise Exception(f"Image comparison failed: {str(e)}")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat()
