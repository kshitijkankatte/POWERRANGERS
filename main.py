from fastapi import FastAPI, HTTPException, Depends, status, Query, Request
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime, timedelta
import sqlite3
import hashlib
import json
from dotenv import load_dotenv
import os
from anthropic import Anthropic
import joblib
import pandas as pd
model = joblib.load('triage_model.pkl')
le = joblib.load('label_encoder.pkl')
columns = joblib.load('model_columns.pkl')
# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(title="Sahanak Backend API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Anthropic client
client = Anthropic()
CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Gemini API key (keep secret in .env)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Database setup
DB_PATH = "sahanak.db"

def init_db():
    """Initialize database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            gender TEXT,
            age INTEGER,
            location TEXT,
            personal_number TEXT,
            allergies TEXT,
            medical_history TEXT,
            emergency_contact_1 TEXT,
            emergency_contact_2 TEXT,
            emergency_contact_3 TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Lightweight migration: add columns if running against an older DB
    cursor.execute("PRAGMA table_info(users)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    if "personal_number" not in existing_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN personal_number TEXT")
    
    # Assessment History table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            symptoms TEXT NOT NULL,
            urgency TEXT,
            urgency_label TEXT,
            message TEXT,
            conditions TEXT,
            specialist TEXT,
            remedies TEXT,
            avoid TEXT,
            warning_signs TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

# =====================
# Pydantic Models
# =====================

class UserRegister(BaseModel):
    """User registration model"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    full_name: str
    gender: Optional[str] = None
    age: Optional[int] = None
    location: Optional[str] = None
    personal_number: str
    allergies: Optional[str] = None
    medical_history: Optional[str] = None
    emergency_contact_1: str
    emergency_contact_2: str
    emergency_contact_3: Optional[str] = None

class UserLogin(BaseModel):
    """User login model"""
    username: str
    password: str

class UserResponse(BaseModel):
    """User response model (no password)"""
    id: int
    username: str
    full_name: str
    gender: Optional[str]
    age: Optional[int]
    location: Optional[str]
    personal_number: Optional[str]
    allergies: Optional[str]
    medical_history: Optional[str]
    emergency_contact_1: Optional[str]
    emergency_contact_2: Optional[str]
    emergency_contact_3: Optional[str]
    created_at: str

class SymptomAssessment(BaseModel):
    """Symptom assessment request"""
    symptoms: List[str]
    other_symptoms: Optional[str] = ""
    time_duration: Optional[str] = "0-3 hrs"

class ClinicInfo(BaseModel):
    """Clinic/Hospital information"""
    name: str
    address: str

class EmergencyInfo(BaseModel):
    """Emergency specific information for HIGH risk"""
    message: str
    panic_button: bool
    panic_button_actions: Optional[List[str]] = None

class AssessmentResponse(BaseModel):
    """New structured assessment response model"""
    risk_level: str  # LOW | MEDIUM | HIGH
    title: str       # Low Risk / Moderate Risk / High Risk
    advice: List[str]
    symptoms_to_watch: List[str]
    clinics: Optional[List[ClinicInfo]] = None
    emergency: Optional[EmergencyInfo] = None

class AssessmentHistory(BaseModel):
    """Assessment history item (simplified for display)"""
    id: int
    symptoms: List[str]
    risk_level: str
    title: str
    created_at: str


class GeminiEnhanceRequest(BaseModel):
    """Request model for Gemini enrichment"""
    label: int = Field(..., ge=0, le=2)
    symptoms: List[str]
    user_location: Optional[str] = None


class GeminiEnhanceResponse(BaseModel):
    """Unified response for Gemini enrichment"""
    home_remedies: List[str] = []
    warning_symptoms: List[str] = []
    clinics: List[str] = []
    monitor_symptoms: List[str] = []


