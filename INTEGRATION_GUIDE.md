"""
Backend Integration Guide for Sahanak Frontend
This file explains how to integrate the frontend with the backend API
"""

# ==========================================
# INTEGRATION SUMMARY
# ==========================================

BACKEND_API_ENDPOINTS = {
    "Health Check": "GET /health",
    "User Registration": "POST /api/auth/signup",
    "User Login": "POST /api/auth/login",
    "Get User Profile": "GET /api/users/{user_id}",
    "Assess Symptoms": "POST /api/assess/symptoms?user_id={user_id}",
    "Get Assessment History": "GET /api/assessments/{user_id}",
}

# ==========================================
# FRONTEND TO BACKEND MAPPING
# ==========================================

"""
1. SIGNUP ENDPOINT
   Frontend: signup form submission
   Backend: POST /api/auth/signup
   
   Request Body:
   {
       "username": "user123",
       "password": "password123",
       "full_name": "John Doe",
       "gender": "Male",
       "age": 30,
       "location": "Mumbai, India",
       "allergies": "Penicillin",
       "medical_history": "Diabetes",
       "emergency_contact_1": "Mom: 9876543210",
       "emergency_contact_2": "Dad: 9876543211",
       "emergency_contact_3": "Sister: 9876543212"
   }
   
   Response:
   {
       "id": 1,
       "username": "user123",
       "full_name": "John Doe",
       ...
       "created_at": "2024-04-04T10:30:00"
   }

2. LOGIN ENDPOINT
   Frontend: login form submission
   Backend: POST /api/auth/login
   
   Request Body:
   {
       "username": "user123",
       "password": "password123"
   }
   
   Response:
   {
       "success": true,
       "user": {
           "id": 1,
           "username": "user123",
           "full_name": "John Doe",
           ...
       },
       "token": "token_1"
   }

3. SYMPTOM ASSESSMENT ENDPOINT
   Frontend: symptom selection page
   Backend: POST /api/assess/symptoms?user_id=1
   
   Request Body:
   {
       "symptoms": ["Fever", "Cough", "Headache"],
       "other_symptoms": "Patient reports mild body ache"
   }
   
   Response:
   {
       "urgency": "YELLOW",
       "urgency_label": "Urgent",
       "message": "Based on your symptoms...",
       "conditions": ["Common Cold", "Flu", "Bronchitis"],
       "specialist": "General Practitioner",
       "remedies": ["Rest", "Hydration", "Vitamin C"],
       "avoid": ["Smoking", "Strenuous activity"],
       "warning_signs": "Seek immediate care if...",
       "specialist_link": "general+practitioner"
   }

4. GET HISTORY ENDPOINT
   Frontend: history page view
   Backend: GET /api/assessments/{user_id}
   
   Response:
   [
       {
           "id": 1,
           "symptoms": ["Fever", "Cough"],
           "urgency": "YELLOW",
           "urgency_label": "Urgent",
           "message": "Assessment message...",
           "created_at": "2024-04-04T10:30:00"
       }
   ]
"""

# ==========================================
# FRONTEND INTEGRATION STEPS
# ==========================================

INTEGRATION_STEPS = """
1. REPLACE LOCALSTORAGE WITH API CALLS

   OLD (app.js):
   saveUser(user) {
       localStorage.setItem('sahanak_user', JSON.stringify(user));
   }
   
   NEW:
   async saveUser(user) {
       const response = await fetch('http://localhost:8001/api/auth/signup', {
           method: 'POST',
           headers: { 'Content-Type': 'application/json' },
           body: JSON.stringify(user)
       });
       return await response.json();
   }

2. REPLACE MOCK API WITH REAL API

   OLD (app.js):
   async callClaudeAPI(symptoms, extra) {
       return new Promise((resolve) => {
           setTimeout(() => {
               resolve(mockResponse);
           }, 1500);
       });
   }
   
   NEW:
   async assessSymptoms(symptoms, extra) {
       const response = await fetch(
           `http://localhost:8001/api/assess/symptoms?user_id=${this.currentUser.id}`,
           {
               method: 'POST',
               headers: { 'Content-Type': 'application/json' },
               body: JSON.stringify({
                   symptoms: symptoms,
                   other_symptoms: extra
               })
           }
       );
       return await response.json();
   }

3. UPDATE LOGIN FLOW

   OLD (app.js):
   const users = JSON.parse(localStorage.getItem('sahanak_users') || '[]');
   const found = users.find(u => u.username === user && u.password === pass);
   
   NEW:
   const response = await fetch('http://localhost:8001/api/auth/login', {
       method: 'POST',
       headers: { 'Content-Type': 'application/json' },
       body: JSON.stringify({
           username: username,
           password: password
       })
   });
   const data = await response.json();
   this.currentUser = data.user;
   localStorage.setItem('userToken', data.token);

4. LOAD HISTORY FROM BACKEND

   OLD (app.js):
   this.history = JSON.parse(localStorage.getItem(...) || '[]');
   
   NEW:
   async loadHistory() {
       const response = await fetch(
           `http://localhost:8001/api/assessments/${this.currentUser.id}`
       );
       return await response.json();
   }
"""

