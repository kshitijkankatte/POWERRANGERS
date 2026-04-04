# API Testing Guide

Complete testing guide for Sahanak Backend API with curl examples, expected responses, and validation steps.

---

## Table of Contents

1. [Setup](#setup)
2. [Health Check](#health-check)
3. [User Management](#user-management)
4. [Symptom Assessment](#symptom-assessment)
5. [Assessment History](#assessment-history)
6. [Error Handling](#error-handling)
7. [Testing Scenarios](#testing-scenarios)

---

## Setup

**Ensure backend is running:**
```bash
cd backend
python -m uvicorn main:app --reload
```

**Backend URL:** `http://localhost:8001`

**Store for reference:**
```
BASE_URL=http://localhost:8001
USER_ID=1
TOKEN=token_1  # Will be provided by login endpoint
```

---

## Health Check

### Endpoint: GET /health

**Description:** Verify backend is running and healthy

**Request:**
```bash
curl -X GET http://localhost:8001/health
```

**Expected Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "Sahanak Backend API",
  "version": "1.0.0",
  "timestamp": "2024-04-04T10:30:00"
}
```

**Validation:** Status should be "healthy" ✅

---

## User Management

### 1. User Registration (Signup)

**Endpoint:** `POST /api/auth/signup`

**Description:** Create new user account with profile information

**Request:**
```bash
curl -X POST http://localhost:8001/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "securepassword123",
    "full_name": "John Doe",
    "gender": "Male",
    "age": 30,
    "location": "Mumbai, India",
    "allergies": "Penicillin",
    "medical_history": "Type 2 Diabetes",
    "emergency_contact_1": "Mom: 9876543210",
    "emergency_contact_2": "Dad: 9876543211",
    "emergency_contact_3": "Sister: 9876543212"
  }'
```

**Expected Response (200 OK):**
```json
{
  "id": 1,
  "username": "john_doe",
  "full_name": "John Doe",
  "gender": "Male",
  "age": 30,
  "location": "Mumbai, India",
  "allergies": "Penicillin",
  "medical_history": "Type 2 Diabetes",
  "emergency_contact_1": "Mom: 9876543210",
  "emergency_contact_2": "Dad: 9876543211",
  "emergency_contact_3": "Sister: 9876543212"
}
```

**Validation Points:**
- ✅ Response contains user ID
- ✅ All fields returned correctly
- ✅ User ID should be auto-incremented (1, 2, 3...)

**Error Cases:**

**Duplicate username (400):**
```json
{
  "error": "Username already exists",
  "status_code": 400
}
```

**Invalid input (422):**
```json
{
  "error": "Invalid input data",
  "status_code": 422
}
```

---

### 2. User Login

**Endpoint:** `POST /api/auth/login`

**Description:** Authenticate user and get access token

**Request:**
```bash
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "securepassword123"
  }'
```

**Expected Response (200 OK):**
```json
{
  "success": true,
  "user": {
    "id": 1,
    "username": "john_doe",
    "full_name": "John Doe",
    "age": 30,
    "gender": "Male",
    "location": "Mumbai, India",
    "allergies": "Penicillin",
    "medical_history": "Type 2 Diabetes",
    "emergency_contact_1": "Mom: 9876543210",
    "emergency_contact_2": "Dad: 9876543211",
    "emergency_contact_3": "Sister: 9876543212"
  },
  "token": "token_1"
}
```

**Validation Points:**
- ✅ login succeeds with correct credentials
- ✅ Token returned (use for subsequent requests)
- ✅ User data matches signup

**Error Cases:**

**Invalid credentials (401):**
```json
{
  "error": "Invalid credentials",
  "status_code": 401
}
```

**User not found (401):**
```json
{
  "error": "User not found",
  "status_code": 401
}
```

---

### 3. Get User Profile

**Endpoint:** `GET /api/users/{user_id}`

**Description:** Retrieve user profile information

**Request:**
```bash
curl -X GET http://localhost:8001/api/users/1
```

**Expected Response (200 OK):**
```json
{
  "id": 1,
  "username": "john_doe",
  "full_name": "John Doe",
  "age": 30,
  "gender": "Male",
  "location": "Mumbai, India",
  "allergies": "Penicillin",
  "medical_history": "Type 2 Diabetes",
  "emergency_contact_1": "Mom: 9876543210",
  "emergency_contact_2": "Dad: 9876543211",
  "emergency_contact_3": "Sister: 9876543212"
}
```

**Validation Points:**
- ✅ User data is complete
- ✅ Correct user ID matched
- ✅ All profile fields present

**Error Cases:**

**User not found (404):**
```json
{
  "error": "User not found",
  "status_code": 404
}
```

---

## Symptom Assessment

### Endpoint: POST /api/assess/symptoms

**Description:** Assess symptoms using Claude AI and return urgency/recommendations

**Required Query Parameter:** `user_id` (integer)

#### Test Case 1: RED Urgency (Emergency)

**Request:**
```bash
curl -X POST "http://localhost:8001/api/assess/symptoms?user_id=1" \
  -H "Content-Type: application/json" \
  -d '{
    "symptoms": ["Chest Pain", "Difficulty Breathing", "Loss of Consciousness"],
    "other_symptoms": "Patient collapsed 5 minutes ago"
  }'
```

**Expected Response (200 OK):**
```json
{
  "id": 1,
  "user_id": 1,
  "urgency": "RED",
  "urgency_label": "Emergency",
  "message": "Based on your symptoms of chest pain, difficulty breathing, and loss of consciousness, this is a medical emergency...",
  "conditions": ["Acute Myocardial Infarction", "Pulmonary Embolism", "Severe Arrhythmia"],
  "specialist": "Cardiologist",
  "remedies": ["Call Emergency Services Immediately", "Perform CPR if trained", "Keep patient calm"],
  "avoid": ["Physical exertion", "Medication without medical guidance"],
  "warning_signs": "Patient showing RED urgency - seek emergency services IMMEDIATELY",
  "specialist_link": "cardiologist",
  "created_at": "2024-04-04T10:35:00"
}
```

**Validation Points:**
- ✅ Urgency is "RED"
- ✅ Emergency message is clear
- ✅ Specialist is cardiology-related
- ✅ Panic button will trigger on frontend

---

#### Test Case 2: YELLOW Urgency (Urgent)

**Request:**
```bash
curl -X POST "http://localhost:8001/api/assess/symptoms?user_id=1" \
  -H "Content-Type: application/json" \
  -d '{
    "symptoms": ["High Fever", "Persistent Cough", "Headache"],
    "other_symptoms": "Fever has been 39C for 3 days, cough is getting worse"
  }'
```

**Expected Response (200 OK):**
```json
{
  "id": 2,
  "user_id": 1,
  "urgency": "YELLOW",
  "urgency_label": "Urgent",
  "message": "Your symptoms suggest a respiratory infection that needs urgent attention...",
  "conditions": ["Pneumonia", "Severe Bronchitis", "Influenza"],
  "specialist": "Pulmonologist",
  "remedies": ["See doctor within 24 hours", "Rest and hydration", "Monitor oxygen levels"],
  "avoid": ["Smoking", "Strenuous activity"],
  "warning_signs": "Seek emergency if: difficulty breathing, chest pain, confusion",
  "specialist_link": "pulmonologist",
  "created_at": "2024-04-04T10:40:00"
}
```

**Validation Points:**
- ✅ Urgency is "YELLOW"
- ✅ Recommends urgent care (within 24 hours)
- ✅ Warning signs provided
- ✅ No panic button on frontend

---

#### Test Case 3: GREEN Urgency (Routine)

**Request:**
```bash
curl -X POST "http://localhost:8001/api/assess/symptoms?user_id=1" \
  -H "Content-Type: application/json" \
  -d '{
    "symptoms": ["Mild Headache", "Slight Fatigue"],
    "other_symptoms": "Symptoms started this morning, no other issues"
  }'
```

**Expected Response (200 OK):**
```json
{
  "id": 3,
  "user_id": 1,
  "urgency": "GREEN",
  "urgency_label": "Routine",
  "message": "Your symptoms appear to be minor. Routine care recommended...",
  "conditions": ["Common Headache", "Mild Fatigue", "Possible Stress"],
  "specialist": "General Practitioner",
  "remedies": ["Rest", "Hydration", "Over-the-counter pain relief if needed"],
  "avoid": ["Stressful activities"],
  "warning_signs": "Consult doctor if symptoms persist beyond 48 hours",
  "specialist_link": "general+practitioner",
  "created_at": "2024-04-04T10:45:00"
}
```

**Validation Points:**
- ✅ Urgency is "GREEN"
- ✅ Routine care suggested
- ✅ No emergency action needed
- ✅ Affordable recommendations

---

### Error Cases for Assessment

**Missing user_id query parameter (422):**
```bash
curl -X POST "http://localhost:8001/api/assess/symptoms" \
  -H "Content-Type: application/json" \
  -d '{"symptoms": ["Fever"]}'
```

Response (422):
```json
{
  "error": "user_id query parameter is required",
  "status_code": 422
}
```

**User not found (404):**
```bash
curl -X POST "http://localhost:8001/api/assess/symptoms?user_id=999" \
  -H "Content-Type: application/json" \
  -d '{"symptoms": ["Fever"]}'
```

Response (404):
```json
{
  "error": "User not found",
  "status_code": 404
}
```

**Empty symptoms (422):**
```bash
curl -X POST "http://localhost:8001/api/assess/symptoms?user_id=1" \
  -H "Content-Type: application/json" \
  -d '{"symptoms": []}'
```

Response (422):
```json
{
  "error": "At least one symptom is required",
  "status_code": 422
}
```

---

## Assessment History

### Endpoint: GET /api/assessments/{user_id}

**Description:** Retrieve all past assessments for a user

**Request:**
```bash
curl -X GET http://localhost:8001/api/assessments/1
```

**Expected Response (200 OK):**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "symptoms": ["Chest Pain", "Difficulty Breathing"],
    "urgency": "RED",
    "urgency_label": "Emergency",
    "message": "Medical emergency - call services immediately",
    "conditions": ["Myocardial Infarction"],
    "specialist": "Cardiologist",
    "created_at": "2024-04-04T10:35:00"
  },
  {
    "id": 2,
    "user_id": 1,
    "symptoms": ["High Fever", "Cough"],
    "urgency": "YELLOW",
    "urgency_label": "Urgent",
    "message": "Respiratory infection - see doctor within 24 hours",
    "conditions": ["Pneumonia"],
    "specialist": "Pulmonologist",
    "created_at": "2024-04-04T10:40:00"
  }
]
```

**Validation Points:**
- ✅ Returns array of assessments
- ✅ Most recent first (if sorted by date)
- ✅ All assessment details included
- ✅ Timestamps present

**Error Cases:**

**User not found (404):**
```json
{
  "error": "User not found",
  "status_code": 404
}
```

**No assessments (200 OK - empty array):**
```json
[]
```

---

## Error Handling

### Common HTTP Status Codes

| Status | Meaning | Example |
|--------|---------|---------|
| 200 | Success | User created successfully |
| 201 | Created | Assessment recorded |
| 400 | Bad Request | Duplicate username |
| 401 | Unauthorized | Wrong password |
| 404 | Not Found | User doesn't exist |
| 422 | Validation Error | Missing required field |
| 500 | Server Error | Unexpected error |

### Standard Error Response Format

```json
{
  "error": "Descriptive error message",
  "status_code": 400,
  "timestamp": "2024-04-04T10:50:00",
  "details": "Additional context if available"
}
```

---

## Testing Scenarios

### Scenario 1: Complete User Journey

**Step 1: Create Account**
```bash
curl -X POST http://localhost:8001/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "password": "alice123",
    "full_name": "Alice Smith",
    "age": 28
  }'
# Save user_id = 1
```

**Step 2: Login**
```bash
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "password": "alice123"
  }'
# Verify token received
```

**Step 3: Assess Symptoms**
```bash
curl -X POST "http://localhost:8001/api/assess/symptoms?user_id=1" \
  -H "Content-Type: application/json" \
  -d '{
    "symptoms": ["Fever", "Cough"],
    "other_symptoms": ""
  }'
# Check urgency level
```

**Step 4: View History**
```bash
curl -X GET http://localhost:8001/api/assessments/1
# Verify assessment recorded
```

### Scenario 2: Emergency Response

Test RED urgency trigger:
```bash
curl -X POST "http://localhost:8001/api/assess/symptoms?user_id=1" \
  -H "Content-Type: application/json" \
  -d '{
    "symptoms": ["Severe Chest Pain", "Unconsciousness", "Severe Bleeding"],
    "other_symptoms": "Patient unresponsive"
  }'
```

**Expected:** urgency = "RED" ✅

### Scenario 3: Multiple Users

Create users 2 and 3, each with different medical histories, login each, and perform assessments to ensure data isolation.

---

## Performance Testing

### Load Testing (Optional)

Test response time with simple health check:
```bash
# Single request
time curl -s http://localhost:8001/health > /dev/null

# Multiple requests (Windows: use for loop)
for i in {1..10}; do
  curl -s http://localhost:8001/health > /dev/null
done
```

**Expected:** <100ms per request ✅

---

## Postman Collection

Instead of manual curl commands, import this Postman collection:

1. Create new environment with variables:
   - `base_url`: http://localhost:8001
   - `user_id`: 1
   - `token`: (auto-populated after login)

2. Create requests for each endpoint

3. Set pre-request scripts to handle auth tokens

---

## Automation Script

Save as `test_api.sh` (Mac/Linux):

```bash
#!/bin/bash

BASE_URL="http://localhost:8001"

echo "🏥 Sahanak API Testing"
echo "====================="

# 1. Health Check
echo -e "\n[1] Health Check..."
curl -s $BASE_URL/health | json_pp

# 2. Signup
echo -e "\n[2] Creating User..."
USER_RESPONSE=$(curl -s -X POST $BASE_URL/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123","full_name":"Test User","age":25}')
USER_ID=$(echo $USER_RESPONSE | grep -o '"id":[0-9]*' | cut -d: -f2)
echo $USER_RESPONSE | json_pp

# 3. Login
echo -e "\n[3] Login..."
LOGIN_RESPONSE=$(curl -s -X POST $BASE_URL/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123"}')
echo $LOGIN_RESPONSE | json_pp

# 4. Assess Symptoms (YELLOW)
echo -e "\n[4] Assessing Symptoms..."
curl -s -X POST "$BASE_URL/api/assess/symptoms?user_id=$USER_ID" \
  -H "Content-Type: application/json" \
  -d '{"symptoms":["Fever","Cough"],"other_symptoms":""}' | json_pp

# 5. Get History
echo -e "\n[5] Viewing History..."
curl -s -X GET "$BASE_URL/api/assessments/$USER_ID" | json_pp

echo -e "\n✅ Testing Complete!"
```

Run:
```bash
chmod +x test_api.sh
./test_api.sh
```

---

## Debugging Tips

**Enable verbose curl:**
```bash
curl -v http://localhost:8001/health
```

**Check backend logs:**
Watch terminal where backend is running for detailed error messages.

**Database inspection:**
```bash
sqlite3 backend/sahanak.db
.tables
SELECT * FROM users;
SELECT * FROM assessments;
```

**Test locally without frontend:**
All endpoints work independently - test backend in isolation first.

---

**Last Updated:** April 2024
**API Version:** 1.0.0
**Status:** ✅ Production Ready