class PredictRequest(BaseModel):
    """Full ML triage prediction input matching the XGBoost model's feature schema."""
    # Demographics
    Age: Optional[int] = None
    Gender: Optional[str] = None  # 'M' or 'F'

    # Vitals
    Hemoglobin_g_dL: Optional[float] = None
    Blood_Sugar_mg_dL: Optional[float] = None
    Systolic_BP_mmHg: Optional[float] = None
    Diastolic_BP_mmHg: Optional[float] = None
    Cholesterol_mg_dL: Optional[float] = None
    O2_Saturation_pct: Optional[float] = None
    Heart_Rate_bpm: Optional[float] = None
    Respiratory_Rate_bpm: Optional[float] = None
    Body_Temp_C: Optional[float] = None

    # Symptom flags (1 = present, 0 = absent)
    Fever: Optional[int] = 0
    Cough: Optional[int] = 0
    Shortness_of_Breath: Optional[int] = 0
    Chest_Pain: Optional[int] = 0
    Dizziness: Optional[int] = 0
    Headache: Optional[int] = 0
    Nausea_Vomiting: Optional[int] = 0
    Abdominal_Pain: Optional[int] = 0
    Fatigue: Optional[int] = 0
    Loss_of_Consciousness: Optional[int] = 0

    # Medical history flags
    Diabetes_History: Optional[int] = 0
    Hypertension_History: Optional[int] = 0

    # Pain & duration
    Pain_Score_0_10: Optional[int] = 0
    Time_Duration: Optional[str] = "0-3 hrs"  # '0-3 hrs', '3-6 hrs', '6+ hrs'


class PredictResponse(BaseModel):
    """ML triage prediction output."""
    label: int = Field(..., ge=0, le=2)  # 0=Normal, 1=Moderate, 2=High
    label_name: str  # 'Normal', 'Moderate', or 'High'
    guidance: str
    reasons: List[str]

# =====================
# Helper Functions
# =====================

def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, password_hash: str) -> bool:
    """Verify password"""
    return hash_password(password) == password_hash

def get_user_from_db(username: str) -> Optional[dict]:
    """Get user from database"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    
    return dict(user) if user else None

def get_user_by_id(user_id: int) -> Optional[dict]:
    """Get user by ID"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    return dict(user) if user else None

def save_user_to_db(user_data: UserRegister) -> dict:
    """Save user to database"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    password_hash = hash_password(user_data.password)
    
    try:
        cursor.execute('''
            INSERT INTO users 
            (username, password_hash, full_name, gender, age, location, personal_number, allergies, 
             medical_history, emergency_contact_1, emergency_contact_2, emergency_contact_3)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_data.username,
            password_hash,
            user_data.full_name,
            user_data.gender,
            user_data.age,
            user_data.location,
            user_data.personal_number,
            user_data.allergies,
            user_data.medical_history,
            user_data.emergency_contact_1,
            user_data.emergency_contact_2,
            user_data.emergency_contact_3
        ))
        conn.commit()
        
        # Get the created user
        cursor.execute("SELECT * FROM users WHERE username = ?", (user_data.username,))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            raise HTTPException(status_code=500, detail="Failed to retrieve created user")
        
        return dict(user)
        
    except sqlite3.IntegrityError as e:
        conn.close()
        raise HTTPException(status_code=409, detail="Username already exists")

def save_assessment_to_db(user_id: int, symptoms: List[str], assessment: dict):
    """Save assessment to database mapping new structure to old columns for compatibility"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Map new fields to existing columns for convenience
    # risk_level -> urgency, title -> urgency_label, advice -> remedies (json), 
    # symptoms_to_watch -> warning_signs (json)
    cursor.execute('''
        INSERT INTO assessments 
        (user_id, symptoms, urgency, urgency_label, message, remedies, warning_signs)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id,
        json.dumps(symptoms),
        assessment.get('risk_level'),
        assessment.get('title'),
        json.dumps(assessment), # Store entire object in message for retrieval
        json.dumps(assessment.get('advice', [])),
        json.dumps(assessment.get('symptoms_to_watch', []))
    ))
    conn.commit()
    conn.close()

def get_user_assessments(user_id: int) -> List[dict]:
    """Get user assessment history mapping old columns to new structure"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM assessments WHERE user_id = ? ORDER BY created_at DESC
    ''', (user_id,))
    raw_assessments = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    processed = []
    for a in raw_assessments:
        try:
            # Try parsing the raw JSON from the 'message' column if it contains the full object
            data = json.loads(a['message'])
            processed.append({
                "id": a['id'],
                "symptoms": json.loads(a['symptoms']),
                "risk_level": data.get('risk_level', a['urgency']),
                "title": data.get('title', a['urgency_label']),
                "created_at": a['created_at']
            })
        except:
            # Fallback for old records
            processed.append({
                "id": a['id'],
                "symptoms": json.loads(a['symptoms']),
                "risk_level": a['urgency'] or "LOW",
                "title": a['urgency_label'] or "Low Risk",
                "created_at": a['created_at']
            })
    return processed


