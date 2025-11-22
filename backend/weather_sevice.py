"""
Weather Service
Fetches weather data to provide context for farming advice
"""

import requests
from typing import Dict, Optional

class WeatherService:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize weather service
        Uses OpenWeather API (free tier) - optional for MVP
        """
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
    
    def get_weather(self, location: str) -> Optional[Dict]:
        """
        Get current weather for location
        
        Args:
            location: City name or coordinates
            
        Returns:
            Weather data dict or None if API not configured
        """
        if not self.api_key:
            # Return mock data if no API key
            return self._get_mock_weather()
        
        try:
            params = {
                'q': location,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(self.base_url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'temperature': data['main']['temp'],
                'humidity': data['main']['humidity'],
                'description': data['weather'][0]['description'],
                'wind_speed': data['wind']['speed']
            }
            
        except Exception as e:
            print(f"Weather API error: {str(e)}")
            return self._get_mock_weather()
    
    def _get_mock_weather(self) -> Dict:
        """Return mock weather data for MVP testing"""
        return {
            'temperature': 25,
            'humidity': 65,
            'description': 'Partly cloudy',
            'wind_speed': 3.5,
            'note': 'Mock data - configure WEATHER_API_KEY for live data'
          }