# ==========================================
# BACKEND DEPLOYMENT
# ==========================================

DEPLOYMENT_STEPS = """
1. SETUP ENVIRONMENT

   # Install dependencies
   cd backend
   pip install -r requirements.txt

2. SET API KEY

   # Edit .env file
   ANTHROPIC_API_KEY=your_actual_api_key_here

3. RUN BACKEND SERVER

   # On Windows PowerShell
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001
   
   # Or on Linux/Mac
   uvicorn main:app --reload --host 0.0.0.0 --port 8001

4. TEST ENDPOINTS

   # Health check
   curl http://localhost:8001/health
   
   # Signup
   curl -X POST http://localhost:8001/api/auth/signup \\
     -H "Content-Type: application/json" \\
     -d '{"username":"test","password":"test123","full_name":"Test User"}'

5. FRONTEND INTEGRATION

   # Update the Frontend URL in app.js
   BACKEND_URL = 'http://localhost:8001'

6. PRODUCTION DEPLOYMENT

   # Use Gunicorn for production
   gunicorn -w 4 -b 0.0.0.0:8001 main:app
   
   # Or use Docker
   docker build -t sahanak-backend .
   docker run -p 8001:8001 sahanak-backend
"""

# ==========================================
# API RESPONSE CODES
# ==========================================

RESPONSE_CODES = """
200 OK               - Request successful
201 Created          - Resource created
400 Bad Request      - Invalid input
401 Unauthorized     - Authentication failed
404 Not Found        - Resource not found
409 Conflict         - Username already exists
500 Server Error     - Internal server error
"""

# ==========================================
# DATABASE SCHEMA
# ==========================================

DATABASE_SCHEMA = """
USERS TABLE:
- id (INTEGER, PRIMARY KEY)
- username (TEXT, UNIQUE)
- password_hash (TEXT)
- full_name (TEXT)
- gender (TEXT)
- age (INTEGER)
- location (TEXT)
- allergies (TEXT)
- medical_history (TEXT)
- emergency_contact_1 (TEXT)
- emergency_contact_2 (TEXT)
- emergency_contact_3 (TEXT)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)

ASSESSMENTS TABLE:
- id (INTEGER, PRIMARY KEY)
- user_id (INTEGER, FOREIGN KEY)
- symptoms (TEXT - JSON array)
- urgency (TEXT)
- urgency_label (TEXT)
- message (TEXT)
- conditions (TEXT - JSON array)
- specialist (TEXT)
- remedies (TEXT - JSON array)
- avoid (TEXT - JSON array)
- warning_signs (TEXT)
- created_at (TIMESTAMP)
"""

# ==========================================
# SECURITY NOTES
# ==========================================

SECURITY_NOTES = """
1. PASSWORD HASHING
   - Passwords are hashed using SHA256
   - In production, use bcrypt or Argon2

2. CORS CONFIGURATION
   - Currently allows all origins for development
   - In production, specify exact frontend URL

3. API AUTHENTICATION
   - Simple token-based authentication
   - In production, use JWT with expiration

4. ENVIRONMENT VARIABLES
   - Store API keys in .env file
   - Never commit .env to version control

5. HTTPS
   - Use HTTPS in production
   - Ensure SSL certificates are valid

6. RATE LIMITING
   - Implement rate limiting in production
   - Prevent abuse of assessment endpoint
"""

print("Backend Integration Guide Loaded Successfully!")
print("See comments above for detailed integration instructions.")