def _extract_json_object(text: str) -> dict:
    """Best-effort extraction of a JSON object from model output."""
    if not text:
        raise ValueError("Empty response")
    start = text.find("{")
    end = text.rfind("}") + 1
    if start == -1 or end <= start:
        raise ValueError("No JSON object found")
    return json.loads(text[start:end])


def _gemini_generate_json(prompt: str, use_search: bool) -> dict:
    """Generate JSON using Gemini; tries google-genai first, falls back to google-generativeai."""
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not set")

    # Preferred SDK: google-genai (supports Google Search tool)
    try:
        from google import genai  # type: ignore
        from google.genai import types  # type: ignore

        client = genai.Client(api_key=GEMINI_API_KEY)
        tools = None
        if use_search:
            tools = [types.Tool(google_search=types.GoogleSearch())]

        resp = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            tools=tools,
        )
        text = getattr(resp, "text", None) or ""
        return _extract_json_object(text)
    except Exception:
        pass

    # Fallback SDK: google-generativeai
    import google.generativeai as genai  # type: ignore

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash")
    resp = model.generate_content(prompt)
    text = getattr(resp, "text", None) or ""
    return _extract_json_object(text)

# =====================
# API Endpoints
# =====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Sahanak Backend API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

# =====================
# Authentication Endpoints
# =====================

