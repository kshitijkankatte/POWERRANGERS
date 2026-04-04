"""
Integration service to connect frontend with backend
"""

import requests
import json
from typing import Optional, Dict, List

class SahanakBackendClient:
    """Client for Sahanak backend API"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
    
    def health_check(self) -> bool:
        """Check if backend is healthy"""
        try:
            response = requests.get(f"{self.base_url}/health")
            return response.status_code == 200
        except:
            return False
    
    def signup(self, user_data: dict) -> dict:
        """Register new user"""
        response = requests.post(
            f"{self.base_url}/api/auth/signup",
            json=user_data
        )
        
        if response.status_code != 200:
            raise Exception(f"Signup failed: {response.json()['detail']}")
        
        return response.json()
    
    def login(self, username: str, password: str) -> dict:
        """Login user"""
        response = requests.post(
            f"{self.base_url}/api/auth/login",
            json={"username": username, "password": password}
        )
        
        if response.status_code != 200:
            raise Exception(f"Login failed: {response.json()['detail']}")
        
        data = response.json()
        self.token = data.get('token')
        self.user_id = data.get('user', {}).get('id')
        
        return data
    
    def get_user_profile(self, user_id: int) -> dict:
        """Get user profile"""
        response = requests.get(
            f"{self.base_url}/api/users/{user_id}",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        
        if response.status_code != 200:
            raise Exception("Failed to get user profile")
        
        return response.json()
    
    def assess_symptoms(self, symptoms: List[str], other_symptoms: str = "") -> dict:
        """Assess symptoms"""
        response = requests.post(
            f"{self.base_url}/api/assess/symptoms?user_id={self.user_id}",
            json={
                "symptoms": symptoms,
                "other_symptoms": other_symptoms
            },
            headers={"Authorization": f"Bearer {self.token}"}
        )
        
        if response.status_code != 200:
            raise Exception("Assessment failed")
        
        return response.json()
    
    def get_assessment_history(self) -> List[dict]:
        """Get assessment history"""
        response = requests.get(
            f"{self.base_url}/api/assessments/{self.user_id}",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        
        if response.status_code != 200:
            raise Exception("Failed to get history")
        
        return response.json()