@app.post("/api/auth/signup", response_model=UserResponse)
async def signup(user_data: UserRegister):
    """Register a new user"""
    # Validate input
    if len(user_data.username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters")
    if len(user_data.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    # Check if user exists
    existing_user = get_user_from_db(user_data.username)
    if existing_user:
        raise HTTPException(status_code=409, detail="Username already exists")
    
    # Save user
    user = save_user_to_db(user_data)
    
    return {
        "id": user['id'],
        "username": user['username'],
        "full_name": user['full_name'],
        "gender": user['gender'],
        "age": user['age'],
        "location": user['location'],
        "personal_number": user['personal_number'],
        "allergies": user['allergies'],
        "medical_history": user['medical_history'],
        "emergency_contact_1": user['emergency_contact_1'],
        "emergency_contact_2": user['emergency_contact_2'],
        "emergency_contact_3": user['emergency_contact_3'],
        "created_at": user['created_at']
    }

@app.post("/api/auth/login", response_model=dict)
async def login(credentials: UserLogin):
    """Login user"""
    # Get user from database
    user = get_user_from_db(credentials.username)
    
    if not user or not verify_password(credentials.password, user['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    return {
        "success": True,
        "user": {
            "id": user['id'],
            "username": user['username'],
            "full_name": user['full_name'],
            "gender": user['gender'],
            "age": user['age'],
            "location": user['location'],
            "personal_number": user.get('personal_number'),
            "allergies": user['allergies'],
            "medical_history": user['medical_history'],
            "emergency_contact_1": user['emergency_contact_1'],
            "emergency_contact_2": user['emergency_contact_2'],
            "emergency_contact_3": user['emergency_contact_3'],
        },
        "token": f"token_{user['id']}"  # Simple token (use JWT in production)
    }

@app.get("/api/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """Get user profile"""
    user = get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user['id'],
        "username": user['username'],
        "full_name": user['full_name'],
        "gender": user['gender'],
        "age": user['age'],
        "location": user['location'],
        "personal_number": user.get('personal_number'),
        "allergies": user['allergies'],
        "medical_history": user['medical_history'],
        "emergency_contact_1": user['emergency_contact_1'],
        "emergency_contact_2": user['emergency_contact_2'],
        "emergency_contact_3": user['emergency_contact_3'],
        "created_at": user['created_at']
    }

# =====================
# Symptom Assessment Endpoints
# =====================

@app.post("/api/assess/symptoms", response_model=AssessmentResponse)
async def assess_symptoms(request: SymptomAssessment, user_id: int = Query(...)):
    """Assess symptoms using Gemini 2.0 Flash with strict risk-level guidance"""
    
    # Get user
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 1. Resolve ML Risk Level first
    symptom_map = {
        "Fever": "Fever", "Cough": "Cough", "Chest Pain": "Chest_Pain",
        "Shortness of Breath": "Shortness_of_Breath", "Dizziness": "Dizziness",
        "Headache": "Headache", "Nausea": "Nausea_Vomiting", "Vomiting": "Nausea_Vomiting",
        "Abdominal Pain": "Abdominal_Pain", "Fatigue": "Fatigue",
        "Chest Tightness": "Chest_Pain"
    }
    
    mapped_symptoms = {}
    valid_fields = PredictRequest.__fields__.keys()
    for s in request.symptoms:
        if s in symptom_map:
            target_field = symptom_map[s]
            if target_field in valid_fields:
                mapped_symptoms[target_field] = 1
        else:
            snake_s = s.replace(' ', '_')
            if snake_s in valid_fields:
                mapped_symptoms[snake_s] = 1
                
    # Intelligent Defaults for Safety Overrides
    if mapped_symptoms.get("Chest_Pain", 0) == 1:
        mapped_symptoms["Pain_Score_0_10"] = 8
    elif len(request.symptoms) >= 4:
        mapped_symptoms["Pain_Score_0_10"] = 5
    else:
        mapped_symptoms["Pain_Score_0_10"] = 2
            
    try:
        pred_req = PredictRequest(
            Age=user.get('age'),
            Gender=user.get('gender')[0].upper() if user.get('gender') else 'M',
            Time_Duration=request.time_duration,
            **mapped_symptoms
        )
        pred_res = _run_triage_model(pred_req)
        ml_risk_label = pred_res['label']
    except Exception:
        ml_risk_label = 1
        
    risk_level_str = ["LOW", "MEDIUM", "HIGH"][ml_risk_label]
    
    # 2. Call Gemini 2.0 Flash using the requested prompt
    symptoms_list = ", ".join(request.symptoms)
    location = user.get('location') or 'nearby'
    input_data = f"Risk Level: {risk_level_str}\nPatient Symptoms: {symptoms_list}\nPatient Location: {location}"

    # Use existing helper (which we'll refine to handle instructions separately or just pass as one prompt)
    prompt = f"""
System Instruction:
You are a medical triage assistant. You will receive a risk level, patient symptoms, and the patient's city or area. Use your own medical knowledge to generate advice, remedial steps, and symptom warnings. For clinics, suggest real and commonly known hospitals or clinics in the patient's city that are relevant to their condition. Do NOT diagnose. Return ONLY strict JSON with no explanation, no markdown, no code fences. 

IF risk_level is LOW: 
- title: Low Risk
- advice: simple home remedies and self-care steps based on symptoms
- symptoms_to_watch: warning signs to monitor
- clinics: []
- emergency: null

IF risk_level is MEDIUM: 
- title: Moderate Risk
- advice: precautionary steps
- symptoms_to_watch: symptoms to monitor
- clinics: 3 real commonly known clinics or hospitals in the patient's city ({location}) relevant to the condition including name and address
- emergency: null

IF risk_level is HIGH: 
- title: High Risk
- advice: "Seek emergency care immediately" followed by urgent steps
- symptoms_to_watch: critical warning signs
- clinics: 2 nearest known emergency hospitals in the patient's city ({location})
- emergency: {{ "message": "Tailored urgent message...", "panic_button": true, "panic_button_actions": ["Notify pre-saved emergency contacts...", "Share live location...", "Call ambulance services immediately"] }}

Input Details:
{input_data}

OUTPUT FORMAT (STRICT JSON):
{{
  "risk_level": "{risk_level_str}",
  "title": "string",
  "advice": ["array of strings"],
  "symptoms_to_watch": ["array of strings"],
  "clinics": [{{ "name": "string", "address": "string" }}],
  "emergency": {{
    "message": "string",
    "panic_button": true,
    "panic_button_actions": ["array of strings"]
  }}
}}
"""

    try:
        assessment = _gemini_generate_json(prompt, use_search=False)
        # Final validation of key fields
        if not assessment.get("risk_level"): assessment["risk_level"] = risk_level_str
    except Exception as e:
        print(f"Gemini Triage Error: {e}")
        # Robust fallback
        assessment = {
            "risk_level": risk_level_str,
            "title": "Low Risk" if risk_level_str == "LOW" else "Moderate Risk" if risk_level_str == "MEDIUM" else "High Risk",
            "advice": ["Rest and stay hydrated"],
            "symptoms_to_watch": ["Persistent pain", "Fever over 103"],
            "clinics": [],
            "emergency": None if risk_level_str != "HIGH" else {
                "message": "URGENT: Call 911 or go to the nearest ER.",
                "panic_button": True,
                "panic_button_actions": ["Contact family", "Call Ambulance"]
            }
        }
    
    save_assessment_to_db(user_id, request.symptoms, assessment)
    return AssessmentResponse(**assessment)

@app.get("/api/assessments/{user_id}", response_model=List[AssessmentHistory])
async def get_assessments(user_id: int):
    """Get user assessment history"""
    
    # Verify user exists
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    assessments = get_user_assessments(user_id)
    
    return [
        {
            "id": a['id'],
            "symptoms": a['symptoms'],
            "urgency": a['urgency'],
            "urgency_label": a['urgency_label'],
            "message": a['message'],
            "created_at": a['created_at']
        }
        for a in assessments
    ]


@app.post("/api/gemini/enhance", response_model=GeminiEnhanceResponse)
async def gemini_enhance(req: GeminiEnhanceRequest):
    """Gemini enrichment for low/moderate risk results."""
    if req.label == 2:
        # High-risk: keep it fast and direct; no Gemini call.
        return GeminiEnhanceResponse()

    symptom_list = ", ".join(req.symptoms or [])
    user_location = (req.user_location or "").strip()

    if req.label == 0:
        prompt = (
            "The patient has the following symptoms: "
            f"{symptom_list}. "
            "Suggest effective home remedies they can try right now, and list 5 warning symptoms "
            "they should watch out for that would indicate their condition is getting worse. "
            "Return JSON ONLY with this exact shape:\n"
            "{\n"
            "  \"home_remedies\": [\"...\"],\n"
            "  \"warning_symptoms\": [\"...\"]\n"
            "}\n"
        )
        try:
            data = _gemini_generate_json(prompt, use_search=True)
            return GeminiEnhanceResponse(
                home_remedies=list(data.get("home_remedies", []) or []),
                warning_symptoms=list(data.get("warning_symptoms", []) or []),
            )
        except Exception:
            return GeminiEnhanceResponse(
                home_remedies=["Rest and stay hydrated", "Monitor temperature", "Avoid strenuous activity"],
                warning_symptoms=["Worsening shortness of breath", "Chest pain", "Confusion", "Severe dehydration", "Persistent high fever"],
            )

    # label == 1
    prompt = (
        "The patient has the following symptoms: "
        f"{symptom_list} "
        f"and is located near {user_location or 'their area'}. "
        "Find nearby clinics or urgent care centers they can visit today. "
        "Also list 5 symptoms to monitor that would mean they need emergency care. "
        "Return JSON ONLY with this exact shape:\n"
        "{\n"
        "  \"clinics\": [\"Name - Address (or area)\"],\n"
        "  \"monitor_symptoms\": [\"...\"]\n"
        "}\n"
    )
    try:
        data = _gemini_generate_json(prompt, use_search=True)
        return GeminiEnhanceResponse(
            clinics=list(data.get("clinics", []) or []),
            monitor_symptoms=list(data.get("monitor_symptoms", []) or []),
        )
    except Exception:
        return GeminiEnhanceResponse(
            clinics=[
                f"Search: urgent care near {user_location or 'you'}",
                f"Search: walk-in clinic near {user_location or 'you'}",
            ],
            monitor_symptoms=["Chest pain", "Severe shortness of breath", "Fainting", "Blue lips/face", "Rapid worsening"],
        )


def _run_triage_model(req: PredictRequest) -> dict:
    """Run the XGBoost triage model with safety overrides.
    Returns a dict with label (int 0-2), label_name, guidance, and reasons.
    """
    reasons = []
    overrides_triggered = []

    # -----------------------------------------------
    # 1) SAFETY OVERRIDES (critical vitals)
    # -----------------------------------------------
    o2 = req.O2_Saturation_pct
    rr = req.Respiratory_Rate_bpm
    hr = req.Heart_Rate_bpm
    duration = req.Time_Duration or "0-3 hrs"
    pain = req.Pain_Score_0_10 or 0

    if o2 is not None and o2 < 90:
        overrides_triggered.append("Low oxygen saturation (<90%)")
    if rr is not None and rr > 22:
        overrides_triggered.append("High respiratory rate (>22 bpm)")
    if hr is not None and hr > 130:
        overrides_triggered.append("Very high heart rate (>130 bpm)")
    
    # Critical symptom overrides (independent of duration)
    if req.Chest_Pain == 1:
        overrides_triggered.append("Chest pain reported - Auto-escalating to Emergency protocol")
    if req.Shortness_of_Breath == 1:
        overrides_triggered.append("Shortness of breath reported - Auto-escalating to Emergency protocol")
    if req.Loss_of_Consciousness == 1:
        overrides_triggered.append("Loss of consciousness reported - Auto-escalating to Emergency protocol")
        
    # Prolonged severe pain
    if duration == "6+ hrs" and pain >= 8:
        overrides_triggered.append("Severe pain for prolonged duration (6+ hrs)")

    if overrides_triggered:
        reasons.extend(overrides_triggered)
        return {
            "label": 2,
            "label_name": "High",
            "guidance": "High Risk 🚨 – Seek immediate medical attention",
            "reasons": reasons,
        }

    # -----------------------------------------------
    # 2) ML PREDICTION via XGBoost model
    # -----------------------------------------------
    try:
        data = {
            "Age": req.Age,
            "Gender": req.Gender,
            "Hemoglobin_g_dL": req.Hemoglobin_g_dL,
            "Blood_Sugar_mg_dL": req.Blood_Sugar_mg_dL,
            "Systolic_BP_mmHg": req.Systolic_BP_mmHg,
            "Diastolic_BP_mmHg": req.Diastolic_BP_mmHg,
            "Cholesterol_mg_dL": req.Cholesterol_mg_dL,
            "O2_Saturation_pct": req.O2_Saturation_pct,
            "Heart_Rate_bpm": req.Heart_Rate_bpm,
            "Respiratory_Rate_bpm": req.Respiratory_Rate_bpm,
            "Body_Temp_C": req.Body_Temp_C,
            "Fever": req.Fever or 0,
            "Cough": req.Cough or 0,
            "Shortness_of_Breath": req.Shortness_of_Breath or 0,
            "Chest_Pain": req.Chest_Pain or 0,
            "Dizziness": req.Dizziness or 0,
            "Headache": req.Headache or 0,
            "Nausea_Vomiting": req.Nausea_Vomiting or 0,
            "Abdominal_Pain": req.Abdominal_Pain or 0,
            "Fatigue": req.Fatigue or 0,
            "Loss_of_Consciousness": req.Loss_of_Consciousness or 0,
            "Diabetes_History": req.Diabetes_History or 0,
            "Hypertension_History": req.Hypertension_History or 0,
            "Pain_Score_0_10": req.Pain_Score_0_10 or 0,
            "Time_Duration": req.Time_Duration or "0-3 hrs",
        }

        df_new = pd.DataFrame([data])
        df_new = pd.get_dummies(df_new)
        df_new = df_new.reindex(columns=columns, fill_value=0)

        pred = model.predict(df_new)
        label_name = le.inverse_transform(pred)[0]  # 'Normal', 'Moderate', or 'High'

        # Map label_name → integer label (0=Normal, 1=Moderate, 2=High)
        label_map = {"Normal": 0, "Moderate": 1, "High": 2}
        label_int = label_map.get(label_name, 1)

        # Baseline Override: If no major symptoms mapped and it predicts Moderate, downgrade to Normal (Low Risk)
        has_major_symptoms = any([
            req.Fever, req.Cough, req.Shortness_of_Breath, req.Chest_Pain, 
            req.Dizziness, req.Headache, req.Nausea_Vomiting, req.Abdominal_Pain, 
            req.Fatigue, req.Loss_of_Consciousness
        ])
        
        if not has_major_symptoms and label_int == 1:
            label_int = 0
            label_name = "Normal"

    except Exception as e:
        print(f"Triage model inference error: {e}")
        # Fallback: conservative moderate risk
        label_name = "Moderate"
        label_int = 1

    # -----------------------------------------------
    # 3) LIGHT REASONS (informational, not diagnostic)
    # -----------------------------------------------
    if o2 is not None and o2 < 94:
        reasons.append("Oxygen saturation slightly low")
    if hr is not None and hr > 110:
        reasons.append("Elevated heart rate")
    if rr is not None and rr > 20:
        reasons.append("Respiratory rate above normal")
    if duration == "3-6 hrs":
        reasons.append("Symptoms persisting (3–6 hrs)")
    if duration == "6+ hrs":
        reasons.append("Symptoms prolonged (6+ hrs)")
    if req.Fever:
        reasons.append("Fever present")
    if req.Chest_Pain:
        reasons.append("Chest pain reported")
    if req.Loss_of_Consciousness:
        reasons.append("Loss of consciousness reported")
    if req.Shortness_of_Breath:
        reasons.append("Shortness of breath reported")

    # -----------------------------------------------
    # 4) GUIDANCE
    # -----------------------------------------------
    if label_name == "High":
        guidance = "High Risk 🚨 – Seek immediate medical attention"
    elif label_name == "Moderate":
        guidance = "Moderate Risk ⚠️ – Consult a doctor soon"
    else:
        guidance = "Low Risk ✅ – Monitor symptoms at home"

    return {
        "label": label_int,
        "label_name": label_name,
        "guidance": guidance,
        "reasons": reasons,
    }


@app.post("/api/predict", response_model=PredictResponse)
async def predict(req: PredictRequest):
    """Predict triage risk using the trained XGBoost model.

    Accepts structured medical vitals and symptom flags.
    Returns a risk label (0=Normal, 1=Moderate, 2=High), human-readable
    guidance, and a list of clinical reasons informing the decision.
    Safety override rules fire first for critical vitals; the ML model
    is used for all remaining cases.
    """
    result = _run_triage_model(req)
    return PredictResponse(**result)


@app.post("/api/triage")
async def triage(req: PredictRequest):
    """Detailed triage endpoint – same logic as /api/predict but returns
    the full result dict directly (useful for richer frontend displays).
    """
    return _run_triage_model(req)

# =====================
# Error Handlers
# =====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat(),
        },
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler"""
    print(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.now().isoformat(),
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Request validation handler (422) with consistent error shape."""
    errors = exc.errors() if hasattr(exc, "errors") else []
    message = "Validation error"
    if errors:
        first = errors[0]
        msg = first.get("msg")
        loc = first.get("loc")
        if loc:
            message = f"{'.'.join(str(x) for x in loc)}: {msg or 'Invalid input'}"
        else:
            message = msg or message

    return JSONResponse(
        status_code=422,
        content={
            "error": message,
            "status_code": 422,
            "details": errors,
            "timestamp": datetime.now().isoformat(),
        },
    )

# Serve Frontend Static Files (at the end to avoid masking routes)
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "POWERRANGERS-main", "hackathon"))

@app.get("/")
async def read_index():
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse(status_code=404, content={"error": "index.html not found"})

if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="static")
else:
    print(f"Warning: Frontend directory not found at {frontend_dir}")

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("BACKEND_HOST") or os.getenv("SERVER_HOST") or "0.0.0.0"
    port_raw = os.getenv("BACKEND_PORT") or os.getenv("SERVER_PORT") or os.getenv("PORT") or "8001"
    try:
        port = int(port_raw)
    except ValueError:
        port = 8001

    uvicorn.run(app, host=host, port=port)
